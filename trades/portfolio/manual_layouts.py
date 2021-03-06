import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import plotly.express as px
from dash_table.Format import Format

from trades.portfolio import stock_calculations
from trades.strategy import get_strategies


def make_manual_dashboard():
    table = make_manual_table()
    sell_input, del_input, sell_date = make_sell_controls()
    strategy_input, strategy_dropdown = make_strategy_controls()
    new_layout = make_new_layout()
    purchase = make_purchase_layout()

    dashboard_div = html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4(children="New Portfolio",
                            style={'text-align': 'center'}),
                    new_layout,
                ],
                    className='pretty_container'
                )
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4(children="Buy Stocks",
                            style={'text-align': 'center'}),
                    purchase,
                    # single_graph,
                ],
                    className='pretty_container'
                )
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4(children="Sell or Delete Stocks",
                            style={'text-align': 'center'}),
                    table,
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                sell_input,
                                sell_date,
                            ])
                        ]),
                        dbc.Col([
                            html.Div([
                                strategy_input,
                                strategy_dropdown,
                            ])
                        ]),
                        dbc.Col([
                            del_input
                        ])
                    ]),
                    # single_graph,
                ],
                    className='pretty_container'
                )
            ]),
        ]),
        dbc.Row([

            dbc.Col([
                html.Div([
                    dbc.Tabs([
                        dbc.Tab(label='Manual', tab_id='tab-1'),
                        dbc.Tab(label='Automatic', tab_id='tab-2'),
                        dbc.Tab(label='Performance', tab_id='tab-3'),
                        dbc.Tab(label='Returns', tab_id='tab-4')

                    ],
                        id='tabs',
                        active_tab='tab-1'),
                    dcc.Graph(id='daily-graph')
                ],
                    className='pretty_container'

                )
            ]),
        ]),
    ]),

    return dashboard_div


def make_return_toggle():
    return_toggle = html.Div([

        dbc.Row([
            dbc.Col([
                dbc.RadioItems(
                    id='return_radio',
                    options=[
                        {'label': 'Portfolio Value', 'value': 1},
                        {'label': 'Portfolio Return', 'value': 2}
                    ],
                    value=1,
                    inline=True,
                    style={'text-align': 'center'})
            ])
        ]),
        ])
    return return_toggle


def make_individual_graph_layout(brand_name, portfolio_list):

    graph = px.line()

    graph_div = html.Div([
        dbc.Row([
            dbc.Col([
                html.Div(dbc.Alert(id='sell_alert',
                                   children="Select Individual Securities",
                                   color="warning",
                                   is_open=False,
                                   duration=4000))
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='portfolio_graph',
                          figure=graph)
            ])
        ])

    ])

    return graph_div


def make_purchase_layout():

    purchase_alert = dbc.FormGroup([
        dbc.Alert(id = 'purchase_alert',
                  children="No new security has been added",
                  color="warning",
                  is_open=False,
                  duration=4000)
    ])

    securities_list = stock_calculations.get_securities_list()

    security_input = dbc.FormGroup([
        dbc.Label("Stock Ticker"),
        dbc.Input(
            id='ticker_input',
            placeholder='SPY',
            type='text',
        ),
        dcc.Dropdown(
            id='ticker_sp500_input',
            options=securities_list,
            style={'display': 'none'}
        ),
    ])

    security_radio = dbc.FormGroup([
        dbc.Label("SP500/Custom"),
            dbc.RadioItems(
                id='ticker_input_radio',
                options=[
                    {'label': 'SP500', 'value': 'SP500'},
                    {'label': 'Custom', 'value': 'Custom'}
                ],
                value='Custom',
            ),
    ])

    # security_input = dbc.FormGroup([
    #     dbc.Label("Company"),
    #     dcc.Dropdown(
    #         id='manage_security_input',
    #         options=securities_list,
    #         value='CVX',
    #     ),
    # ])

    value_input = dbc.FormGroup([
        dbc.Label("Value (US $)"),
        dbc.Input(id='value_input',
                  type='number',
                  value=100.00,
                  ),
    ])

    purchase_date_input = dbc.FormGroup([
        dbc.Label("Purchase Date"),
        dcc.DatePickerSingle(id = 'purchase_date_input', style={'width': '99%'}),
    ])

    source_input = dbc.FormGroup([
        dbc.Label("Source"),
        dbc.RadioItems(id="source_input",
                       options=[{'label': "Internal Funds", 'value':'Internal Funds'},
                                {'label': 'External Funds', 'value': 'External Funds'}],
                       value = 'External Funds'),


    ])

    submit_input = dbc.FormGroup([
        dbc.Label("Buy"),
        dbc.Button(id='submit_input',
                   children="Purchase",
                   block=True)
    ])

    form_div = html.Div([
        dbc.Form([
            dbc.Row([
                dbc.Col([
                    security_radio,
                ]),
                dbc.Col([
                    security_input
                ]),
                dbc.Col([
                    value_input
                ]),
                dbc.Col([
                    purchase_date_input
                ]),
                dbc.Col([
                    source_input
                ]),
                dbc.Col([
                    submit_input
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    purchase_alert
                ])
            ]),
        ])
    ],
        style={'margin-top': '5px'}
    )

    return form_div


def make_manual_table():
    sell_div = make_sell_layout()

    controls = dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.FormGroup([
                    sell_div
                ],
                )
            ]),
        ]),
    ])

    return controls


def make_strategy_controls():
    strategy_input = dbc.FormGroup([
        dbc.Button(id='strategy_input', children='Update Strategy', block=True)
    ])

    strategy_list = get_strategies()

    strategy_dropdown = dbc.FormGroup([
        dcc.Dropdown(
            id='strategy_dropdown',
            options=[{'label': i.name, 'value': i.name} for i in strategy_list])
    ])

    return strategy_input, strategy_dropdown


def make_sell_controls():
    sell_input = dbc.FormGroup([
        dbc.Button(id='sell_input', children="Sell", block=True),
    ])

    del_input = dbc.FormGroup([
        dbc.Button(id='delete_input', children="Delete", block=True)
    ])

    sell_date = dbc.FormGroup([
        dcc.DatePickerSingle(id='sell_date'),
    ])

    return sell_input, del_input, sell_date,


def make_new_layout():

    name_input = dbc.FormGroup([
        dbc.Label("Name"),
        dbc.Input(id='new-portfolio-input',
                  type='text',
                  placeholder='Portfolio Name',
                  ),
        dbc.FormText("Name this Portfolio"),
    ])

    create_input = dbc.FormGroup([
        dbc.Label("Create"),
        dbc.Button(id='new-portfolio-button',
                   children="Create Portfolio",
                   block=True),
        dbc.FormText("Make a New Portfolio")
    ])

    new_layout = html.Div([
        dbc.Row([
            dbc.Col([
                name_input
            ]),
            dbc.Col([
                create_input
            ])
        ]),
    ])

    return new_layout


def make_sell_layout():

    sell_alert = dbc.Alert(id='sell_alert',
                           children="Sell or Delete Stocks from the Selected Portfolio",
                           color='warning',
                           is_open=False,
                           duration=4000,
                           style={"position": "fixed", "top": 0})

    delete_alert = dbc.Alert(id='delete_alert',
                             children="Sell or Delete Stocks from the Selected Portfolio",
                             color='warning',
                             is_open=False,
                             duration=4000,
                             style={"position": "fixed", "top": 0})

    strategy_alert = dbc.Alert(id='strategy_alert',
                               children="Update the Strategy of the Selected Trade",
                               color='warning',
                               is_open=False,
                               duration=4000,
                               style={"position": "fixed", "top": 0})


    strategies = get_strategies()


    table_input = dbc.FormGroup([
        dash_table.DataTable(id='portfolio_entries',
                             columns=(
                                 [{'id': 'portfolio', 'name': 'Portfolio'},
                                  {'id': 'security', 'name': 'Company'},
                                  {'id': 'purchase_value', 'name': 'Purchase Value'},
                                  {'id': 'purchase_date', 'name': 'Purchase Date'},
                                  {'id': 'purchase_internal', 'name': 'Internal?'},
                                  {'id': 'sell_value', 'name': 'Sell Value', 'type': 'numeric', 'format': Format(precision=5)},
                                  {'id': 'sell_date', 'name': 'Sell Date', 'type': 'datetime'},
                                  {'id': 'strategy', 'name': 'Strategy'},
                                  ]),
                             row_selectable='single'),
        dbc.FormText("Select the Secruity to Sell, or Delete"),
    ])

    data_div = html.Div([
        dbc.Row([
            dbc.Col([
                table_input,
            ],
            style={'margin-left': '15px', 'margin-right': '15px'}),
        ]),
        dbc.Row([
            dbc.Col([
                sell_alert
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                delete_alert
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                strategy_alert
            ]),
        ]),
    ],
        style={'margin-top': '5px', 'width': '100%', 'margin-right': '15px'})

    return data_div


def make_navbar_view():
    navbar_div = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.NavbarSimple(
                    id='stock_navbar',
                    children=[
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(
                                    id='portfolio_input',
                                    placeholder="Select Portfolio",
                                    style={'min-width': '200px'}),
                            ]),
                            dbc.Col([
                                dbc.Button(id='delete-portfolio-button',
                                           children='Delete Portfolio',
                                           block=True)
                            ])
                        ]),
                    ],
                    color="primary",
                    dark=True)
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Alert(id='delete-portfolio-alert',
                          children="Delete Entire Portfolio",
                          color='warning',
                          is_open=False,
                          duration=4000,
                          style={"position": "fixed", "top": 0})

            ])
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Alert(id='new-portfolio-alert',
                          children='New Portfolio Created',
                          color='warning',
                          is_open=False,
                          duration=4000,
                          style={"position": "fixed", "top": 0},
                          )
            ])
        ])
    ])
    return navbar_div
