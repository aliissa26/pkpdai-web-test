import pathlib
import dash_dangerously_set_inner_html
import dash_html_components as html
from dash import dcc
from spacy import displacy
from utils import rexdemo, common, nerdemo
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app


PATH = pathlib.Path(__file__).parent
COLORS = {"PK": "#d90368"}
DISPLACY_OPTIONS = {"ents": ["PK"], "colors": COLORS}



STARTING_VALUE = """BACKGROUND
Intranasal application is a comfortable, effective, nearly non-invasive, and easy route of administration in children. To date, there is, however, only one pharmacokinetic study on intranasal dexmedetomidine in pediatric populations and none in Chinese children available. Therefore, this study aimed to characterize the pharmacokinetics of intranasally administered dexmedetomidine in Chinese children
METHODS
Thirteen children aged 4 to 10 years undergoing surgery received 1 µg/kg dexmedetomidine intranasally. Arterial blood samples were drawn at various time points until 180 min after dose. Dexmedetomidine plasma concentrations were measured with high performance liquid chromatography (HPLC) and mass spectrometry. Pharmacokinetic modeling was performed by population analysis using linear compartment models with first-order absorption. 
RESULTS
An average peak plasma concentration of 748 ± 30 pg/ml was achieved after 49.6 ± 7.2 min. The pharmacokinetics of dexmedetomidine was best described by a two-compartment model with first-order absorption and an allometric scaling with estimates standardized to 70-kg body weight. The population estimates (SE) per 70 kg bodyweight of the apparent pharmacokinetic parameters were clearance CL/F = 0.32 (0.02) L/min, central volume of distribution V1/F = 34.2 (4.9) L, intercompartmental clearance Q2/F = 10.0 (2.2) L/min, and peripheral volume of distribution V2/F = 34.9 (2.3) L. The estimated absorption rate constant was Ka = 0.038 (0.004) min-1. 
CONCLUSIONS
When compared with studies in Caucasians, Chinese children showed a similar time to peak plasma concentration after intranasal administration, but the achieved plasma concentrations were about three times higher. Possible reasons are differences in age, ethnicity, and mode of administration.
"""

layout = html.Div(children=[

    html.H1("PK Named Entity Recognition"),
    html.H4("A model to locate PK parameter mentions in scientific text text",
            style=dict(marginTop=common.INTERDIV_MARGIN)),
    html.Div(nerdemo.HOWTO_CARD, className="accordion", style=dict(marginTop=common.INTERDIV_LG_MARGIN)),

    html.Div(dcc.Markdown(
        '''
Some examples to try:  

* Two hours before operation each patient received midazolam 0.5 mg kg-1 orally for premedication and 0.5 mg kg-1 
i.v. during induction. Six minutes after cessation of anaesthesia, a bolus of flumazenil 10 micrograms kg-1 was given 
i.v., followed by an infusion of flumazenil at 5 micrograms kg-1 min-1 which was maintained until the child could 
identify himself. Midazolam data were consistent with a three-compartment model with a mean (SD) elimination 
half-life of 107 (30) min, total body clearance of 15.4 (3.2) ml min-1 kg-1 and apparent volume of distribution at 
steady state of 1.9 (0.6) litre kg-1. Flumazenil data were best interpreted by a monoexponential function, 
with a mean terminal elimination half-life of 35.3 (13.8) min, a total plasma clearance of 20.6 (6.9) ml min-1 kg-1 
and apparent volume of distribution at steady state of 1.0 (0.2) litre kg-1. No unchanged midazolam was detected in 
the 24-h urine sample, but 5.8-13.8% of the flumazenil dose was recovered unchanged. 

* When predicting human in vitro CLint, average absolute fold-error was ≤2.0 by SSS with monkey, minipig and guinea 
pig (rat/mouse >3.0) and was <3.0 by most MA species combinations (including rat/mouse combinations). 4. Interspecies 
variables, including fraction metabolized by AO (Fm,AO) and hepatic extraction ratios (E) were estimated in vitro. 
 

 * For a typical 34-year-old patient receiving rFIX, clearance (CL), intercompartmental clearance (Q2, Q3), 
 distribution volume of the central compartment (V1) and peripheral compartments (V2, V3) plus interpatient 
 variability (%CV) were: CL, 284 mL h-170 kg-1 (18%); V1, 5450 mL70 kg-1 (19%); Q2, 110 mL h-170 kg-1; V2, 
 4800 mL70 kg-1; Q3, 1610 mL h-170 kg-1; V3, 2040 mL70 kg-1. '''
    ), style=dict(marginTop=common.INTERDIV_LG_MARGIN)),
    dbc.Textarea(id="ner-input",
                 value=STARTING_VALUE,
                 bs_size="lg",
                 placeholder="Enter some pharmacokinetic text here",
                 maxLength=2000,
                 debounce=False,
                 style=dict(marginTop=common.INTERDIV_LG_MARGIN, height=rexdemo.MAINAREAHEIGHT),
                 ),
    html.Div(
        [
            dbc.Button('Process', id='ner-button',
                       color="primary", size='lg',

                       ),

            dbc.Button('Clear', id='ner-clear-button',
                       color="primary", size='lg',
                       style=dict(marginLeft=common.INTERDIV_MARGIN)
                       )
        ], style=dict(marginTop=common.INTERDIV_MARGIN)
    ),
    html.Div(
        [
            dbc.Spinner(
                [

                    # html.Div(coolhtml, id='ner-output')
                    html.Div(id='ner-output', style=dict(marginTop=common.INTERDIV_MARGIN))

                ],
                color="red", fullscreen=False, debounce=2,
                show_initially=False,
                size="lg",
                spinner_style={"top": 800, "position": "fixed", "fontSize": "20px",
                               "height": 70, "width": 70}
            )
        ],
        style=dict(marginTop=common.INTERDIV_LG_MARGIN)
    )

]
)


@app.callback(
    Output("ner-output", "children"),
    [State("ner-input", "value"),
     Input("ner-button", "n_clicks")],
    prevent_initial_call=True
)
def update_output(inp_text, _):
    # out_ents = predic_ner(inp_text=inp_text)
    api_results = common.query_api(inp_text=inp_text, pred_type="ner")
    ner_results = common.request_handler(inp_request=api_results)
    if ner_results is None:
        return "Error querying the NER API - try in a few minutes", [], None, dict()
    out_ents = []
    if ner_results is not None and "entities" in ner_results.keys() and "text" in ner_results.keys():
        out_ents = ner_results["entities"]
    instance = [dict(text=ner_results["text"], ents=out_ents, title=None)]
    out_ent_div = html.Div(dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
        displacy.render(instance, style="ent", manual=True, jupyter=False, options=DISPLACY_OPTIONS))
        , style=dict(fontSize=18))

    return out_ent_div


@app.callback(
    Output("ner-input", "value"),
    [Input("ner-clear-button", "n_clicks")],
    prevent_initial_call=True
)
def update_output2(_):
    return None


@app.callback(
    Output("howto-collapse-ner", "is_open"),
    [Input("howto-ner", "n_clicks")],
    [State("howto-collapse-ner", "is_open")],
    prevent_initial_call=True
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
