from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app, server
from apps import pkdocsearch, pkrexdemo, pkhome, pknerdemo, about, team, pkdatabase
from utils import common

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/", active="exact",
                                style=dict(fontSize=common.FONT_SIZE_NAVBAR))),
        dbc.NavItem(dbc.NavLink("Paper Search", href="/pkdocsearch", active="exact",
                                style=dict(fontSize=common.FONT_SIZE_NAVBAR))),
        dbc.NavItem(dbc.NavLink("NER demo", href="/pknerdemo", active="exact",
                                style=dict(fontSize=common.FONT_SIZE_NAVBAR))),
        dbc.NavItem(dbc.NavLink("REX demo", href="/pkrexdemo", active="exact",
                                style=dict(fontSize=common.FONT_SIZE_NAVBAR))),
        dbc.NavItem(dbc.NavLink("PKDB", href="/pkdatabase", active="exact",
                                style=dict(fontSize=common.FONT_SIZE_NAVBAR))),
        dbc.NavItem(dbc.NavLink("Team", href="/team", active="exact",
                                style=dict(fontSize=common.FONT_SIZE_NAVBAR))),
        dbc.NavItem(dbc.NavLink("Contact", href="/contact", active="exact",
                                style=dict(fontSize=common.FONT_SIZE_NAVBAR))),

    ],
    # brand="PKPDAI",
    # brand_href="/",
    color="primary",
    # color="#F72585",
    # color="#2B4764",
    # color="#ff206e",
    # color="#D81E5B",
    # color="#EB5E55",
    expand="lg",
    dark=True,
    fluid=True,
    style=dict(fontSize=common.FONT_SIZE_NAVBAR)

)

app.layout = html.Div(
    [
        navbar,
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content', children=[], style=common.MAIN_DIV_STYLE)
    ]
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return pkhome.layout
    if pathname == '/pkdocsearch':
        return pkdocsearch.layout
    if pathname == '/pkrexdemo':
        return pkrexdemo.layout
    if pathname == '/pknerdemo':
        return pknerdemo.layout
    if pathname == '/contact':
        return about.layout
    if pathname == '/team':
        return team.layout
    if pathname == '/pkdatabase':
        return pkdatabase.layout
    else:
        return "404 Page Error! Please choose a link"


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True)
