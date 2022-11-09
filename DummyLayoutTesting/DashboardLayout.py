from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_extensions as de
import dash_daq as daq
# import RPi.GPIO as GPIO
import base64
# from PIL import Image       # use and download PILLOW for it to work  https://pillow.readthedocs.io/en/stable/installation.html
import time
# from time import sleep
# import Freenove_DHT as DHT
import smtplib, ssl, getpass, imaplib, email
import random
# from paho.mqtt import client as mqtt_client
from datetime import datetime


url="https://assets5.lottiefiles.com/packages/lf20_UdIDHC.json"
options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))

# -----------------------------------------------

app = Dash(external_stylesheets=[dbc.themes.SOLAR])
nav_menu= dbc.NavbarSimple(
    brand="PHASE03",
    color="secondary",
    dark=True,
)

# row = html.Div(
#     [
#         dbc.Row(dbc.Col(html.Div("A single column"))),
#         dbc.Row(
#             [
#                 dbc.Col(html.Div("One of three columns")),
#                 dbc.Col(html.Div("One of three columns")),
#                 dbc.Col(html.Div("One of three columns")),
#             ]
#         ),
#     ]
top_card = dbc.Card(
    [
        dbc.CardImg(src="assets/minion.jpg", top=True),
        dbc.CardBody(
            dbc.Row([
                html.H1("User Profile: ",style={'text-align':'center'}),
                html.P("Username:" , className="card-text"),
                html.P("Favorites:",  className="card-text"),
                html.P("Temperature:",  className="card-text"),
                html.P("Humidity:",  className="card-text"),
                html.P("Light intensity:",  className="card-text"),
            ])
        )
    ],
    style={"width": "25rem"},
)
app.layout = html.Div([nav_menu,
    html.Div([
        dbc.Row([
            dbc.Col(top_card, width="auto"),

            dbc.Col(
                dbc.Row(
                    [
                    daq.Gauge(
                    id='my-gauge-1',
                    label="Humidity",
                    showCurrentValue=True,
                    max=100,
                    value= 64,
                    min=0),
                    daq.Thermometer(
                    id='my-thermometer-1',
                    min=-40,
                    max=160,
                    value= 24.5,
                    scale={'start': -40, 'interval': 25},
                    label="Temperature(Celsius)",
                    showCurrentValue=True,
                    units="C",
                    color="red"),
                    # html.Button('Fahrenheit', id='fahrenheit-button', n_clicks=0), 
                    html.H1('Fan',style={'text-align':'center'}),
                    html.Div([de.Lottie(options=options, width="25%", height="25%", url=url)], id='my-gif', style={'display':'none'}),
                    html.H1(id='my_h1',style={'text-align':'center'})
                    ]
                )
            , width=5),
            dbc.Col(
                dbc.Row(
                    [
                    html.H1(id='light_h1',style={'text-align':'center'}),
                    daq.LEDDisplay(
                        id='light-intensity',
                        label="Light Intensity",
                        value = 5),
                    
                    ]
                )
            , width=4)
        ]
        )
    ]),
        
        html.H1(
            id='email_h1',
            style={'text-align':'center'}
        ),
        dcc.Interval(
            id='interval_component',
             disabled=False,
             interval=5*1000, # 10 seconds
             n_intervals=0,
                 # max_intervals=-1, # -1 goes on forever no max
        ),
        dcc.Interval(
            id = 'humid-update',
            disabled=False,
            interval = 1*3000,  #lower than 3000 for humidity wouldn't show the humidity on the terminal
            n_intervals = 0
        ),
        dcc.Interval(
            id = 'temp-update',
            disabled=False,
            interval = 1*8000,   #lower than 5000 for temperature wouldn't show the temp on the terminal #1800000 equivalent to 30 mins
            n_intervals = 0
        ),
        dcc.Interval(
            id = 'fan-update',
            disabled=False,
            interval = 1*8000,  
            n_intervals = 0,
        ),
        dcc.Interval(
            id = 'light-intensity-update',
            disabled=False,
            interval = 1*1000,   
            n_intervals = 0,
        ),
])

# @app.callback(
#     Output(component_id='my-output', component_property='children'),
#     Input(component_id='my-input', component_property='value')
# )
# def update_output_div(input_value):
#     return f'Output: {input_value}'


if __name__ == '__main__':
    app.run_server(debug=True)
