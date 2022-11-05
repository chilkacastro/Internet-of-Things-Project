from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_extensions as de
import dash_daq as daq
import RPi.GPIO as GPIO
import base64
from PIL import Image       # use and download PILLOW for it to work  https://pillow.readthedocs.io/en/stable/installation.html
import time
from time import sleep
import Freenove_DHT as DHT
import smtplib, ssl, getpass, imaplib, email
import random
from paho.mqtt import client as mqtt_client
from datetime import datetime

#------------PHASE03 VARIABLE CODES--------------
# broker = '192.168.0.158' #ip in Lab class
broker = '192.168.1.110'
port = 1883
topic = "esp/lightintensity"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'
esp_message = 0
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
LedPin = 35 # Led Pin/Enable Pin
GPIO.setup(LedPin,GPIO.OUT)
email_counter = 0    # just checks if email has been sent at some stage
# -----------------------------------------------

#------------PHASE02 VARIABLE CODES--------------
EMAIL = 'iotdashboard2022@outlook.com'
PASSWORD = 'iotpassword123'

SERVER = 'outlook.office365.com'
temperature = 0
DHTPin = 40 # equivalent to GPIO21
fan_status_checker=False

#GPIO.setmode(GPIO.BOARD)
#GPIO.setwarnings(False)
#Motor1 = 35 # Enable Pin
#Motor2 = 37 # Input Pin
#Motor3 = 33 # Input Pin

#GPIO.setup(Motor1,GPIO.IN)
#GPIO.setup(Motor2,GPIO.IN)
#GPIO.setup(Motor3,GPIO.IN)

url="https://assets5.lottiefiles.com/packages/lf20_UdIDHC.json"
options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))

# -----------------------------------------------

app = Dash(external_stylesheets=[dbc.themes.SKETCHY])
nav_menu= dbc.NavbarSimple(
    brand="PHASE02",
    color="secondary",
    dark=True,
)
app.layout = html.Div([nav_menu,
#     html.Div([
#         dbc.Row([
#             dbc.Col(daq.Gauge(
#                 id='my-gauge-1',
#                 label="Humidity",
#                 showCurrentValue=True,
#                 max=100,
#                 min=0)
#             , width=4),
#         
#             dbc.Col(
#                 dbc.Row(
#                     [
#                     daq.Thermometer(
#                     id='my-thermometer-1',
#                     min=-40,
#                     max=160,
#                     scale={'start': -40, 'interval': 25},
#                     label="Temperature(Celsius)",
#                     showCurrentValue=True,
#                     units="C",
#                     color="red"),
#                     html.Button('Fahrenheit', id='fahrenheit-button', n_clicks=0)
#                     ]
#                     )
#                  ,width=4),
#             dbc.Col(
#                 dbc.Row(
#                     [
#                     html.H1('Fan',style={'text-align':'center'}),
#                     html.Div([de.Lottie(options=options, width="25%", height="25%", url=url)], id='my-gif', style={'display':'none'}),
#                     html.H1(id='my_h1',style={'text-align':'center'})
#                     ]
#                 )
#             , width=4),
#             dbc.Col(
#                 dbc.Row(
#                     [
#                     html.H1('LightIntensity',style={'text-align':'center'}),
#                     html.H1(id='light_h1',style={'text-align':'center'})
#                     ]
#                 )
#             , width=4)
#         ]
#         )
#      ]),
        daq.LEDDisplay(
            id='light-intensity',
            label="Light Intensity",
        ),
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
# 
# @app.callback(Output('my-gauge-1', 'value'), Input('humid-update', 'n_intervals'))
# def update_output(value):
#     dht = DHT.DHT(DHTPin)   #create a DHT class object
#     while(True):
#         for i in range(0,15):            
#             chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
#             if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
#                 break
#             time.sleep(0.1)
#         time.sleep(2)
#         print("Humidity : %.2f \t \n"%(dht.humidity))  # for testing on the terminal
#         return dht.humidity
#     
# @app.callback([Output('my-thermometer-1', 'value')], Input('temp-update', 'n_intervals'))
# def update_output(value):
#     dht = DHT.DHT(DHTPin)   #create a DHT class object
#     while(True):
#         for i in range(0,15):            
#             chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
#             if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
#                 break
#             time.sleep(0.1)
#         time.sleep(2)
#         temperature = dht.temperature
#         print("Temperature : %.2f \n"%(dht.temperature))
#         if (dht.temperature >= 24):
#             sendEmail()
#           
#         return dht.temperature
# 
# def sendEmail():
#         port = 587  # For starttls
#         smtp_server = "smtp-mail.outlook.com"
#         sender_email = "iotdashboard2022@outlook.com"
#         receiver_email = "iotdashboard2022@outlook.com"
#         password = 'iotpassword123'
#         subject = "Subject: FAN CONTROL" 
#         body = "Your home temperature is greater than 24. Do you wish to turn on the fan. Reply YES if so."
#         message = subject + '\n\n' + body
#         context = ssl.create_default_context()
#         with smtplib.SMTP(smtp_server, port) as server:
#             server.ehlo()  # Can be omitted
#             server.starttls(context=context)
#             server.ehlo()  # Can be omitted
#             server.login(sender_email, password)
#             server.sendmail(sender_email, receiver_email, message) 
# 
# def is_fan_on():  
#     if GPIO.input(Motor1) and not GPIO.input(Motor2) and GPIO.input(Motor3):
#         return True
#     else:
#         return False
# 
# @app.callback(Output('my-fan-1', 'value'), Input('fan-update', 'n_intervals'))
# def update_output(value):
#     fan_status_checker = is_fan_on()
# #     print(fan_status_checker)
#     return True if fan_status_checker else False
#         # return True if GPIO.input(Motor1) and not GPIO.input(Motor2) and GPIO.input(Motor3) else False
# 
# 
# @app.callback([Output('my_h1', 'children'), Output('my-gif', 'style')],Input('interval_component', 'n_intervals'))
# def update_h1(n):
#     fan_status_checker = is_fan_on()
#     
#     if fan_status_checker:
#         return "Status: On", {'display':'block'}
#     
#     else:
#         return "Status: Off",{'display':'none'}
    
# CONVERSION NOT YET DONE
# @app.callback([Output('my-thermometer-1', 'value')] ,
#               [Input('temp-update', 'n_intervals'),
#               Input('fahrenheit-button', 'n_clicks')])
# def changeToFahrenheit(n_intervals, n_clicks): 
#     return (temperature * 1.8) + 32

# PHASE 03 CODE FOR SUBSCRIBE 
def sendEmail():
        port = 587  # For starttls
        smtp_server = "smtp-mail.outlook.com"
        sender_email = "iotdashboard2022@outlook.com"
        receiver_email = "iotdashboard2022@outlook.com"
        password = 'iotpassword123'
        subject = "Subject: LIGHT NOTIFICATION" 
        current_time = datetime.now()
        time = current_time.strftime("%H:%M")
        body = "The Light is ON at " + time
        message = subject + '\n\n' + body
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            
 
def turn_led_on(value):         # turn led on depending on value send email and increase the email counter to know there is an email sent
     if value < 400:
        GPIO.output(LedPin, True)
        sendEmail()
        email_counter += 1
     else:
        GPIO.output(LedPin, False)  

@app.callback(Output('light-intensity', 'value'), Input('light-intensity-update', 'n_intervals'))  
def update_output(value):
    run()
    # print("Here: ", esp_message) UNCOMMENT TO SEE THE VALUE PASSED FROM THE PUBLISHER 
    value = esp_message
    turn_led_on(value)              # turn led on and send email.
    return value

@app.callback(Output('email_h1', 'children'), Input('interval_component', 'n_intervals'))       # update email sent message
def update_email_status(n):
     if email_counter > 0:
         return "Email has been sent."
     
     else:
         return "No email has been sent."


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            time.sleep(5)
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global esp_message
        esp_message = int(float(msg.payload.decode()))
        
    client.subscribe(topic)
    client.on_message = on_message
    
def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()

if __name__ == '__main__':
    app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)

        


        