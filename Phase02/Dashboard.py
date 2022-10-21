from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import RPi.GPIO as GPIO
import time
import Freenove_DHT as DHT
DHTPin = 11

app = Dash(external_stylesheets=[dbc.themes.SUPERHERO])
nav_menu= dbc.NavbarSimple(
#     children=[
#         dbc.DropdownMenu(
#             children=[
#                 dbc.DropdownMenuItem("Pages", header=True),
#                 dbc.DropdownMenuItem("Page 1", href="/page-a"),
#                 dbc.DropdownMenuItem("Page 1", href="/page-b"),
#             ],
#             nav=True,
#             in_navbar=True,
#             label="More",
#         ),
#     ],
    brand="PHASE02",
#     brand_href="#",
    color="secondary",
    dark=True,
)
app.layout = html.Div([nav_menu,
    daq.Gauge(
        id='my-gauge-1',
        label="Humidity",
        showCurrentValue=True,
        max=100,
        min=0,
        
    ),
    daq.Thermometer(
        id='my-thermometer-1',
        min=-40,
        max=50,
        label="Temperature",
        showCurrentValue=True,
        units="C",
        color="red",
    ),
    dcc.Interval(
        id = 'humid-update',
        disabled=False,
        interval = 1*3000,  #lower than 3000 for humidity wouldn't show the humidity on the
        n_intervals = 0
    ),
    dcc.Interval(
        id = 'temp-update',
        disabled=False,
        interval = 1*5000,  #lower than 5000 for temperature wouldn't show the temp on the
        n_intervals = 0
    ),
    
])

@app.callback(Output('my-gauge-1', 'value'), Input('humid-update', 'n_intervals'))
def update_output(value):
    dht = DHT.DHT(DHTPin)   #create a DHT class object
    while(True):
        for i in range(0,15):            
            chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
                break
            time.sleep(0.1)
        time.sleep(2)
        print("Humidity : %.2f \t \n"%(dht.humidity))  # for testing on the terminal
        return dht.humidity
    
@app.callback(Output('my-thermometer-1', 'value'), Input('temp-update', 'n_intervals'))
def update_output(value):
    dht = DHT.DHT(DHTPin)   #create a DHT class object
    while(True):
        for i in range(0,15):            
            chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
                break
            time.sleep(0.1)
        time.sleep(2)
        print("Temperature : %.2f \n"%(dht.temperature)) 
        return dht.temperature
    
if __name__ == '__main__':
    app.run_server(debug=True)

        