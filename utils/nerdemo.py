import dash_bootstrap_components as dbc
from dash import html, dcc

HOWTO_MARKDOWN_NER = """ 

* **What is it?**  
    This demo showcases a model developed to analyse scientific text and locate mentions of pharmacokinetic parameters. 

* **How to use it?**  
    You can try to introduce any pharmacokinetic text, click process, and visualize the model predictions. You can also select any of the examples provided. 
    
* **How was the model developed?**  
    A deep language model based on [BioBERT](https://arxiv.org/abs/1901.08746) was trained on thousands of sentences from pharmacokinetic articles labelled by pharmacometricians to perform [Named Entity Recognition](https://en.wikipedia.org/wiki/Named-entity_recognition) of PK parameters. 

* **Applications**  
    Such model can be used as a first step to extract numerical estimations of PK parameters in 
scientific publications, clinical trial reports or other textual sources. Additionally, it can be used to better 
characterise PK drug-drug interactions reported in the literature, where PK parameters of one drug might be altered 
by another compound. 

"""

HOWTO_CARD = [dbc.Card(
    [
        dbc.CardHeader(
            html.H4(
                dbc.Button(
                    "How does it work?  Click Here!",
                    color="secondary",
                    id="howto-ner",
                    n_clicks=0,
                    size="lg",
                    style={"width": "100%", "textAlign": "left"}
                )
            )
        ),
        dbc.Collapse(
            dbc.CardBody(
                dcc.Markdown(
                    HOWTO_MARKDOWN_NER
                )
            ),
            id="howto-collapse-ner",
            is_open=False
        )
    ]
)]
