import pathlib
import pandas as pd
from dash import dcc
import dash_html_components as html
from utils import rexdemo, common
from spark_display.relation_extraction import RelationExtractionVisualizer
from app import app
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_dangerously_set_inner_html

PATH = pathlib.Path(__file__).parent

EXAMPLE_OTHERS = """The pharmacokinetics of oral midazolam (Dormicum, 15 mg) and loprazolam (Dormonoct, 1 mg) were 
studied in eight healthy young volunteers in a cross-over design. Plasma concentrations of midazolam were measured 
with a gas chromatographic method and loprazolam concentrations were determined by a radio-receptor technique. 
Absorption of midazolam proceeded very rapidly (median tmax = 0.4 h) and a rapid onset of sedative action was 
observed. Loprazolam absorption was relatively slow (median tmax = 3 h) and its absorption profile was often 
irregular. Most subjects fell asleep before peak concentrations were reached. Median peak concentrations were 94 ng 
ml-1 and 3.1 ng ml-1 for midazolam and loprozolam, respectively. The median elimination half-life of midazolam was 
1.8 h and that of loprazolam 15 h. It is possible that the elimination half-life of loprazolam as determined by 
radioreceptor assay is determined by active metabolites rather than by loprazolam itself. Midazolam elimination 
half-life was the same when determined by radioreceptor assay or by GLC. There was no significant correlation between 
the half-lives of the two drugs. """
EXAMPLE_OTHERS2 = """Maximum concentrations after IV administration (median, 1,394 ng/mL [range, 1,150 to 1,
503 ng/mL]) and IM administration (411 ng/mL [217 to 675 ng/mL]) were measured at 3 minutes and at 5 to 30 minutes, 
respectively. Distribution half-life was 18.7 minutes (13 to 47 minutes) after IV administration and 41 minutes (30 
to 80 minutes) after IM administration. Elimination half-life was 98 minutes (67 to 373 minutes) and 234 minutes (103 
to 320 minutes) after IV and IM administration, respectively. Total clearance after IV administration was 11.3 
mL/min/kg (6.7 to 13.9 mL/min/kg), and steady-state volume of distribution was 525 mL/kg (446 to 798 mL/kg). 
Bioavailability of midazolam after IM administration was 92%. Peak onset of sedation occurred at 0.4 minutes (IV) and 
15 minutes (IM). Sedation was significantly greater after IV administration. """

MORE_EXAMPLES = """Rifampin significantly (P < 0.0001) increased the systemic and oral clearance of midazolam from 0.44 ± 0.2 L h/kg and 1.56 ± 0.8 L h/kg to 0.96 ± 0.3 L h/kg and 34.4 ± 21.2 L h/kg,
respectively."""

layout = html.Div(children=[
    dcc.Store(id='memory-rex'),
    html.H1("PK Relation Extraction"),
    html.H4("An app to visualize PK relations extracted in scientific sentences",
            style=dict(marginTop=common.INTERDIV_MARGIN)),
    html.Div(rexdemo.HOWTO_CARD_REX, className="accordion", style=dict(marginTop=common.INTERDIV_LG_MARGIN)),
    html.Div(dcc.Markdown(
        '''
Some examples to try:   

* Bendamustine plasma concentration peaked near the end of infusion and was rapidly eliminated with a mean elimination half-life (t(1/2)) of 0.67-0.8 h. 

* The half-life of baricitinib in patients less than 40 kg was substantially shorter than in adult populations, requiring the need for dosing up to 4 times daily. On therapeutic doses, the mean area-under-the-concentration-vs.-time curve was 2,388 nM*hr, which is 1.83-fold higher than mean baricitinib exposures in adult patients with rheumatoid arthritis receiving doses of 4 mg once-daily.
 
* The Cmax, Vd, and AUC0-inf were 12.12 +- 3.2 mg/L, 44.20 +- 1 L and 34.18 +- 8 mg.h/L, respectively

 * A two-compartment PK-model best described the data. Volume of distribution of paracetamol increased exponentially 
 with body weight. Clearance was not influenced by any covariate. Simulations of the standardized dosing regimens 
 resulted in a Css of 9.2 mg l-1 and 7.2 mg l-1 , for every 6 h and every 8 h respectively. Variability in 
 paracetamol PK resulted in Css above 5.4 and 4.1 mg l-1 , respectively, in 90% of the population and above 15.5 and 
 11.7 mg l-1, respectively, in 10% at these dosing regimens. '''
    ), style=dict(marginTop=common.INTERDIV_LG_MARGIN)),
    dbc.Textarea(id="rex-input", bs_size="lg",
                 value="Ten nonobese subjects (mean age 30.6 ± 7.12 y; body mass index 21.56 ± 1.95 kg/m2 ) and 20 "
                       "obese subjects (mean age 34.47 ± 7.03 y; body mass index 33.17 ± 2.38 kg/m2 ) participated in "
                       "the study and were given p.o. amoxicillin.  Both maximum concentration (Cmax ; 12.12 ± 4.06 "
                       "vs. 9.66 ± 2.93 mg/L) and area under the curve (AUC)0-inf (34.18 ± 12.94 mg.h/L vs. 26.88 ± "
                       "9.24 mg.h/L) were slightly higher in nonobese than in obese subjects, respectively, "
                       "but differences were not significant. The volume of distribution (V/F) parameter was "
                       "statistically significantly higher in obese compared to nonobese patients (44.20 ± 17.85 L "
                       "vs. 27.57 ± 12.96 L).",
                 placeholder="Enter some pharmacokinetic text here",
                 maxLength=3000,
                 debounce=False,
                 style=dict(marginTop=common.INTERDIV_LG_MARGIN, height=rexdemo.MAINAREAHEIGHT),
                 ),
    html.Div(
        [
            dbc.Button('Process', id='rex-button',
                       color="primary", size='lg',

                       ),
            dbc.Button('Clear', id='rex-clear-button',
                       color="primary", size='lg',
                       style=dict(marginLeft=common.INTERDIV_MARGIN)
                       )
        ],
        style=dict(marginTop=common.INTERDIV_MARGIN)
    ),

    html.Div(
        [

            dbc.Spinner(
                [html.Div(id='rex-output'),
                 html.Div(id="tabular-output"),
                 dbc.Form(
                     [
                         dbc.Button('Download table', id='download-button-rex',
                                    className='mr-1', color='secondary', size='lg',
                                    style={'borderRadius': '8px',
                                           'display': 'none'},

                                    ),
                         dcc.Download(id="download-rex-search")
                     ],
                     style={'float': 'left'},
                 )

                 ],
                color="red", fullscreen=False, debounce=2,
                show_initially=False,
                size="lg",
                spinner_style={"top": 700, "position": "fixed", "fontSize": "20px",
                               "height": 70, "width": 70}
            ),

        ]
        ,
        style=dict(marginTop=common.INTERDIV_LG_MARGIN))

],
)


@app.callback(
    Output("rex-output", "children"),
    Output("tabular-output", "children"),
    Output(component_id='memory-rex', component_property='data'),
    Output(component_id='download-button-rex', component_property='style'),
    [State("rex-input", "value"),
     Input("rex-button", "n_clicks")],
    prevent_initial_call=True
)
def update_output(inp_text, _):
    out_tab_style = {'display': 'none'}

    api_results = common.query_api(inp_text=inp_text, pred_type="rex")
    rex_results = common.request_handler(inp_request=api_results)
    if rex_results is None:
        return "Error querying the REX API - try in a few minutes", [], None, dict()
    pkre, prodigy_output, extra_ents, sofs = rex_results['spark_format'], rex_results['main'], \
                                             rex_results['extra_ents'], rex_results['sentence_offsets']
    pkre = rexdemo.pkre2sparknlp(pkre=prodigy_output)
    c_val_dicts = rexdemo.get_c_val_dicts(prodigy_output)
    out_records = None
    if c_val_dicts:
        extra_ents = rexdemo.remove_bad_chemicals(inp_chemicals=extra_ents, inp_cvals=c_val_dicts)
        c_val_dicts = rexdemo.add_drugs(inp_c_val_dicts=c_val_dicts, inp_extra_dicts=extra_ents,
                                        sentences_offsets=sofs)
        c_val_dicts_mentions = rexdemo.transform2mentions(inp_text=prodigy_output["text"], inp_c_val_dicts=c_val_dicts)
        tabular_output = rexdemo.cvalmentions2table(inp_cvals=c_val_dicts_mentions)

        out_records = tabular_output.to_records(index=False)
        out_tab_style['display'] = 'block'
        out_tabular_div = dbc.Table.from_dataframe(tabular_output, striped=True, bordered=True, hover=True,
                                                   )
    else:
        out_tabular_div = ""
    visualizer = RelationExtractionVisualizer()
    html_content = visualizer.display(pkre, relation_col='relations', return_html=True,
                                      exclude_relations=["NO_RELATION"], max_x=1700)

    # clean_rels = [x for x in prodigy_output['relations'] if x['label'] != 'NO_RELATION']
    # cvals = [x['child_span'] for x in clean_rels if x['label'] == 'C_VAL' and x['child_span']['label'] == "VALUE"]

    # dwg = svgwrite.Drawing("temp.svg", profile='full', size=(x_limit, start_y + y_offset))

    html_content = '<div>' + html_content + '</div>'
    out_img = html.Div(dash_dangerously_set_inner_html.DangerouslySetInnerHTML(html_content), style=dict(margin="auto"))

    return out_img, out_tabular_div, out_records, out_tab_style


@app.callback(
    Output('download-rex-search', 'data'),
    Input('download-button-rex', 'n_clicks'),
    State('memory-rex', 'data'),
    prevent_initial_call=True
)
def fun(_, inp_records):
    out_df = pd.DataFrame({})
    if inp_records is not None:
        try:
            out_df = pd.DataFrame.from_records(inp_records)
            out_df.columns = ["Parameter", "Drug", "Measurement", "Units", "Deviation", "DevUnits", "Compare"]
        except:
            pass
    return dcc.send_data_frame(out_df.to_csv, "pkpdai_results.csv")


@app.callback(
    Output("rex-input", "value"),
    [Input("rex-clear-button", "n_clicks")],
    prevent_initial_call=True
)
def update_output2(_):
    return None


@app.callback(
    Output("howto-collapse-rex", "is_open"),
    [Input("howto-rex", "n_clicks")],
    [State("howto-collapse-rex", "is_open")],
    prevent_initial_call=True
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
