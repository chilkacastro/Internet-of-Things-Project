from dash import Dash, html, dcc, Input, Output
import dash_daq as daq
import RPi.GPIO as GPIO
import time
import Freenove_DHT as DHT
DHTPin = 11

app = Dash(__name__)

app.layout = html.Div([
    daq.Gauge(
        id='my-gauge-1',
        label="Humidity",
        max=100,
        min=0
        
    ),
    daq.Thermometer(
        id='my-thermometer-1',
        min=0,
        max=105,
        value=100,
        label="Temperature",
        showCurrentValue=True,
        units="C",
        color="red"
    ),

])

@app.callback(Output('my-gauge-1', 'value'), Input('my-gauge-1', 'value'))
def update_output(value):
    dht = DHT.DHT(DHTPin)   #create a DHT class object
    while(True):
        for i in range(0,15):            
            chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
                break
            time.sleep(0.1)
        time.sleep(2)
        return dht.humidity
    
@app.callback(Output('my-thermometer-1', 'value'), Input('my-thermometer-1', 'value'))
def update_output(value):
    dht = DHT.DHT(DHTPin)   #create a DHT class object
    while(True):
        for i in range(0,15):            
            chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
                break
            time.sleep(0.1)
        time.sleep(2)
        return dht.temperature
    
if __name__ == '__main__':
    app.run_server(debug=True)

        