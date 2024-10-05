import os
from typing import Dict, List
from sparknlp.annotation import Annotation
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc

os.environ["TOKENIZERS_PARALLELISM"] = "false"
ACCEPTABLE_ENTITY_COMBINATIONS = [
    ("PK", "VALUE"), ("PK", "RANGE"), ("VALUE", "PK"), ("RANGE", "PK"),  # C_VAL relations
    ("VALUE", "VALUE"), ("RANGE", "RANGE"), ("RANGE", "VALUE"), ("VALUE", "RANGE"),  # D_VAL relations

    # RELATED relations
    ("UNITS", "VALUE"), ("UNITS", "RANGE"), ("VALUE", "UNITS"), ("RANGE", "UNITS"),
    ("COMPARE", "VALUE"), ("COMPARE", "RANGE"), ("VALUE", "COMPARE"), ("RANGE", "COMPARE")

]
MAINAREAHEIGHT = "150px"

REX2ID = dict(NO_RELATION=0, C_VAL=1, D_VAL=2, RELATED=3)
ID2REX = {v: k for k, v in REX2ID.items()}
TO_PRESERVE = ['input_ids', 'token_type_ids', 'attention_mask', 'overflow_to_sample_mapping', 'labels']


def pkre2sparknlp(pkre: Dict):
    text = pkre['text']
    result = {
        'document': [Annotation('document', 0, len(text) - 1, text, (), None)],
        'relations': []
    }

    # converting
    res = pkre['relations']  # relations (list)
    for re in res:
        meta = {
            'entity2': re['head_span']['label'],
            'entity2_begin': re['head_span']['start'],
            'entity2_end': re['head_span']['end'],
            'chunk2': text[re['head_span']['start']:re['head_span']['end']],

            'entity1': re['child_span']['label'],
            'entity1_begin': re['child_span']['start'],
            'entity1_end': re['child_span']['end'],
            'chunk1': text[re['child_span']['start']:re['child_span']['end']]
        }

        result['relations'].append(Annotation(annotator_type=None,
                                              begin=None,
                                              end=None,
                                              result=re['label'],
                                              metadata=meta,
                                              embeddings=None))
    return result


def simplify_annotation(inp_annotation: Dict, keep_tokens: bool = False) -> Dict:
    """"
    Removes non-useful information from inside entities and relations keys coming out of the prodigy annotations.
    Annotated data is the same so this funcion just removes irrelevant dictionary keys
    All entities/spans become:
    {
        "start": <character_start>,
        "end": <character_end>,
        "label": <label>
    }
    All relations become:
    {
        "head_span": <dictionary of head entity>,
        "child_span": <dictionary of child entity>,
        "label": <relation label>
    }

    """

    if keep_tokens:
        new_spans = [{"start": span["start"],
                      "end": span["end"],
                      "token_start": span["token_start"],
                      "token_end": span["token_end"],
                      "label": span["label"]
                      }
                     for span in inp_annotation["spans"]]

        new_relations = [{
            "head": relation["head"],
            "child": relation["child"],
            "head_span": {"start": relation["head_span"]["start"],
                          "end": relation["head_span"]["end"],
                          "token_start": relation["head_span"]["token_start"],
                          "token_end": relation["head_span"]["token_end"],
                          "label": relation["head_span"]["label"]
                          },
            "child_span": {"start": relation["child_span"]["start"],
                           "end": relation["child_span"]["end"],
                           "token_start": relation["child_span"]["token_start"],
                           "token_end": relation["child_span"]["token_end"],
                           "label": relation["child_span"]["label"]
                           },
            "label": relation["label"]
        }
            for relation in inp_annotation["relations"]]
    else:
        new_spans = [{"start": span["start"], "end": span["end"], "label": span["label"]} for span in
                     inp_annotation["spans"]]
        new_relations = [{
            "head_span": {"start": relation["head_span"]["start"],
                          "end": relation["head_span"]["end"],
                          "label": relation["head_span"]["label"]},
            "child_span": {"start": relation["child_span"]["start"],
                           "end": relation["child_span"]["end"],
                           "label": relation["child_span"]["label"]},
            "label": relation["label"]
        }
            for relation in inp_annotation["relations"]]

    inp_annotation["relations"] = new_relations
    inp_annotation["spans"] = new_spans
    return inp_annotation


def get_predicted_cval_entities(inp_annotation: Dict) -> List[Dict]:
    """
    Gets all the VALUE entities that are labelled with a C_VAL relation
    """
    out_c_vals = []
    for relation in inp_annotation["relations"]:
        if relation["label"] == "C_VAL":
            for relspantype in ["head_span", "child_span"]:
                if relation[relspantype]['label'] in ["VALUE", "RANGE"]:
                    out_c_vals.append(relation[relspantype])
    return out_c_vals


def get_c_val_dicts(annotation: Dict) -> List[Dict]:
    """
    Gets as an input an annotated sentence in prodigy format and it returns a list of central values with all
    the related information in the form of:

    dict(
        parameter=None,
        central_v={
            "value/range": s_text[c_val["start"]:c_val["end"]],
            "units": None,
            "type_meas": None,
            "compare": None
        },
        deviation={
            "value/range": None,
            "units": None,
            "type_meas": None,
            "compare": None
        },
        sentence=annotation["text"],
        source=annotation["meta"]["url"],
                            )

    """
    annotation = simplify_annotation(annotation)
    complementary_fields = ["TYPE_MEAS", "COMPARE", "UNITS"]
    # 1. Get central values

    c_val_entities = get_predicted_cval_entities(annotation)
    output_cvals = []

    if c_val_entities:
        for c_val in c_val_entities:

            new_cval = dict(
                parameter=None,
                central_v={
                    "value/range": c_val,
                    "units": None,
                    "type_meas": None,
                    "compare": None
                },
                deviation={
                    "value/range": None,
                    "units": None,
                    "type_meas": None,
                    "compare": None
                },
                sentence=annotation["text"],
            )
            relations = annotation["relations"]
            for relation in relations:
                relation_ents = [relation["child_span"], relation["head_span"]]
                rel_type = relation["label"]
                if c_val in relation_ents:
                    nocval_ent = [x for x in relation_ents if x != c_val][0]
                    if rel_type == "C_VAL":
                        if nocval_ent['label'] == "PK":
                            new_cval['parameter'] = nocval_ent
                        else:
                            print("CAREFUL! HEAD OF C_VAL DOESN'T SEEM TO BE PK")
                    elif rel_type == "RELATED":
                        for f in complementary_fields:
                            if nocval_ent['label'] == f:
                                new_cval["central_v"][f.lower()] = nocval_ent
                    elif rel_type == "D_VAL":
                        d_val = nocval_ent
                        new_cval["deviation"]["value/range"] = d_val
                        # search for complementary information on dval
                        for subrel in relations:
                            subrel_ents = [subrel["child_span"], subrel["head_span"]]
                            if d_val in subrel_ents and subrel['label'] == "RELATED":
                                nodvalent = [x for x in subrel_ents if x != d_val][0]
                                for f in complementary_fields:
                                    if nodvalent['label'] == f:
                                        new_cval["deviation"][f.lower()] = nodvalent

            output_cvals.append(new_cval)
    return output_cvals


def get_extra_offsets(inp_spacy_doc):
    out_ents = []
    for ent in inp_spacy_doc.ents:
        new_dict = dict(start=ent.start_char, end=ent.end_char, label=ent.label_)
        out_ents.append(new_dict)
    return out_ents


def get_extra_offsets_stanza(inp_stanza_doc):
    out_ents = []
    for ent in inp_stanza_doc.ents:
        new_dict = dict(start=ent.start_char, end=ent.end_char, label=ent.type)
        out_ents.append(new_dict)
    return out_ents


def inwhich_sentence(sent_offs, inp_ent):
    for i, tmp_offsets in enumerate(sent_offs):
        if tmp_offsets[0] <= inp_ent['start'] and inp_ent['end'] <= tmp_offsets[1]:
            return i


def find_closest(central_entity, candidate_neighbours):
    mindist = 10000000
    main_candidate = candidate_neighbours[0]
    for cand in candidate_neighbours:
        distleft = cand['end'] - central_entity['start']
        distright = central_entity['end'] - cand['start']
        distance_candidate = min(abs(distleft), abs(distright))
        if distance_candidate < mindist:
            mindist = distance_candidate
            main_candidate = cand
    return main_candidate


def add_drugs(inp_c_val_dicts, inp_extra_dicts, sentences_offsets):
    out_dicts = []
    drug_dicts = [x for x in inp_extra_dicts if x['label'] == 'CHEMICAL']

    if inp_c_val_dicts:
        for x in inp_c_val_dicts:
            x['chemical'] = None
        if drug_dicts:
            if len(drug_dicts) == 1:
                for cvd in inp_c_val_dicts:
                    cvd['chemical'] = drug_dicts[0]
                    out_dicts.append(cvd)
                return out_dicts
            else:
                for cvd in inp_c_val_dicts:
                    cv = cvd['central_v']['value/range']
                    cv_sent_id = inwhich_sentence(sent_offs=sentences_offsets, inp_ent=cv)
                    drugs_in_same_sentence = [d for d in drug_dicts if inwhich_sentence(sent_offs=sentences_offsets,
                                                                                        inp_ent=d) == cv_sent_id]
                    if drugs_in_same_sentence:
                        match_drug = find_closest(central_entity=cv, candidate_neighbours=drugs_in_same_sentence)
                    else:
                        match_drug = find_closest(central_entity=cv, candidate_neighbours=drug_dicts)

                    cvd['chemical'] = match_drug
                    out_dicts.append(cvd)
        else:
            out_dicts = inp_c_val_dicts
    return out_dicts


def get_text_if_exists(inp_dict, inp_text):
    if isinstance(inp_dict, dict):
        return inp_text[inp_dict['start']:inp_dict['end']]
    else:
        return inp_dict


def transform2mentions(inp_text, inp_c_val_dicts):
    out_dicts = []
    for tmpd in inp_c_val_dicts:
        for f in ['parameter', 'chemical']:
            tmpd[f] = get_text_if_exists(inp_dict=tmpd[f], inp_text=inp_text)
        for v in ['central_v', 'deviation']:
            for y in ['value/range', 'units', 'type_meas', 'compare']:
                tmpd[v][y] = get_text_if_exists(inp_dict=tmpd[v][y], inp_text=inp_text)
        out_dicts.append(tmpd)
    return out_dicts


def cvalmentions2table(inp_cvals):
    allentries = []
    for entry in inp_cvals:
        allentries.append(dict(Parameter=entry["parameter"],
                               Chemical=entry['chemical'],
                               Value=entry["central_v"]["value/range"],
                               Units=entry["central_v"]["units"],
                               Deviation=entry["deviation"]["value/range"],
                               DevUnits=entry["deviation"]["units"],
                               Compare=entry["central_v"]["compare"],
                               )
                          )

    return pd.DataFrame(allentries)


def remove_bad_chemicals(inp_chemicals, inp_cvals):
    if inp_cvals:
        c_val_limits = [(x['central_v']['value/range']['start'], x['central_v']['value/range']['end'])
                        for x in inp_cvals]
        inp_chemicals = [ch for ch in inp_chemicals if (ch['start'], ch['end']) not in c_val_limits]

    return inp_chemicals


HOWTO_MARKDOWN_REX = """ 

* **What is it?**  
    This demo showcases a model developed to analyse scientific text and extract estimates of 
pharmacokinetic parameters reported in the literature. 

* **How to use it?**  
    You can try to introduce any pharmacokinetic text, click process, and visualize the model 
predictions. You can also select any of the examples provided. 

* **How was the model developed?**  
    A deep language model based on [SpERT](https://arxiv.org/abs/1909.07755) was 
trained on thousands of sentences from pharmacokinetic articles labelled by pharmacometricians to perform Named 
Entity Recognition and Relation Extraction of pharmacokinetic entities. The model was trained on articles performing 
PK studies *in vivo*. 

* **Applications**  
    The model can be used to extract numerical estimations of PK parameters in 
scientific publications, clinical trial reports or other textual sources to automatically generate databases of PK 
parameters

"""

HOWTO_CARD_REX = [dbc.Card(
    [
        dbc.CardHeader(
            html.H4(
                dbc.Button(
                    "How does it work?  Click Here!",
                    color="secondary",
                    id="howto-rex",
                    n_clicks=0,
                    size="lg",
                    style={"width": "100%", "textAlign": "left"}
                )
            )
        ),
        dbc.Collapse(
            dbc.CardBody(
                dcc.Markdown(
                    HOWTO_MARKDOWN_REX
                )
            ),
            id="howto-collapse-rex",
            is_open=False
        )
    ]
)]
