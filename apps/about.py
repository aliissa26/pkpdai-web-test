import dash_html_components as html
from dash import dcc

from utils import common

layout = html.Div([
    html.Div(
        [
            html.H2(
                "Contact",
                style=dict(marginTop=common.INTERDIV_MARGIN)),
            dcc.Markdown(
                """
                If you would like to collaborate, use the models or have any suggestions get in touch at <info@pkpdai.com>
                
                For technical details regarding NLP approaches behind the demos, search engine or website code you can email <ferran.hernandez.17@ucl.ac.uk>
                
                """,
                style=dict(marginTop=common.INTERDIV_LG_MARGIN, fontSize=common.FONTSIZE_PAR)  # ,color="#FDF0D5"),
            ),

        ]
    ),
    html.Div(
        [
            html.H2(
                "Code",
                style=dict(marginTop=common.INTERDIV_MARGIN)),

            dcc.Markdown(
                """
                  We will be realasing the code and data behind the models at <https://github.com/PKPDAI>
                """,
                style=dict(marginTop=common.INTERDIV_LG_MARGIN, fontSize=common.FONTSIZE_PAR)  # ,color="#FDF0D5"),
            ),


        ]
    )

],
)
