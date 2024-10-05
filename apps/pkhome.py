import pathlib

import dash_html_components as html
import dash_bootstrap_components as dbc
from utils import common

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

CARD1 = common.make_home_card(
    card_title="Article search",
    card_text="Given one or more drugs, this app will help you find articles that reported PK parameters from "
              "clinical and animal studies",
    card_link="/pkdocsearch"
)

CARD2 = common.make_home_card(
    card_title="Relation Extraction Demo",
    card_text="We developed a model to extract PK measurements from scientific sentences including parameter "
              "mentions, central and deviation measurements, units and more. This demo shows you the model output "
              "given some input sentence",
    card_link="/pkrexdemo"
)

CARD3 = common.make_home_card(
    card_title="Named Entity Recognition Demo",
    card_text="We developed a model to identify mentions of PK parameters in scientific text. This model can be used "
              "as initial step for information extraction, subsequent entity linking or feature extraction in DDIs. "
              "This demo shows you the model output "
              "given some input sentence",
    card_link="/pknerdemo"
)

CARDS1 = dbc.CardDeck(
    [
        CARD1, CARD3

    ],
)

CARDS2 = dbc.CardDeck(
    [
        CARD2
    ],
    style=dict(margin="auto")
)

layout = html.Div([

    html.H1("PKPDAI toolkit"),
    html.H3(
        "A toolkit to efficiently deal with pharmacokinetic (PK) literature",
        style=dict(marginTop=common.INTERDIV_MARGIN)),

    html.P("In this website you will find apps and demos developed to process PK literature through Natural Language "
           "Processing approaches. Here you can find the main tools:",
           style=dict(marginTop=common.INTERDIV_LG_MARGIN, fontSize=common.FONTSIZE_PAR)#,color="#FDF0D5"),
           ),
    dbc.Row(CARDS1, style=dict(marginTop=common.INTERDIV_LG_MARGIN)),
    dbc.Row(CARDS2, style=dict(marginTop=common.INTERDIV_LG_MARGIN)),

    # dcc.Link('Home', href='/'),
    # dcc.Link('PK article search', href='/pkdocsearch'),
    # dcc.Link('PK Relation Extraction demo', href='/pkrexdemo')
],
)
