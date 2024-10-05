from typing import List

import dash_html_components as html
from dash import dcc
from utils import common
import dash_bootstrap_components as dbc


def make_team_card(inp_name: str, inp_descr: str, inp_email: str):
    card_body_list = [
        #   html.H5(inp_name, className="card-title"),
        html.P(
            inp_descr,
            className="card-text"
        ),

    ]
    if inp_email and inp_name != "":
        card_body_list.append(html.P(inp_email))
    card = dbc.Card(
        [dbc.CardHeader(html.H4(inp_name)),
         dbc.CardBody(
             card_body_list
         )
         ],
        # color="secondary", inverse=True
        color='primary',  # inverse=True,
        className="primary",
        style={'border-radius': '8px'}
    )
    return card


def group_team_elements(inp_list: List, subgroup_size: int):
    """
    Gets a flat list and groups its elements in subgroups of size subgroup_size
    The last element will have remaining size
    """
    return (inp_list[pos:pos + subgroup_size] for pos in range(0, len(inp_list), subgroup_size))


def render_team_cards(inp_list_cards: List[dbc.Card]):
    all_rows = []
    n = 3
    for cardgroup in group_team_elements(inp_list=inp_list_cards, subgroup_size=n):
        tmp_row = []
        for card in cardgroup:
            tmp_row.append(card)
        assert len(tmp_row) <= n
        all_rows.append(dbc.CardDeck(tmp_row, style={"margin-bottom": '25px'}))

    return html.Div(all_rows)


author1 = dict(name="Joe Standing", description="Pharmacometrician and clinical pharmacist with academic, industry "
                                                "and regulatory experience. Main research focus is on antimicrobial "
                                                "and general paediatric drug development.",
               email=dcc.Markdown("""<j.standing@ucl.ac.uk>"""))

author2 = dict(name="Frank Kloprogge", description="Pharmacological modeller with academic experience. Main research "
                                                   "focus is on infectious diseases including tuberculosis using both"
                                                   " in-vitro and in-vivo data.",
               email=dcc.Markdown("""<f.kloprogge@ucl.ac.uk>"""))

author3 = dict(name="Waty Lilaonitkul", description="Computational dynamic systems modeller with academic and "
                                                    "industrial experience. Main research focus on ML methodology for"
                                                    " high-dimensional health data.",
               email=dcc.Markdown("""<watjana.lilaonitkul.16@ucl.ac.uk>"""))

author4 = dict(name="Ferran Gonzalez Hernandez", description=dcc.Markdown(
    "PhD student at UCL and the [Alan Turing Institute]("
    "https://www.turing.ac.uk/people/ferran-gonzalez"
    "-hernandez) "
    "working on biomedical natural language processing ("
    "NLP). Main research focus is the extraction of PKPD "
    "information using NLP and machine learning approaches."),
               email=dcc.Markdown("""<ferran.hernandez.17@ucl.ac.uk>"""))

author5 = dict(name="Victoria Smith", description="PhD Student at UCL, interested in Natural Language Processing in "
                                                  "Healthcare. Current research focus is PKPD information extraction "
                                                  "from tables in biomedical literature using ML and NLP approaches.",
               email=dcc.Markdown("""<v.smith.20@ucl.ac.uk>"""))

author6 = dict(name="Simon Carter", description="Pre-clinical and in vitro mechanistic modeller with academic and "
                                                "extensive industry experience. Main research focus is PKPD modelling "
                                                "and future applications of machine learning based predictions.",
               email=dcc.Markdown("""<simon.carter@farmaci.uu.se>"""))

extra1 = dict(name="James Yates", description="Modelling and Simulation scientist with extensive experience in drug "
                                              "discovery and development. Main research focus is on the development "
                                              "of mechanistic models of anti-cancer drug pharmacology.",
              email=dcc.Markdown("""<james.yates@astrazeneca.com>"""))

extra2 = dict(name="Juha Iso-Sipilä", description="NLP researcher at BenevolentAI focusing on literature based "
                                                  "scientific discovery. Main research focus is on the Named Entity "
                                                  "Recognition and Entity Linking from biomedical literature.",
              email="")

extra3 = dict(name="Paul Goldsmith", description="Experienced Clinical Pharmacologist/Pharmacokineticist with over 20 "
                                                 "years’ experience in large pharmaceutical and biotech companies "
                                                 "leading new initiatives in clinical study design and PK analysis. "
                                                 "Research fellow in Clinical Pharmacology at Eli Lilly",
              email=dcc.Markdown("""<goldsmith_paul1@lilly.com>"""))

extra4 = dict(name="Ahmed Almousa", description="Clinical pharmacokineticist and pediatric oncology pharmacist, "
                                                "with experience in personalized medicine and drug discovery. Main "
                                                "research focus on pharmacogenomics and personalized medicine in "
                                                "paediatrics using big data",
              email="")

extra5 = dict(name="José Antonio Cordero Rigol", description="Pre-clinical and Clinical pharmacokineticist with "
                                                             "extensive experience in industry and academic "
                                                             "involvement in Blanquerna School of Health Sciences, "
                                                             "Ramon Llull University. Main research focus is on "
                                                             "Pharmacoepidemiology using big data.",
              email="")

extra6 = dict(name="Maria Rosa Ballester", description="Clinical pharmacokineticist with over 20 years’ experience in "
                                                       "clinical trials and PK analysis. PhD in PK/PD population "
                                                       "modelling with academic experience in Blanquerna School of "
                                                       "Health Sciences, Ramon Llull University. Main research focus "
                                                       "is on Clinical Pharmacology at IIB Sant Pau- CERCA Center in "
                                                       "Catalonia, Spain.",
              email="")

extra7 = dict(name="Mario Duran Hortolà", description="PhD. Pharmacist and chemist with over 30 years’ experience of "
                                                      "academic experience in pharmacology and quality in higher "
                                                      "education in Blanquerna School of Health Sciences, Ramon Llull "
                                                      "University. Main research focus is on pharmacology and "
                                                      "physiotherapy interactions.",
              email="")

extra8 = dict(name="Albert Solé Guixeres", description="Undergraduate student at the end-of-degree project at Ramon "
                                                       "Llull University working on Pharmacokinetics and "
                                                       "Pharmacodynamics.",
              email="")

extra9 = dict(name="Palang Chotsiri", description="Pharmacometric modeller with academic experience. Main research "
                                                  "focus is on the PKPD of anti-infective agents on vulnerable "
                                                  "population.",
              email="")

extra10 = dict(name="Thanaporn Wattanakul", description="Pharmacometric modeller and pharmacist with academic "
                                                        "experience. Main research focus is on tropical diseases "
                                                        "including malaria and tuberculosis.",
               email="")

extra11 = dict(name="Gill Mundin", description="Experienced Clinical Pharmacokineticist with over 20 years’ industry "
                                               "experience in designing and analysing clinical PK trials. Main "
                                               "research focus on controlled release formulations and combination "
                                               "therapies. More recent pre-clinical modelling and simulation "
                                               "experience in oncology drug discovery and development.",
               email="")

MAIN_TEAM = [author1, author2, author3, author4, author5, author6]

EXTRA_TEAM = [extra1, extra2, extra3, extra4, extra5, extra6, extra7, extra8, extra9, extra10, extra11]

MAIN_TEAM_CARDS = [make_team_card(inp_name=x['name'], inp_descr=x['description'], inp_email=x['email']) for x in
                   MAIN_TEAM]

EXTRA_TEAM_CARDS = [make_team_card(inp_name=x['name'], inp_descr=x['description'], inp_email=x['email']) for x in
                    EXTRA_TEAM]

MAIN_TEAM_DIV = html.Div([render_team_cards(inp_list_cards=MAIN_TEAM_CARDS)], style={"marginTop": "20px"})

EXTRA_TEAM_DIV = html.Div([render_team_cards(inp_list_cards=EXTRA_TEAM_CARDS)], style={"marginTop": "20px"})

layout = html.Div([
    html.Div(
        [

            # dcc.Markdown(
            #    """
            #    The content presented in this website is part of the PKPDAI project, launched at University College London
            #    """,
            #    style=dict(marginTop=common.INTERDIV_MARGIN, fontSize=common.FONTSIZE_PAR)  # ,color="#FDF0D5"),
            # ),

            html.H1(
                "Team",
                style=dict(marginTop=common.INTERDIV_LG_MARGIN)),

            MAIN_TEAM_DIV,

            html.H1(
                "Contributors and Collaborators",
                style=dict(marginTop=common.INTERDIV_LG_MARGIN, marginBottom=common.INTERDIV_LG_MARGIN)),

            EXTRA_TEAM_DIV,
        ]
    ),

],
)
