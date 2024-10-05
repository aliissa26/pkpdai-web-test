import dash_bootstrap_components as dbc
import dash_html_components as html
from dash import dcc
import requests

META_TAGS = [{'name': 'viewport',
              'content': 'width=device-width, initial-scale=0.8, maximum-scale=1.2, minimum-scale=0.3,'}]

# MARGINS
MAIN_MARGIN_TOP = 10  # "10px"
MAIN_BORDER_MARGIN = 30  # "30px"
INTERDIV_MARGIN = 20  # "20px"
INTERDIV_LG_MARGIN = 50  # "50px"
# FONTSIZES
FONT_SIZE_NAVBAR = 20  # remember to change navbar-brand font-size
FONTSIZE_PAR = 18
# DIV STYLING
MAIN_DIV_STYLE = dict(margin=MAIN_BORDER_MARGIN, verticalAlign="top", marginTop=MAIN_MARGIN_TOP)


def query_api(inp_text: str, pred_type: str):

    api_url = "https://pkpdai.azurewebsites.net/"
    out = None
    if pred_type in ["ner", "rex"]:
        if pred_type == "ner":
            query_url = api_url + f"pred_ner"
        else:
            query_url = api_url + f"pred_rex"
        params = dict(text=inp_text)
        try:
            out = requests.post(query_url, json=params, timeout=30)
        except:
            return None
    return out


def request_handler(inp_request):
    if inp_request is not None and inp_request.status_code in [200, 201]:
        results = inp_request.json()
        return results
    else:
        return None


def make_home_card(card_title, card_text, card_link):
    card = dbc.Card(
        [
            #     dbc.CardImg(src=image_source, top=True),
            dcc.Link(dbc.CardHeader(card_title, style=dict(fontSize=22), className="card-header"),
                     href=card_link, style=dict(color="white", textDecoration="none")),
            dbc.CardBody(
                [
                    html.P(
                        card_text,
                        className="card-text",
                        style=dict(fontSize=FONTSIZE_PAR)

                    ),
                    dbc.Button("Try it!", href=card_link, size='lg', color="secondary"),
                ],

            ),
        ],

        color="dark",  # inverse=True

    )

    return card
