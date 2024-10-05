import pathlib
import pickle
import random
import statistics
from typing import Dict, List
import dash_table
import pandas as pd
import dash
from dash.exceptions import PreventUpdate
from spacy import displacy
from dash.dependencies import Input, Output, State
import dash_dangerously_set_inner_html
import dash_html_components as html
import dash_core_components as dcc
from app import app
from utils.pkdatabase import PKEstimate
import plotly.express as px
from collections import Counter
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
from utils.docsearch import get_json

DEBUG = False

random.seed(0)
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets/pkdatabase/").resolve()

ALLRECORDS = pd.read_pickle(DATA_PATH.joinpath("maindbdf.pkl"))

with open(DATA_PATH.joinpath("estimates_classes.pkl"), "rb") as fp:
    RECORDS2IDS: Dict[int, PKEstimate] = pickle.load(fp)

if DEBUG:
    n = 1000
    ALLRECORDS = ALLRECORDS[0:n]

ALLRECORDS = pd.DataFrame(ALLRECORDS)

ALLRECORDS.rename(columns={"ID": "id"}, inplace=True)
ALLRECORDS.set_index('id', inplace=True, drop=False)

# search engine suggestions
with open(DATA_PATH.joinpath("lookup_options.pkl"), "rb") as fp:
    SUGGESTIONS_OBJECT = pickle.load(fp)

COLORS = {"PK": "#d90368", "VALUE": "#ebe8e8", "RANGE": "#fcba5d", "UNITS": "#5dfcd2", "COMPARE": "#8714fa"}
DISPLACY_OPTIONS = {"ents": ["PK", "VALUE", "RANGE", "UNITS", "COMPARE"], "colors": COLORS}
INTERDIV_LG_MARGIN = "50px"
LABELS_FONTSIZE = '18px'
SEARCH_BORDER = '40px'
MAX_SUG = 10000
INITIAL_SUGGESTIONS = SUGGESTIONS_OBJECT.all_unique_items[0:MAX_SUG]

filter_group = dbc.FormGroup(

    [
        #    dbc.Label("Filter:", size="lg"),
        dbc.Checklist(
            options=[
                {"label": "Clinical trials", "value": 1},
                {"label": "Animal studies", "value": 2}
            ],
            value=[],
            id="study-type",
            labelStyle={"fontSize": LABELS_FONTSIZE, 'display': 'inline-block'},

        )

    ],
    inline=False,
    className="mr-3",
)

search_bar = html.Div(
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
                              style=dict(borderTopLeftRadius=SEARCH_BORDER,
                                         borderBottomLeftRadius=SEARCH_BORDER,
                                         border='2px solid #303030',
                                         padding='20px',
                                         fontSize='25px', height="80px")
                              ),
                    dbc.InputGroupAddon(dbc.Button('Search', id='search-button',
                                                   color="primary", size='lg',
                                                   style=dict(padding='20px',
                                                              borderTopRightRadius=SEARCH_BORDER,
                                                              borderBottomRightRadius=SEARCH_BORDER,
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
    style=dict(marginTop=INTERDIV_LG_MARGIN)  # , 'width':'80%'}
)


def records2plot(inp_df, inp_field):
    pktypes = []
    pkfreqs = []
    for k, v in Counter(inp_df[inp_field].to_list()).items():
        pktypes.append(k)
        pkfreqs.append(v)
    out_dict = {inp_field: pktypes, "Freqs": pkfreqs}
    out_df = pd.DataFrame(out_dict)
    out_df = out_df.sort_values(by=[inp_field])
    return out_df


def get_records(drug_query: str, clinical_trial: bool = False, animal_study: bool = False):
    query_pmids = get_json(inp_query=drug_query, clinical_trial=clinical_trial,
                                           animal_study=animal_study)
    # print(query_pmids)
    if query_pmids is not None and len(query_pmids) > 0:
        df_subset = ALLRECORDS[ALLRECORDS['PMID'].isin(query_pmids)]
        df_subset.set_index('id', inplace=True, drop=False)
        if df_subset is not None:
            if len(df_subset) > 0:
                return df_subset.to_dict('records')
    df_subset = ALLRECORDS[0:0]
    df_subset.set_index('id', inplace=True, drop=False)
    return df_subset.to_dict('records')


def get_pmids(drug_query: str, clinical_trial: bool = False, animal_study: bool = False):
    query_pmids = get_json(inp_query=drug_query, clinical_trial=clinical_trial,
                                           animal_study=animal_study)
    return query_pmids


layout = html.Div(children=[

    html.H1("Dataset statistics"),
    search_bar,
    filter_group,

    html.Br(),
    html.Div(id="sentence-explore"),
    html.Br(),

    dbc.ButtonGroup(
        [
            dbc.Button("Select All", color="primary", size="sm", id="all"),
            dbc.Button("Erase", color="primary", size="sm", id="erase")
        ]
    ),
    dbc.Spinner(dash_table.DataTable(
        id="datatable-interact",
        columns=[dict(name=i, id=i, deletable=True, selectable=True, hideable=True) if i != "URL" else
                 dict(name=i, id=i, deletable=True, selectable=True, hideable=True, type="text",
                      presentation="markdown")
                 for i in ALLRECORDS.columns],
        data=ALLRECORDS.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="multi",
        row_selectable="multi",  # allow users to select 'multi' or 'single' rows
        row_deletable=True,  # choose if user can delete a row (True) or not (False)
        selected_columns=[],  # ids of columns that user selects
        selected_rows=[],  # indices of rows that user selects
        page_action="native",  # all data is passed to the table up-front or not ('none')
        page_current=0,  # page number that user is on
        page_size=10,
        export_format="csv",
        style_cell={
            'minWidth': 95, 'maxWidth': 95, 'width': 95
        },
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white'
        },

        style_filter={
            'backgroundColor': 'rgb(110, 106, 106)',
            'color': 'white'
        },

        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        }
    ), color="red", fullscreen=False, debounce=2,
        show_initially=False,
        size="md", spinner_style={"top": 700, "position": "fixed", "fontSize": "20px",
                                  "height": 70, "width": 70}),

    html.Div(id="main-stats"),
    html.Br(),
    html.Div(id="main-plot"),

]
)


@app.callback(
    Output(component_id='datatable-interact', component_property="data"),
    Input(component_id='search-button', component_property='n_clicks'),
    State(component_id='my-input', component_property='value'),
    Input("study-type", "value"),
    Input(component_id='my-input', component_property='n_submit'),
    prevent_initial_call=True
)
def update_data_table_search(_, drug_name: str, study_type: List[int], s):
    if drug_name == "" or drug_name is None or not drug_name:
        base_df = ALLRECORDS
        return base_df.to_dict('records')
    clinical_trial = False
    animal_study = False
    extra = ""
    if 1 in study_type:
        clinical_trial = True
        extra += " (clinical trials) "
    if 2 in study_type:
        animal_study = True
        extra += " (animal studies) "

    base_df = ALLRECORDS
    search_pmids = get_pmids(drug_query=drug_name, clinical_trial=clinical_trial,
                             animal_study=animal_study)
    if search_pmids is not None and len(search_pmids) > 0:
        base_df = base_df[base_df['PMID'].isin(search_pmids)]
    else:
        base_df = base_df[0:0]
    # records_to_display = get_records(drug_query=drug_name, clinical_trial=clinical_trial,
    #                                 animal_study=animal_study)
    base_df.set_index('id', inplace=True, drop=False)
    print(base_df.head())
    print(base_df.index)
    return base_df.to_dict('records')


# update other things the stats

@app.callback(
    Output(component_id='datatable-interact', component_property='selected_rows'),
    # Output(component_id='datatable-interact', component_property='derived_virtual_selected_rows'),
    [
        Input(component_id='all', component_property='n_clicks'),
        Input(component_id='erase', component_property='n_clicks')
    ],
    [
        State(component_id='datatable-interact', component_property="data"),
        State(component_id='datatable-interact', component_property="derived_virtual_data"),
        State(component_id='datatable-interact', component_property="derived_virtual_selected_rows")
    ]

)
def selection(select_n_clicks, deselect_n_clicks, original_rows, filtered_rows, selected_rows):
    ctx = dash.callback_context.triggered[0]
    ctx_caller = ctx['prop_id']
    if filtered_rows is not None:
        if ctx_caller == 'all.n_clicks':
            selected_ids = [row['id'] for row in filtered_rows]
            out = [i for i, row in enumerate(original_rows) if row['id'] in selected_ids]
            return out  # , out
        if ctx_caller == 'erase.n_clicks':
            return []  # , []
        raise PreventUpdate
    else:
        raise PreventUpdate
    pass


@app.callback(
    Output(component_id='main-stats', component_property='children'),
    Output(component_id='sentence-explore', component_property='children'),
    Output(component_id='main-plot', component_property='children'),
    [Input(component_id='datatable-interact', component_property="derived_virtual_data"),
     Input(component_id='datatable-interact', component_property='derived_virtual_selected_rows'),
     Input(component_id='datatable-interact', component_property='derived_virtual_selected_row_ids'),
     Input(component_id='datatable-interact', component_property='selected_rows'),
     Input(component_id='datatable-interact', component_property='derived_virtual_indices'),
     Input(component_id='datatable-interact', component_property='derived_virtual_row_ids'),
     Input(component_id='datatable-interact', component_property='active_cell'),
     Input(component_id='datatable-interact', component_property='selected_cells'),
     #    Input(component_id='datatable-interact', component_property='data')
     ]
)
def update_stats(all_rows_data, slctd_row_indices, slct_rows_names, slctd_rows,
                 order_of_rows_indices, order_of_rows_names, actv_cell, slctd_cell):
    #   print('***************************************************************************')
    #   #  print('Data across all pages pre or post filtering: {}'.format(all_rows_data))
    #   print('---------------------------------------------')
    #   #  print("Indices of selected rows if part of table after filtering:{}".format(slctd_row_indices))
    #   #  print("Names of selected rows if part of table after filtering: {}".format(slct_rows_names))
    #   print("Indices of selected rows regardless of filtering results: {}".format(slctd_rows))
    #   print('---------------------------------------------')
    #   #   print("Indices of all rows pre or post filtering: {}".format(order_of_rows_indices))
    #   #   print("Names of all rows pre or post filtering: {}".format(order_of_rows_names))
    #   print("---------------------------------------------")
    #   print("Complete data of active cell: {}".format(actv_cell))
    #   print("Complete data of all selected cells: {}".format(slctd_cell))

    dff = pd.DataFrame(all_rows_data)

    # Entity Graph
    ent_graph = ""
    if dff["Type"].to_list():
        etypes = records2plot(dff, inp_field="Type")
        etypes = etypes.sort_values(by=["Freqs"], ascending=False)
        etypes.head(20)
        graph_types = dcc.Graph(id='bar-chart-ent',
                                figure=px.bar(data_frame=etypes, x="Type", y="Freqs",
                                              template="plotly_dark"),
                                responsive=True,
                                )
        ent_graph = html.Div(children=[html.H4("Entity frequency:"),
                                       graph_types], style={'width': '49%', 'display': 'inline-block'})

    # Units Graph
    units_graph = ""
    if dff["Units"].to_list():
        utypes = records2plot(dff, inp_field="Units")
        utypes = utypes.sort_values(by=["Freqs"], ascending=False)
        # utypes = utypes[utypes["Freqs"] > 2]
        utypes = utypes.head(10)
        graph_units = dcc.Graph(id='bar-chart-units',
                                figure=px.bar(data_frame=utypes, x="Units", y="Freqs",
                                              template="plotly_dark"
                                              ),
                                responsive=True,
                                )
        units_graph = html.Div(children=[html.H4("Top Units:"), graph_units],
                               style={'width': '49%', 'display': 'inline-block'})

    n_abstracts = len(dff["PMID"].unique())
    out1 = html.H5(f"# Abstracts: {n_abstracts}")
    out2 = html.H5(f"# Estimates:: {len(dff)}")

    graphs_together = html.Div([ent_graph, units_graph])

    out_ent_div = []
    if actv_cell:
        est = RECORDS2IDS[actv_cell['row_id']]

        instance = [dict(text=est.sent_text, ents=est.get_character_spans(), title=None)]

        out_ent_div = [html.Div(dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
            displacy.render(instance, style="ent", manual=True, jupyter=False, options=DISPLACY_OPTIONS))
            , style=dict(fontSize=16, display='inline-block'))]

    # Get plot for the graph:

    selected_values = []
    print(slctd_row_indices)
    for v in slctd_row_indices:

        tmp_est = RECORDS2IDS[all_rows_data[v]['id']]
        estimate_text = tmp_est.central_v.text
        if check_if_float(inp_text=estimate_text):
            selected_values.append(float(estimate_text))
        else:
            if check_if_range(inp_text=estimate_text):
                new_est_text = get_mean_of_range(inp_text=estimate_text)
                selected_values.append(new_est_text)

    graph_values = None
    if len(selected_values) > 1:
        hist_data = [selected_values]
        group_labels = ['distplot']
        graph_values = dcc.Graph(id='distribution-plot',
                                 figure=ff.create_distplot(hist_data, group_labels),
                                 responsive=True
                                 )
        med = statistics.median(selected_values)
        graph_values = [graph_values, html.H4(f"Median: {med}")]

    out_stats = [html.Br(), out1, out2, graphs_together]

    return out_stats, out_ent_div, graph_values


# RECORDS2IDS[543].view_all_entities_terminal(inp_text=RECORDS2IDS[543].sent_text,ner_dictionaries=RECORDS2IDS[543].get_character_spans())

def check_if_float(inp_text):
    try:
        float(inp_text)
        return True
    except ValueError:
        return False


def get_mean_of_range(inp_text):
    if len(inp_text.split("-")) == 2:
        v0 = float(inp_text.split("-")[0].strip())
        v1 = float(inp_text.split("-")[1].strip())
    else:
        v0 = float(inp_text.split("to")[0].strip())
        v1 = float(inp_text.split("to")[1].strip())
    return (v0 + v1) / 2


def check_if_range(inp_text):
    if "-" in inp_text or "to" in inp_text:
        if len(inp_text.split("-")) == 2:
            v0 = inp_text.split("-")[0].strip()
            v1 = inp_text.split("-")[1].strip()
            if check_if_float(v0) and check_if_float(v1):
                return True
        else:
            if len(inp_text.split("to")) == 2:
                v0 = inp_text.split("to")[0].strip()
                v1 = inp_text.split("to")[1].strip()
                if check_if_float(v0) and check_if_float(v1):
                    return True
    return False
