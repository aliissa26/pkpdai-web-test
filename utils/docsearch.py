from typing import Iterable, List, Dict
import numpy as np
import re
import urllib.request
import json
import dash_bootstrap_components as dbc
from dash import html, dcc
from tqdm import tqdm

MAX_SUG = 10
BAR_HEIGHT = "65px"
BAR_FONT = 20
SEARCH_BORDER = '40px'
MAIN_BORDER_MARGIN = 30
LABELS_FONTSIZE = '18px'
MAIN_DIV_STYLE = dict(margin=MAIN_BORDER_MARGIN, verticalAlign="top")
META_TAGS = [{'name': 'viewport',
              'content': 'width=device-width,'
                         ' initial-scale=1.0,'
                         ' maximum-scale=1.5,'
                         ' minimum-scale=0.5,'
              }]

MAIN_SEARCH_STYLE = {
    'borderTopLeftRadius': SEARCH_BORDER,
    'borderBottomLeftRadius': SEARCH_BORDER,
    'borderTopRightRadius': SEARCH_BORDER,
    'borderBottomRightRadius': SEARCH_BORDER,
    'text-align-last': 'center',
    "height": BAR_HEIGHT,
    "font-size": "20px"
}
EXTRA_MARG = "0px"
MARGIN_TOP_FILTERS = "30px"

MARGIN_RESULTS_TOP = '120px'



HOWTO_MARKDOWN = """The search is pretty simple; **enter the name of a drug** and we will search for a collection of 
papers that reported *in vivo* PK parameters for that drug  

* **Do you want more than one drug?**  
    If searching for more than one drug, please use boolean operators: e.g.
    *"rifampicin AND isoniazid"*, *"rifampicin OR isoniazid"* 

* **What does PK relevance mean?**  
    In the background, we ran a machine-learning algorithm to identify scientific 
    publications that are likely to have estimated PK parameters. "_How likely_" refers 
    to the posterior probability of the algorithm and is the percentage displayed as _PK relevance_ 

* **Do you want to find out more about the algorithm or our group?**  

    Check out [the publication](https://wellcomeopenresearch.org/articles/6-88/v1) describing the algorithm  behind 
    this search engine  
    You can also [view the project on GitHub](https://github.com/PKPDAI/PKDocClassifier)   
    For more information on PKPDAI go to [our website](https://pkpdai.com) """

HOWTO_CARD = [dbc.Card(
    [
        dbc.CardHeader(
            html.H4(
                dbc.Button(
                    "How does it work?  Click Here!",
                    color="secondary",
                    id="howto",
                    n_clicks=0,
                    size="lg",
                    style={"width": "100%", "textAlign": "left"}
                    # style={"backgroundColor":"transparent"}
                )
            )
        ),
        dbc.Collapse(
            dbc.CardBody(
                dcc.Markdown(
                    HOWTO_MARKDOWN
                )
            ),
            id="howto-collapse",
            is_open=False
        )
    ]
)]


def make_pubmed_query(inp_url: str):
    try:
        with urllib.request.urlopen(inp_url) as url:
            data = json.loads(url.read().decode())['esearchresult']['idlist']
        return data
    except ValueError as e:
        print(e)
        return False


def read_pmid_papers(inp_path: str):
    pkpmids = np.loadtxt(inp_path, dtype="int")
    return pkpmids


def get_json(inp_query: str, clinical_trial: bool):
    inp_query = re.sub(' +', ' ', inp_query)
    inp_query = inp_query.strip().replace(" ", "+").lower()
    start_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=pharmacokinetics+AND+" \
                f"({inp_query})"
    end_url = "&usehistory=y&retmax=50000&retmode=json"
    intermediate_stuff = ""
    if clinical_trial:
        intermediate_stuff += """+AND+(monolix+OR+nonmem+OR+nlmixr+OR+("population+pharmacokinetic*"))"""

    search_query = start_url + intermediate_stuff + end_url

    result = make_pubmed_query(search_query)
    if result:
        result = np.asarray(result, dtype="int")
        return result
    return None


def get_article_links(inp_pmids: Iterable) -> List[str]:
    return [f"https://pubmed.ncbi.nlm.nih.gov/{x}" for x in inp_pmids]


def make_card(inp_record: Dict, x: int):
    card_body_list = construct_card_body(inp_record=inp_record)
    card = dbc.Card(
        [
            dbc.CardHeader(f"{inp_record['pubdate']}"),
            dbc.CardBody(
                card_body_list
            )
        ],
        # color="secondary", inverse=True
        # color='secondary', inverse=True, style={'border-radius': '12px'}
        className="bg-primary",
        style={'border-radius': '8px'}
    )
    return card


def construct_card_body(inp_record):
    link = f"https://pubmed.ncbi.nlm.nih.gov/{inp_record['pmid']}"
    authors = ",".join(inp_record['author'].split(";"))
    main_content = [
        html.H5(inp_record['title'], className="card-title"),
        html.P(
            [html.Small(authors),
             ], className="card-text"
        ),
        html.P(
            [html.Small(f"\n PK relevance: {round(inp_record['prob'] * 100)} %")],
            className="card-text"
        ),
        dbc.Button(
            "Article Link",
            href=link,
            target="_blank",

            style={'border-radius': '8px'}
            #  color="primary"
            # , className="mt-auto"
        )
    ]
    if inp_record['pmc'] != '' and inp_record['pmc'] is not None:
        main_content.append(
            dbc.Button(
                "See full text",
                f"href=https://www.ncbi.nlm.nih.gov/labs/pmc/articles/{inp_record['pmc']}",
                style={'backgroundColor': '#FF8C00', 'color': 'white', 'border-radius': '8px'}
            )
        )
    return main_content


def render_cards(inp_list_cards: List[dbc.Card]):
    all_rows = []
    n = 3
    for cardgroup in group_elements(inp_list=inp_list_cards, subgroup_size=n):
        tmp_row = []
        for card in cardgroup:
            tmp_row.append(card)
        assert len(tmp_row) <= n
        all_rows.append(dbc.CardDeck(tmp_row, style={"margin-bottom": '25px'}))

    return html.Div(all_rows)


def group_elements(inp_list: List, subgroup_size: int):
    """
    Gets a flat list and groups its elements in subgroups of size subgroup_size
    The last element will have remaining size
    """
    return (inp_list[pos:pos + subgroup_size] for pos in range(0, len(inp_list), subgroup_size))


class TreeSearch(object):
    def __init__(self, n_starting_options: int = 10):
        self.main_dict = {}
        self.starting_options = []
        self.max_start_options = n_starting_options
        self.all_unique_items = []

    def add_words(self, inp_word_list: List[str]):
        for word in tqdm(inp_word_list):
            tmp_dict = dict(label=word, value=word)
            if tmp_dict not in self.all_unique_items:
                self.all_unique_items.append(tmp_dict)
            if len(self.starting_options) < self.max_start_options and tmp_dict not in self.starting_options:
                self.starting_options.append(tmp_dict)
            part_word = ""
            for character in word:
                part_word += character
                if part_word not in self.main_dict.keys():
                    self.main_dict[part_word] = [tmp_dict]
                else:
                    if tmp_dict not in self.main_dict[part_word]:
                        self.main_dict[part_word] += [tmp_dict]

    def search(self, inp_prefix: str):
        if inp_prefix in self.main_dict.keys():
            return self.main_dict[inp_prefix]
        return []


class TreeSearchDataList(object):
    def __init__(self, n_starting_options: int = 10):
        self.main_dict = {}
        self.starting_options = []
        self.max_start_options = n_starting_options
        self.all_unique_items = []

    def add_words(self, inp_word_list: List[str]):
        for word in tqdm(inp_word_list):
            tmp_opt = html.Option(value=word)
            if not self.html_option_isin(inp_option=tmp_opt, inp_opt_list=self.all_unique_items):
                self.all_unique_items.append(tmp_opt)
            #  if len(self.starting_options) < self.max_start_options and tmp_dict not in self.starting_options:
            #      self.starting_options.append(tmp_dict)
            part_word = ""
            for character in word:
                part_word += character
                if part_word not in self.main_dict.keys():
                    self.main_dict[part_word] = [tmp_opt]
                else:
                    if not self.html_option_isin(inp_option=tmp_opt, inp_opt_list=self.main_dict[part_word]):
                        self.main_dict[part_word] += [tmp_opt]

    def search(self, inp_prefix: str):
        if inp_prefix in self.main_dict.keys():
            return self.main_dict[inp_prefix]
        return []

    @staticmethod
    def html_option_isin(inp_option: html.Option, inp_opt_list: List[html.Option]):
        all_vals = [x.value for x in inp_opt_list]
        if inp_option.value in all_vals:
            return True
        return False
