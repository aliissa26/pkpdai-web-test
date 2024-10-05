from collections import Counter
from typing import List, Dict, Union, Tuple
from termcolor import colored
import re

from tqdm import tqdm

TO_REMOVE = []  # ['[', '(', ']', ')']
DOT_SYNS = ['x', '*', '×', '•', ' ', '⋅']
UNIT_SYNONYMS = {
    '·': DOT_SYNS,
    'μg': ['micrograms', 'micro g', 'microg', 'microgram', 'µg', 'mug'],
    'h': ['hr', 'hrs', 'hour', 'hours'],
    '%': ['percent', 'percentage'],
    'μl': ['microliters', 'microliter', 'micro l', 'microl', 'µl'],
    'l': ['liters', 'litre', 'liter', 'litres'],
    'dl': ['deciliter', 'dliter'],
    'min': ['minutes', 'minute', 'mins'],
    'd': ['days', 'day'],
    'month': ['months'],
    'kg': ['kilogram', 'kilograms'],
    's': ['sec'],
    'ms': ['milisec', 'miliseconds', 'msec'],
    'nM': ['nmol', 'nanomol'],
    'mM': ['mmol', 'milimol'],
    'μM': ['mumol', 'micromol', 'micromols', 'mumol', 'μmol', 'µmol', 'µM'],
    'pM': ['pmol', 'pmols', 'picomol']

}

MAGNITUDES = {
    'TIME': ['ms', 's', 'min', 'h', 'd', 'month'],
    'MASS': ['ng', 'μg', 'mg', 'g', 'kg', 'pg'],
    'VOLUME': ['nl', 'μl', 'ml', 'l', 'dl'],
    'CONCENTRATION': ['pM', 'nM', 'μM', 'mM', 'M'],
    'PERCENTAGE': ['%'],
}

RANGE_SEPARATORS = [', and ,', '- x (-)', 'to over', '·–·', ',–,', 'and', '–‐', '−,', '%-', 'to', '-', '‐', '−', ';',
                    ',', '–']


def num_meas(inp_paper: List[Dict]) -> int:
    total_cvals = 0
    for s in inp_paper:
        for r in s['relations']:
            if r['label'] == "C_VAL":
                total_cvals += 1
    return total_cvals


def num_meas_per_sent(inp_paper: List[Dict]) -> float:
    across_sents = []
    for s in inp_paper:
        total_cvals_in_sent = 0
        for r in s['relations']:
            if r['label'] == "C_VAL":
                total_cvals_in_sent += 1
        if total_cvals_in_sent != 0:
            across_sents.append(total_cvals_in_sent)
    return sum(across_sents) / len(across_sents)


def has_cvals(inp_s):
    for r in inp_s['relations']:
        if r['label'] == "C_VAL":
            return True
    return False


def extract_sents_with_meas(inp_paper: List[Dict]) -> List[Dict]:
    return [s for s in inp_paper if has_cvals(s)]


class Span(object):
    def __init__(self, inp_dict: Dict, inp_text: str):
        self.start = inp_dict['start']
        self.end = inp_dict['end']
        self.base_text = inp_text
        self.text = self.base_text[self.start:self.end]
        self.label = inp_dict['label']
        self.is_param = False
        if self.label == "PK":
            self.is_param = True


class PKSpan(Span):
    def __init__(self, inp_dict: Dict, inp_text: str):
        super().__init__(inp_dict=inp_dict, inp_text=inp_text)
        self.id = inp_dict['kb_id']
        self.id_name = inp_dict['kb_name']


def subs_underscore_dot(inp_mention: str, standard_dot: str = '·') -> str:
    """
    Substitutes '.' by '·' if '.' is not surrounded by numbers
    """
    match_dot = r"(?<!\d)\.(?!\d)|\.(?!\d)|(?<!\d)\."
    inp_mention = re.sub(match_dot, standard_dot, inp_mention)
    return inp_mention


def sub_all_mult(inp_mention: str, standard_dot: str = '·') -> str:
    for subelement in DOT_SYNS:
        if subelement in inp_mention:
            inp_mention = inp_mention.replace(subelement, standard_dot)
    inp_mention = re.sub(r'·+', standard_dot, inp_mention)
    return inp_mention


def check_syns(inp_term: str, replacement_dict: Dict) -> str:
    for main_form, synonyms in replacement_dict.items():
        if inp_term in synonyms:
            return main_form
        synonyms_changed = [x + "-1" for x in synonyms]
        main_form_changed = main_form + "-1"
        if inp_term in synonyms_changed:
            return main_form_changed
    return inp_term


def unit_std_dict(inp_mention: str, standard_dot: str = '·', standard_div: str = '/') -> str:
    subunits_one = inp_mention.split(standard_dot)
    std_subunits_one = []
    subunits_one = ["/" if x == "per" else x for x in subunits_one]
    for subu in subunits_one:
        if standard_div in subu:
            subunits_two = subu.split(standard_div)
            std_subunits_two = [check_syns(inp_term=t, replacement_dict=UNIT_SYNONYMS) for t in subunits_two]
            std_subunits_one.append(f"{standard_div}".join(std_subunits_two))
        else:
            std_subunits_one.append(check_syns(inp_term=subu, replacement_dict=UNIT_SYNONYMS))

    assert len(subunits_one) == len(std_subunits_one)
    return f"{standard_dot}".join(std_subunits_one)


def standardise_unit(inp_mention: str) -> str:
    inp_mention = inp_mention.strip()
    inp_mention = "".join([x.lower() if x != 'M' else x for x in inp_mention])
    inp_mention = inp_mention.replace("per cent", "%")
    inp_mention = inp_mention.replace(" per ", "/")
    inp_mention = inp_mention.replace("per ", "/")
    inp_mention = inp_mention.replace("of", "")
    inp_mention = inp_mention.replace("proteins", "")
    inp_mention = inp_mention.replace("protein", "")
    inp_mention = inp_mention.strip()
    if '.' in inp_mention:
        inp_mention = subs_underscore_dot(inp_mention=inp_mention)
    for x in TO_REMOVE:
        inp_mention = inp_mention.replace(x, '')
    inp_mention = sub_all_mult(inp_mention=inp_mention)
    inp_mention = unit_std_dict(inp_mention=inp_mention)

    inp_mention = inp_mention.replace("micro·", "μ")
    inp_mention = inp_mention.replace("micro", "μ")
    return inp_mention


def check_for_divide(inp_mention: str) -> str:
    if len(inp_mention.split("/")) > 1:
        # Checks for the first "/" and if more than one, conversts subsequent "/" to "·"
        splt_on_divide = inp_mention.split("/", 1)
        replaced_second_divide = [x.replace("/", "·") for x in splt_on_divide]
        replaced_second_divide = ["(" + item + ")(-1)" for item in replaced_second_divide[1:]]
        replaced_second_divide.insert(0, splt_on_divide[0])
        new_inp_mention = "·".join(replaced_second_divide)
        return new_inp_mention.strip("·")

    return inp_mention


def check_weight_bracket_dot_split(inp_mention: str) -> List:
    weight_split = re.split(r"70·kg\(-1\)|70·kg-1|70·\(kg\)-1", inp_mention)
    if len(weight_split) > 1:
        weight_split = [minus for minus in weight_split if (minus != "" and minus is not None)]
        weight_split = "".join(weight_split)
        dot_split = re.split(r"·(?=[^\)]*(?:\(|$))", weight_split)
        dot_split.extend(["70·kg(-1)"])
        dot_split = [dot for dot in dot_split if (dot != "" and dot is not None)]
    else:
        dot_split = re.split(r"·(?=[^\)]*(?:\(|$))", inp_mention)
        dot_split = [dot for dot in dot_split if (dot != "" and dot is not None)]
    return dot_split


def check_weight_dot_split(inp_mention: str) -> List:
    if len(re.findall("70·kg\(-1\)|70·kg-1|70·\(kg\)-1", inp_mention)) >= 1:
        weight_split = re.split("70·kg\(-1\)|70·kg-1|70·\(kg\)-1", inp_mention)
        weight_split = [minus for minus in weight_split if (minus != "" and minus is not None)]
        weight_split = "".join(weight_split)
        dot_split = re.split(r"·", weight_split)
        dot_split.extend(["70·kg(-1)"])
        dot_split = [dot for dot in dot_split if (dot != "" and dot is not None)]
    else:
        dot_split = re.split(r"·", inp_mention)
        dot_split = [dot for dot in dot_split if (dot != "" and dot is not None)]

    return dot_split


def check_for_brackets(inp_mention: str) -> List:
    big_parenthesis_regex = r"\((.*?)\)-\d+|\((.*?)\)−\d+|\((.*?)\)\(-\d+\)|\((.*?)\)\(−\d+\)"
    small_parenthesis_regex = r"\((-\d+)\)|\((−\d+)\)|(-\d+)|(−\d+)"
    if len(re.findall(big_parenthesis_regex, inp_mention)) >= 1:
        # split on dots outside of brackets only
        dot_split = check_weight_bracket_dot_split(inp_mention)
        brackets_split = [re.split(r"\((.*?)\)", dot) and re.split(r"(-\d)|(−\d)", dot) for dot in dot_split]
        brackets_split = [[bracket for bracket in i if bracket is not None] for i in brackets_split]
        brackets_split = [[num_bracket.strip("(){}[]") for num_bracket in i] for i in brackets_split]
        brackets_split = [[bracket for bracket in i if bracket != ""] for i in brackets_split]
        final_split = [[strip_bracket.replace("−", "-") for strip_bracket in i] for i in brackets_split]
    elif len(re.findall(small_parenthesis_regex, inp_mention)) >= 1:
        dot_split = check_weight_dot_split(inp_mention)
        minus_one_split = [re.split(small_parenthesis_regex, dot2) for dot2 in dot_split]
        minus_one_split = [[num_minus.strip("(){}[]") for num_minus in i if num_minus] for i in minus_one_split]
        minus_one_split = [[minus for minus in i if (minus != "" and minus is not None)] for i in minus_one_split]
        final_split = [[strip_minus.replace("−", "-") for strip_minus in i] for i in minus_one_split]
    else:
        final_split = [[inp_mention]]
    if not all([0 < len(sublist) <= 2 for sublist in final_split]):
        a = 1
    return final_split


def standardise_divide(inp_mention: str) -> Tuple:
    """
    Converts all units into dict of numerator and denominator (removes all "/" and "-1")
    N.B. second slash equivalent to multiplication
    """
    # 1. check for /, and if more than one convert subsequent to ·
    inp_mention = check_for_divide(inp_mention)

    # 2. Check for brackets and splits on the dot returning numerator and denominator candidates
    units_split = check_for_brackets(inp_mention)
    # ml*kg-1*h*min-1 -> [[ml], [kg, -1], [h], [min, -1]]
    # ml/h -> [[ml],[h, -1]
    # 3. Add all those without -digits to nominator list
    num_list = [sublist for sublist in units_split if len(sublist) == 1]
    minus_list = [sub for sub in units_split if sub not in num_list]
    minus_list = [x for x in minus_list if x]
    # sort out if any minus digits that are not 1s
    denom_list = []
    for sublist in minus_list:
        if sublist[1] != "-1":
            power = sublist[1].replace("-", "^")
            subject = "(" + sublist[0] + ")"
            new_sublist = "".join([subject, power])
            denom_list.append([new_sublist])
        else:
            new_subject = sublist[0]
            denom_list.append([new_subject])

    # get final denominator and nominator lists
    num_list = [item for sublist in num_list for item in sublist]
    denom_list = [item for sublist in denom_list for item in sublist]

    # join elements with mutliplication sign
    numerator = "·".join(num_list)
    denominator = "·".join(denom_list)
    # print(numerator, "/", denominator)

    return numerator, denominator


def unit2magnitude(inp_unit: str) -> Union[str, None]:
    for magnitude, magn_units in MAGNITUDES.items():
        if inp_unit in magn_units:
            return magnitude
    return None


def clean_trailing(inp_mention):
    if inp_mention == "":
        return None
    if inp_mention[0] == "·":
        inp_mention = inp_mention[1:]
    if inp_mention == "":
        return None
    if inp_mention[-1] == "·":
        inp_mention = inp_mention[:-1]
    if inp_mention == "":
        inp_mention = None
    return inp_mention


def units2magnitudes(inp_xnumertor: str) -> Tuple[str, bool]:
    all_converted = True
    all_units = inp_xnumertor.split("·")
    out_magnitudes = []
    for tmp_unit in all_units:
        magnitude = unit2magnitude(inp_unit=tmp_unit)
        if magnitude is None:
            all_converted = False
            out_magnitudes.append(tmp_unit)
        else:
            out_magnitudes.append(magnitude)
    out_magnitudes = sorted(out_magnitudes)
    return "·".join(out_magnitudes), all_converted


def clean_denom(inp_denom):
    if inp_denom == "1":
        return None
    return inp_denom


def convert_final_std(inp_num, inp_denom) -> Tuple[str, str, bool]:
    inp_num = clean_trailing(inp_num)
    inp_denom = clean_denom(clean_trailing(inp_denom))
    if inp_num and inp_denom:
        inp_num_sorted = "·".join(sorted(inp_num.split("·")))
        inp_denom_sorted = "·".join(sorted(inp_denom.split("·")))
        inp_num_mag, all_as_mag_n = units2magnitudes(inp_xnumertor=inp_num_sorted)
        inp_denom_mag, all_as_mag_d = units2magnitudes(inp_xnumertor=inp_denom_sorted)
        st_unit_mention = f"[{inp_num_sorted}] / [{inp_denom_sorted}]"
        st_unit_magnitudes = f"{inp_num_mag} / {inp_denom_mag}"
        all_as_mag = False
        if all_as_mag_n and all_as_mag_d:
            all_as_mag = True
        return st_unit_mention, st_unit_magnitudes, all_as_mag
    else:
        if inp_num:
            inp_num_sorted = "·".join(sorted(inp_num.split("·")))
            inp_num_mag, all_as_mag = units2magnitudes(inp_xnumertor=inp_num_sorted)
            st_unit_mention = f"{inp_num_sorted}"
            st_unit_magnitudes = f"{inp_num_mag}"
            return st_unit_mention, st_unit_magnitudes, all_as_mag
        else:
            if inp_denom:
                inp_denom_sorted = "·".join(sorted(inp_denom.split("·")))
                inp_denom_mag, all_as_mag = units2magnitudes(inp_xnumertor=inp_denom_sorted)
                st_unit_mention = f"1/[{inp_denom_sorted}]"
                st_unit_magnitudes = f"1/{inp_denom_mag}"
                return st_unit_mention, st_unit_magnitudes, all_as_mag
            return "", "", False


class PKEstimate(object):
    def __init__(self, param: PKSpan, central_v: Span, central_v_units: Union[Span, None],
                 deviation_v: Union[Span, None], deviation_v_units: Union[Span, None],
                 compare: Union[Span, None]):
        self.param = param
        self.central_v = central_v
        self.central_v_units = central_v_units
        self.central_v_units_std = self.std_units(inp_u=self.central_v_units)
        self.deviation_v = deviation_v
        self.deviation_v_units = deviation_v_units
        self.deviation_v_units_std = self.std_units(inp_u=self.deviation_v_units)
        self.compare = compare
        self.sent_text = param.base_text

    @staticmethod
    def get_text_or_none(inp_e):
        if inp_e is not None:
            return inp_e.text
        return ""

    @staticmethod
    def std_units(inp_u):
        if inp_u is not None:
            u_std = standardise_unit(inp_u.text)
            num, denom = standardise_divide(u_std)
            std_unit_mention, std_unit_magnitudes, _ = convert_final_std(inp_num=num,
                                                                         inp_denom=denom)
            return std_unit_mention

        return ""

    def get_dict_output(self):
        return dict(
            Parameter=self.get_text_or_none(self.param),
            ParamID=f"{self.param.id_name}-{self.param.id}",
            Value=self.get_text_or_none(self.central_v),
            Units=self.get_text_or_none(self.central_v_units),
            Units_std=self.std_units(self.central_v_units),
            Deviation=self.get_text_or_none(self.deviation_v),
            DevUnits=self.get_text_or_none(self.deviation_v_units),
            DevUnits_std=self.std_units(self.deviation_v_units),
            Compare=self.get_text_or_none(self.compare)
        )

    def get_ents(self):
        out_ents = []
        for x in [self.param, self.central_v, self.central_v_units, self.deviation_v, self.deviation_v_units,
                  self.compare]:
            if x is not None:
                e = dict(start=x.start, end=x.end, label=x.label)
                if e not in out_ents:
                    out_ents.append(e)
        return out_ents

    def print_estimate(self):
        character_annots = self.get_character_spans()
        t = self.view_all_entities_terminal(inp_text=self.sent_text, ner_dictionaries=character_annots)
        eid = f"{self.param.id}({self.param.id_name})"
        print(eid)
        print(t)

    def get_character_spans(self):
        ents = []
        for x in [self.param, self.central_v, self.central_v_units, self.deviation_v, self.deviation_v_units,
                  self.compare]:
            if x is not None and x not in ents:
                ents.append(dict(start=x.start, end=x.end, label=x.label))
        return ents

    @staticmethod
    def view_all_entities_terminal(inp_text, ner_dictionaries):
        color_map = {"PK": "red", "VALUE": "blue", "UNITS": "green", "RANGE": "cyan", "COMPARE": "magenta"}
        # filter uniques
        uq_ner_dictionaries = []
        for t in ner_dictionaries:
            if t not in uq_ner_dictionaries:
                uq_ner_dictionaries.append(t)
        if uq_ner_dictionaries:
            uq_ner_dictionaries = sorted(uq_ner_dictionaries, key=lambda anno: anno['start'])
            sentence_text = ""
            end_previous = 0
            for annotation in uq_ner_dictionaries:
                c = color_map[annotation['label']]
                sentence_text += inp_text[end_previous:annotation["start"]]
                sentence_text += colored(inp_text[annotation["start"]:annotation["end"]],
                                         c, attrs=['reverse', 'bold'])
                end_previous = annotation["end"]
            sentence_text += inp_text[end_previous:]
            return sentence_text
        else:
            return inp_text


def make_span(inp_dict: Union[Dict, None], original_text: str):
    if inp_dict is not None:
        return Span(inp_dict=inp_dict, inp_text=original_text)
    return None


def get_measurements(inp_sent: Dict) -> Union[List[PKEstimate], None]:
    measurements = []
    sent_text = inp_sent['text']
    sent_relations = inp_sent['relations']
    for r in sent_relations:
        if r['label'] == 'C_VAL':
            # HERE, EXTRACT EVERYTHING FROM INSIDE
            # 1) extract parameters and central_v if existing
            param = None
            c_v = None
            for side in ['left', 'right']:
                ent = r[side]
                if ent['label'] == 'PK':
                    param = ent  # PKSpan(inp_dict=ent, inp_text=sent_text)
                else:
                    if ent['label'] in ['VALUE', 'RANGE']:
                        c_v = ent  # Span(inp_dict=ent, inp_text=sent_text)
            if param is not None and c_v is not None:
                c_v_units = None
                d_v = None
                d_v_units = None
                compare = None
                # 2) Find Units and Compare
                for sub_r in sent_relations:
                    if sub_r['label'] == 'RELATED' and (sub_r['right'] == c_v or sub_r['left'] == c_v):
                        for side in ['left', 'right']:
                            if sub_r[side] != c_v:
                                if sub_r[side]['label'] == "COMPARE":
                                    compare = sub_r[side]
                                if sub_r[side]['label'] == "UNITS":
                                    c_v_units = sub_r[side]
                # 3) Find Dev
                for sub_r in sent_relations:
                    if sub_r['label'] == 'D_VAL' and (sub_r['right'] == c_v or sub_r['left'] == c_v):
                        for side in ['left', 'right']:
                            if sub_r[side] != c_v:
                                if sub_r[side]['label'] in ['VALUE', 'RANGE']:
                                    d_v = sub_r[side]

                # 4) Find Dev units
                if d_v:
                    for sub_r in sent_relations:
                        if sub_r['label'] == 'RELATED' and (sub_r['right'] == d_v or sub_r['left'] == d_v):
                            for side in ['left', 'right']:
                                if sub_r[side] != d_v:
                                    if sub_r[side]['label'] == "UNITS":
                                        d_v_units = sub_r[side]

                # Estimation object

                param = PKSpan(inp_dict=param, inp_text=sent_text)
                c_v = Span(inp_dict=c_v, inp_text=sent_text)
                c_v_units = make_span(inp_dict=c_v_units, original_text=sent_text)
                d_v = make_span(inp_dict=d_v, original_text=sent_text)
                d_v_units = make_span(inp_dict=d_v_units, original_text=sent_text)
                compare = make_span(inp_dict=compare, original_text=sent_text)

                estimate = PKEstimate(param=param, central_v=c_v, central_v_units=c_v_units,
                                      deviation_v=d_v, deviation_v_units=d_v_units, compare=compare)

                measurements.append(estimate)

            else:
                pass
                # raise ValueError("There was a central measurement without one of its elements being "
                #                 "parameter or value/range")

    if measurements:
        return measurements
    return None


# Classes: (1) measurement (2) sentence (3) paper

class PKSentence(object):
    def __init__(self, inp_sent: Dict):
        self.estimates: Union[List[PKEstimate], None] = get_measurements(inp_sent=inp_sent)
        self.text: str = inp_sent['text']
        self.has_params = False
        self.pmid = inp_sent['pmid']
        self.is_title = inp_sent['is_title']
        if self.estimates is not None:
            assert len(self.estimates) > 0
            self.has_params = True

    def print_estimates(self):
        if self.estimates is not None:
            for e in self.estimates:
                e.print_estimate()

    def get_dict_estimates(self):
        out_estimates = []
        if self.estimates is not None:
            for e in self.estimates:
                out_dict = e.get_dict_output()
                if out_dict not in out_estimates:
                    out_estimates.append(out_dict)
        return out_estimates

    def get_entities(self):
        uq_ents = []
        for estimate in self.estimates:
            ents = estimate.get_ents()
            for e in ents:
                if e not in uq_ents:
                    uq_ents.append(e)
        uq_ents = sorted(uq_ents, key=lambda x: x['start'])
        return uq_ents


class PKAbstract(object):
    def __init__(self, inp_sents: List[PKSentence]):
        self.title = ""
        self.sentences = inp_sents
        self.n_sentences = len(inp_sents)
        self.parameter_ids = [f"{e.param.id_name}({e.param.id})" for s in inp_sents if s.estimates for e in s.estimates]
        uq_pmids = list(set([s.pmid for s in inp_sents]))
        assert len(uq_pmids) == 1
        self.pmid = uq_pmids[0]
        for s in self.sentences:
            if s.is_title:
                self.title += s.text + " "


class PKAbstractsDB(object):
    def __init__(self, inp_abstracts: List[PKAbstract]):
        self.abstracts = inp_abstracts

    def ent_stats(self):
        cc = Counter([eid for a in self.abstracts for eid in a.parameter_ids]).most_common()
        total_meas = sum([c for eid, c in cc])
        for eid, c in cc:
            print(f"{eid} - {round(c * 100 / total_meas, 2)}% (n={c})")

    @staticmethod
    def format_est(inp_dict, pmid, sentence_text, title, est_id):
        return {
            "PMID": pmid,
            "Parameter": inp_dict["Parameter"],
            "Type": inp_dict["ParamID"],
            "Value": inp_dict["Value"],
            "Units": inp_dict["Units_std"],
            "Compare": inp_dict["Compare"],
            "Sentece": sentence_text,
            "Title": title,
            "URL": f"[Article Link](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)",
            "ID": est_id
        }

    def estimates_to_records(self):
        estimates_records = []
        out_dict = dict()
        est_id = 0
        for abstract in tqdm(self.abstracts):
            for s in abstract.sentences:
                if s.estimates is not None:
                    tmp_estimates = s.get_dict_estimates()
                    for tmp_e, original_est in zip(tmp_estimates, s.estimates):
                        estimates_records.append(self.format_est(inp_dict=tmp_e,
                                                                 pmid=abstract.pmid,
                                                                 sentence_text=s.text,
                                                                 title=abstract.title,
                                                                 est_id=est_id)
                                                 )
                        out_dict[est_id] = original_est
                        est_id += 1
        return estimates_records, out_dict
