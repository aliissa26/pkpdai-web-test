import pathlib
import pickle
from typing import List
import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from utils import docsearch, common
from app import app

# ================= 1. Define global variables (don't modify them on the app) ===========================

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets/pkdocsearch").resolve()

with open(DATA_PATH.joinpath("lookup_options.pkl"), "rb") as fp:
    SUGGESTIONS_OBJECT = pickle.load(fp)

INITIAL_SUGGESTIONS = SUGGESTIONS_OBJECT.all_unique_items[0:docsearch.MAX_SUG]
MAIN_DB = pd.read_parquet(path=DATA_PATH.joinpath("allPapers.parquet"))
ALL_PMIDS = MAIN_DB['pmid'].to_numpy()


# ================= 2. Main search function ===========================
def get_records(drug_query: str, clinical_trial: bool = False, sortby: str = "pk"):
    query_pmids = docsearch.get_json(inp_query=drug_query, clinical_trial=clinical_trial)
    if query_pmids is not None and len(query_pmids) > 0:
        df_subset = MAIN_DB[MAIN_DB['pmid'].isin(query_pmids)]
        if len(df_subset) > 0:
            if sortby == "date":
                df_subset = df_subset.sort_values("pubdate", ascending=False)
            relevant_records = df_subset.to_dict('records')
            return relevant_records
    return None


layout = html.Div(children=[

    html.H1("Find relevant PK literature"),
    html.Div(dcc.Markdown(
        '''
#### An app to find papers that estimated pharmacokinetic (PK) parameters *in vivo*
        '''
    ), style=dict(marginTop=common.INTERDIV_LG_MARGIN)),
    html.Div(docsearch.HOWTO_CARD, className="accordion", style=dict(marginTop=common.INTERDIV_LG_MARGIN))

    ,
    dcc.Store(id='memory'),
    html.Div([
        html.Div(
            dbc.Form(
                [

                    dbc.InputGroup(
                        [
                            html.Datalist(
                                id='list-suggested-inputs',
                                children=INITIAL_SUGGESTIONS

                            ),
                            dbc.Input(id='my-input', value="", placeholder="Search for a drug...", type='text',
                                      minLength=0, maxLength=100, autoFocus=True, autoComplete=True,
                                      list='list-suggested-inputs',
                                      debounce=False,
                                      bs_size='lg',
                                      style=dict(borderTopLeftRadius=docsearch.SEARCH_BORDER,
                                                 borderBottomLeftRadius=docsearch.SEARCH_BORDER,
                                                 border='2px solid #303030',
                                                 padding='20px',
                                                 fontSize='25px', height="80px")
                                      ),
                            dbc.InputGroupAddon(dbc.Button('Search', id='button',
                                                           color="primary", size='lg',
                                                           style=dict(padding='20px',
                                                                      borderTopRightRadius=docsearch.SEARCH_BORDER,
                                                                      borderBottomRightRadius=docsearch.SEARCH_BORDER,
                                                                      border='2px solid #303030',
                                                                      fontSize='25px'
                                                                      )
                                                           ),
                                                addon_type="append"),

                        ],
                        className="mb-3",
                        size="lg",
                        style={'width': '100%'}

                    )],

            ),
            style=dict(marginTop=common.INTERDIV_LG_MARGIN)  # , 'width':'80%'}
        ),

        html.Div(
            [

                dbc.Form(
                    [
                        dbc.FormGroup(
                            [
                                #      dbc.Label("Sort:", size="lg", style={'marginRight': '20px'}),
                                dbc.RadioItems(

                                    options=[
                                        {"label": "PK relevance", "value": "pk"},
                                        {"label": "Date", "value": "date"}
                                    ],
                                    value="pk",
                                    id="sortby",
                                    labelStyle={"fontSize": docsearch.LABELS_FONTSIZE, 'display': 'inline-block'}

                                ),

                            ],
                            className="mr-3",
                            inline=False

                        ),
                        dbc.FormGroup(

                            [
                                #    dbc.Label("Filter:", size="lg"),
                                dbc.Checklist(
                                    options=[
                                        {"label": "PopPK", "value": 1},
                                    ],
                                    value=[],
                                    id="study-type",
                                    labelStyle={"fontSize": docsearch.LABELS_FONTSIZE, 'display': 'inline-block'},

                                )

                            ],
                            inline=False,
                            className="mr-3",

                            # style={'marginLeft': '10px'}
                        ),

                    ],
                    style={'float': 'left'},
                    inline=True

                    # inline=False,
                    # style={"marginLeft": docsearch.MAIN_BORDER_MARGIN, "marginRight": docsearch.MAIN_BORDER_MARGIN}
                ),
                dbc.Form(
                    [
                        dbc.Button('Download results', id='download-button',
                                   className='mr-1', color='secondary', size='lg',
                                   style={'borderRadius': '8px'}

                                   ),
                        dcc.Download(id="download-search")
                    ],
                    style={'float': 'right'},
                )

            ],
            style=dict(marginTop=docsearch.MARGIN_TOP_FILTERS, marginRight=docsearch.EXTRA_MARG,
                       marginLeft=docsearch.EXTRA_MARG)
        ),

    ],
        style=dict(marginTop=common.INTERDIV_LG_MARGIN, marginRight=docsearch.EXTRA_MARG,
                   marginLeft=docsearch.EXTRA_MARG)
    )
    ,
    html.Div([

        # html.P('Click when changing parameters',
        #        style={'color': 'red', 'fontSize': '12px', 'margin': '2px'}),

        # dbc.Row(
        html.Div(dbc.Spinner(html.Div(id='my-output'), color="red", fullscreen=False, debounce=2,
                             show_initially=False,
                             size="md", spinner_style={"top": 700, "position": "fixed", "fontSize": "20px",
                                                       "height": 70, "width": 70}))


    ],
        style=dict(marginTop=docsearch.MARGIN_RESULTS_TOP, verticalAlign="top")
    ),

],
)


# ================= 4. Define callbacks ===========================

@app.callback(
    Output(component_id='my-output', component_property='children'),
    Output(component_id='memory', component_property='data'),
    Input(component_id='button', component_property='n_clicks'),
    State(component_id='my-input', component_property='value'),
    Input(component_id="sortby", component_property="value"),
    Input("study-type", "value"),
    Input(component_id='my-input', component_property='n_submit'),
    prevent_initial_call=True
)
def update_output_div(_, drug_name: str, sorting: str, study_type: List[int], s):
    if drug_name == "":
        return html.Div(), None

    pop_pk = False
    extra = ""
    if 1 in study_type:
        pop_pk = True
        extra += " (population PK) "

    records_to_display = get_records(drug_query=drug_name, clinical_trial=pop_pk,
                                     sortby=sorting)

    if records_to_display is not None:
        n = len(records_to_display)
        out = []
        for i, tmp_record in enumerate(records_to_display):
            try:
                out.append(docsearch.make_card(inp_record=tmp_record, x=i))
            except ValueError as e:
                print(f"Error constructing card {tmp_record}")
                print(e)

        # if switch:
        #    extra = "(only clinical trials)"
        header_div_1 = html.Div([html.P(f"""{n} results for "{drug_name}" {extra}""")],
                                style={'margin': 10})

        if out:
            out_div = html.Div([header_div_1, docsearch.render_cards(inp_list_cards=out)], style={"marginTop": "20px"})
        else:
            header_div_1 = html.H5(f"No relevant PK papers found for {drug_name}, please check spelling...",
                                   style={"marginTop": f"20px"})
            out_div = html.Div([header_div_1], style={"marginTop": "20px"})
    else:
        header_div_1 = html.H5(f"No relevant PK papers found for {drug_name}, please check spelling",
                               style={"marginTop": f"20px"})
        out_div = html.Div([header_div_1], style={"marginTop": "20px"})

    return out_div, records_to_display


@app.callback(
    Output('download-search', 'data'),
    Input('download-button', 'n_clicks'),
    State('memory', 'data'),
    prevent_initial_call=True
)
def fun(_, inp_records):
    out_df = pd.DataFrame({})
    if inp_records is not None:
        try:
            out_df = pd.DataFrame(inp_records)
        except:
            pass
    return dcc.send_data_frame(out_df.to_csv, "pkpdai_results.csv")


@app.callback(
    Output("howto-collapse", "is_open"),
    [Input("howto", "n_clicks")],
    [State("howto-collapse", "is_open")],
    prevent_initial_call=True
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("list-suggested-inputs", "children"),
    [Input("my-input", "value")],
    prevent_initial_call=True
)
def update_options(inp_val):
    if len(inp_val) > 0:
        return SUGGESTIONS_OBJECT.search(inp_val.lower())[0:docsearch.MAX_SUG]
    return INITIAL_SUGGESTIONS
