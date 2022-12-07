import logging
import os
import subprocess
from dash import Dash, html, dcc, Input, Output, State
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import dash_bootstrap_components as dbc
import dash_extensions as de
import dash_daq as daq
import RPi.GPIO as GPIO
import base64
import bluetooth
import time
from time import sleep
import Freenove_DHT as DHT
import smtplib, ssl, getpass, imaplib, email
import random
from paho.mqtt import client as mqtt_client
from datetime import datetime
import pymysql
import pymysql.cursors

#removes the post update component in the terminal
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Dash(__name__,  meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0",
        }
    ])
theme_change = ThemeChangerAIO(aio_id="theme", radio_props={"persistence": True}, button_props={"color": "danger","children": "Change Theme"})
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(theme_change),
    ],
    brand="IOT SMART HOME",
    color="dark",
    dark=True,
    sticky="top"
)

#------------thresholds and user info-----
esp_rfid_message = "RFID FROM MQTT"
user_id = "Default"
temp_threshold = 25.0
light_threshold = 0
humidity = 40
path_to_picture = 'assets/minion.jpg'

#------------PHASE03 VARIABLE CODES--------------
#broker = '192.168.0.158' #ip in Lab class
# broker = '192.168.76.10'
broker = '192.168.1.110' #chilka home
#broker = '10.0.0.218'
#broker = '192.168.208.198'
#broker = "192.168.225.198"
port = 1883
topic1 = "esp/lightintensity"
topic2 = "esp/lightswitch"
topic3 = "esp/rfid"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'

esp_message = 0
# send_user_email_counter = 0
# esp_lightswitch_message = "OFF"
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

email_counter = 0    # just checks if email has been sent at some stage
# -----------------------------------------------

#------------PHASE02 VARIABLE CODES--------------
EMAIL = 'iotdashboard2022@outlook.com'
PASSWORD = 'iotpassword123'

SERVER = 'outlook.office365.com'
temperature = 0
DHTPin = 40 # equivalent to GPIO21
fan_status_checker=False

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
Motor1 = 35 # Enable Pin
Motor2 = 37 # Input Pin
Motor3 = 33 # Input Pin
LedPin = 38
GPIO.setup(Motor1, GPIO.IN)
GPIO.setup(Motor2, GPIO.IN)
GPIO.setup(Motor3, GPIO.IN)
GPIO.setup(LedPin, GPIO.OUT)

light_bulb_off = 'assets/lightbulbOFF.png'        
light_bulb_on = 'assets/lightbulbON.png'       
url="https://assets5.lottiefiles.com/packages/lf20_UdIDHC.json"
options = dict(loop=True, autoplay=True, rendererSettings=dict(preserveAspectRatio='xMidYMid slice'))
url2 = "https://assets8.lottiefiles.com/packages/lf20_ylvmhzmx.json"
# -----------------------------------------------
#Components

# related to gauge
daq_Gauge = daq.Gauge(
                id='my-gauge-1',
                label="Humidity",
                showCurrentValue=True,
                size=200,
                max=100,
                min=0)

# related to temperature
daq_Thermometer = daq.Thermometer(
                        id='my-thermometer-1',
                        min=-40,
                        max=50,
                        scale={'start': -40, 'interval': 10},
                        label="Temperature",
                        showCurrentValue=True,
                        height=150,
                        units="C",
                        color="red")
daq_Fahrenheit_ToggleSwitch = daq.ToggleSwitch(
        id='fahrenheit-switch',
        label='Fahrenheit',
        labelPosition='bottom',
        value=False)

# all fan related html
html_Fan_Label = html.H6('Fan',style={'text-align':'center'})
html_Div_Fan_Gif = html.Div([de.Lottie(options=options, width="40%", height="25%", url=url, id='lottie-gif', isStopped=True, isClickToPauseDisabled=True)], id='fan_display')
html_Bluetooth_Gif = html.Div([de.Lottie(options=options, width="40%", height="25%", url=url2, isClickToPauseDisabled=True)])
html_Fan_Status_Message = html.H5(id='fan_status_message',style={'text-align':'center'})


# all related to light intensity and led
html_Light_Intensity_Label =  html.H6('Light Intensity',style={'text-align':'center'})
html_bluetooth_Label =  html.H6('Bluetooth Devices',style={'text-align':'center'})
daq_Led_Light_Intensity_LEDDisplay = daq.LEDDisplay(
                                        id='light-intensity',
                                        label="Light Intensity Value",
                                        labelPosition='bottom',
                                        value = 0,
                                        size = 50)
html_Led_Status_Message = html.H1(id='light_h1',style={'text-align':'center'})  #not used yet

# intervals
fan_Status_Message_Interval = dcc.Interval(
            id='fan_status_message_update',
            disabled=False,
            interval=1 * 3000,
            n_intervals=0)
            
fan_Interval = dcc.Interval(
            id = 'fan-update',
            disabled=False,
            interval = 1 * 8000,  
            n_intervals = 0)
            
humidity_Interval = dcc.Interval(
            id = 'humid-update',
            disabled=False,
            interval = 1 * 3000,
            n_intervals = 0)

temperature_Interval =  dcc.Interval(
            id = 'temp-update',
            disabled=False,
            interval = 1*20000,   #lower than 5000 for temperature wouldn't show the temp on the terminal #1800000 equivalent to 30 mins
            n_intervals = 0)

light_Intensity_Interval =  dcc.Interval(
            id = 'light-intensity-update',
            disabled=False,
            interval = 1*5000,   
            n_intervals = 0)

led_On_Email_Interval = dcc.Interval(
            id = 'led-email-status-update',
            disabled=False,
            interval = 1*5000,   
            n_intervals = 0)

rfid_Interval = dcc.Interval(
            id = 'rfid-code-update',
            disabled=False,
            interval = 1*10000,   
            n_intervals = 0)

userinfo_Interval = dcc.Interval(
            id = 'userinfo-update',
            disabled=False,
            interval = 1*2000,   
            n_intervals = 0)

bluetooth_Interval = dcc.Interval(
            id = 'bluetooth-update',
            disabled=False,
            interval = 1*2000,   
            n_intervals = 0)
fahrenheit_Interval = dcc.Interval(
            id = 'fahrenheit-update',
            disabled=False,
            interval = 1*2000,   
            n_intervals = 0)

fan_Label = html.H6("Electric Fan", style={'text-align': 'center'});
sidebar = html.Div([
    html.H3('User Profile', style={'text-align': 'center', 'margin-top': '20px'}),
    dbc.CardBody([
            html.Img(src=path_to_picture, id="picture_path", style={'border-radius': '80px', 'width':'140px', 'height':'140px', 'object-fit': 'cover', 'display': 'block','margin-left':'auto','margin-right': 'auto'}),
            html.H6("Username:" + str(user_id), style={'margin-top':'30px'}, id="username_user_data"),
            html.H4("Favorites ", style={'margin-top':'40px'}),
            html.H6("Humidity: " + str(humidity), style={'margin-left':'15px'}, id="humidity_user_data"),
            html.H6("Temperature: " + str(temp_threshold), style={'margin-left':'15px'}, id="temperature_user_data"),
            html.H6("Light Intensity: " + str(light_threshold), style={'margin-left':'15px'}, id="lightintensity_user_data")
            ])
    ])

card_content1 = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        html.B("SMART HOME COMPONENTS"),
                        className="text-center mt-4 mb-2",
                    )
                )
            ]
        ),
        dbc.Row([
            dbc.Col(dbc.Card(dbc.Col(daq_Gauge), color="secondary", inverse=True, style={"width": "30rem", 'height': "22rem"}), width="auto"),
            dbc.Col(dbc.Card(dbc.Col(html.Div([daq_Thermometer, daq_Fahrenheit_ToggleSwitch])), color="secondary", inverse=True, style={"width": "30rem", 'height': "22rem"}), width="auto"),
            dbc.Col(dbc.Card(dbc.Col(html.Div([fan_Label, html_Div_Fan_Gif, html_Fan_Status_Message])), color="secondary", inverse=True, style={"width": "30rem", 'height': "22rem"}), width="auto")],
            justify="center",
        ),
        dbc.Row([
            dbc.Col(dbc.Card(
                     html.Div([
                         html_Light_Intensity_Label,
                         html.Img(id="light-bulb", src=light_bulb_off,
                                  style={'width':'80px', 'height': '110px',
                                  'display': 'block','margin-left':'auto','margin-right': 'auto', 'margin-top':'10px'}),
                         daq_Led_Light_Intensity_LEDDisplay,
                         html.H5(id='email_heading',style ={"text-align":"center"}) ]),
                     color="secondary", inverse=True, style={"width": "30rem", 'height': "22rem"}), width="auto"),
            dbc.Col(dbc.Card(
                html.Div([
                    html_bluetooth_Label,
                    html_Bluetooth_Gif,
                    html.H5("Number of Bluetooth Devices: ",
                            id='bluetooth_heading',style ={"text-align":"center", 'margin-top':'10px'}),
                     html.H5(id='rfid_heading',style ={"text-align":"center", 'margin-top':'10px'})
                ]),
                color="secondary", inverse=True, style={"width": "30rem", 'height': "22rem"}), width="auto")],
            justify="center",
        className="mt-5"),
    ],
    fluid=True,)


content = html.Div([
           dbc.Row([
                card_content1,
                humidity_Interval, temperature_Interval, light_Intensity_Interval, led_On_Email_Interval, rfid_Interval,
                userinfo_Interval, bluetooth_Interval, fahrenheit_Interval, fan_Status_Message_Interval, fan_Interval
             ]),
        ])

app.layout = dbc.Container([
                dbc.Row(navbar),
                dbc.Row([
                    dbc.Col(sidebar, width=2), 
                    dbc.Col(content, width=10, className="bg-secondary") # content col
                ], style={"height": "100vh"}), # outer
            ], fluid=True) #container

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
    
@app.callback(
    [Output('my-thermometer-1', 'value'),
     Output('my-thermometer-1', 'min'),
     Output('my-thermometer-1', 'max'),
     Output('my-thermometer-1', 'scale'),
     Output('my-thermometer-1', 'units')],
    [Input('fahrenheit-switch', 'value'),
    Input('my-thermometer-1', 'value'),
    Input('temp-update', 'n_intervals')])
def update_output(switch_state, temp_value, interval_value):
    dht = DHT.DHT(DHTPin)   #create a DHT class object
    while(True):
        for i in range(0,15):            
            chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
                break
            time.sleep(0.1)
        time.sleep(2)
        temperature = dht.temperature
        print("Temperature : %.2f \n"%(dht.temperature))
        if (dht.temperature >= temp_threshold):
            sendEmail()
            
        if switch_state:
           return (temperature * 1.8) + 32, 40, 120, {'start': 40, 'interval': 10}, 'F'
        else:
            return temperature, -40, 50, {'start': -40, 'interval': 10}, 'C'

def sendEmail():
        port = 587  # For starttls
        smtp_server = "smtp-mail.outlook.com"
        sender_email = "iotdashboardother2022@outlook.com"
        receiver_email = "iotdashboardother2022@outlook.com"
        password = 'iotpassword123'
        subject = "Subject: FAN CONTROL" 
        body = "Your home temperature is greater than your desired threshold. Do you wish to turn on the fan. Reply YES if so."
        message = subject + '\n\n' + body
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)


def is_fan_on():  
    if GPIO.input(Motor1) and not GPIO.input(Motor2) and GPIO.input(Motor3):
        return True
    else:
        return False

@app.callback([Output('fan_status_message', 'children'), Output('lottie-gif', 'isStopped')],
              Input('fan_status_message_update', 'n_intervals'))
def update_h1(n):
    fan_status_checker = is_fan_on()
    
    if fan_status_checker:
        return "Status: On", False
    
    else:
        return "Status: Off", True
    
@app.callback([Output('username_user_data', 'children'),
               Output('humidity_user_data', 'children'),
               Output('temperature_user_data', 'children'),
               Output('lightintensity_user_data', 'children'),
               Output('picture_path', 'src')],
               Input('userinfo-update', 'n_intervals'))
def update_user_information(n):
    return "Username: " + str(user_id) ,"Humidity: 40" ,"Temperature: " +  str(temp_threshold), "Light Intensity: " + str(light_threshold), path_to_picture
    

# PHASE 03 CODE FOR SUBSCRIBE 
def sendLedStatusEmail():
         print("PASSED BY SENDLEDSTATUSEMAIL method")
         port = 587  # For starttls
         smtp_server = "smtp-mail.outlook.com"
         sender_email = "iotdashboardother2022@outlook.com"
         receiver_email = "iotdashboardother2022@outlook.com"
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


def sendUserEnteredEmail(user_name):
        port = 587  # For starttls
        smtp_server = "smtp-mail.outlook.com"
        sender_email = "iotdashboardother2022@outlook.com"
        receiver_email = "iotdashboardother2022@outlook.com"
        password = 'iotpassword123'
        subject = "Subject: USER ENTERED" 
        current_time = datetime.now()
        time = current_time.strftime("%H:%M")
        body = user_name + " has entered at: " + time
        message = subject + '\n\n' + body
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message) 
        
            
@app.callback(Output('light-intensity', 'value'), Input('light-intensity-update', 'n_intervals'))  
def update_output(value):
#     run()
    print("Here is light intensity: ", esp_message) 
    return esp_message

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
#             print("Connected to MQTT Broker!")
            time.sleep(10)
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def on_message_from_lightintensity(client, userdata, message):
   global esp_message
   esp_message = int(float(message.payload.decode()))
#    print("Message Received from Photoresistor: ")
#    print(esp_message)

# def on_message_from_lightswitch(client, userdata, message):
#    global esp_lightswitch_message
#    esp_lightswitch_message = message.payload.decode()
#    print("Message Received from lightswitch: ")
#    print(esp_lightswitch_message)

def on_message_from_rfid(client, userdata, message):
   global esp_rfid_message
#    global send_user_email_counter
#    send_user_email_counter = 0
   esp_rfid_message = message.payload.decode()
   print("Message Received from rfid: ")
   print(esp_rfid_message)
   get_from_database(esp_rfid_message)
   sendUserEnteredEmail(esp_rfid_message)

def on_message(client, userdata, message):
   print("Message Received from Others: "+message.payload.decode())
   
   
def get_from_database(rfid):
    #Connect to the database
    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             database='IOT',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
    # Read a single record
        sql = "SELECT * FROM USER WHERE id = %s"
        # To execute the SQL query
        cursor.execute(sql, (rfid))
        user_info = cursor.fetchone()
    print("Result from database select: ")
    print(user_info)
    if(user_info):
        global user_id
        user_id = user_info['id']
        global temp_threshold
        temp_threshold = user_info['temp_threshold']
        global light_threshold
        light_threshold = user_info['light_threshold']
        global path_to_picture
        path_to_picture = user_info['picture']
        
    print(str(user_id) + " " + str(temp_threshold) + " " + str(light_threshold) + " " + path_to_picture)
    
def run():
    client = connect_mqtt()
    client.subscribe(topic1, qos=1)
#     client.subscribe(topic2, qos=1)
    client.subscribe(topic3, qos=1)
    client.message_callback_add(topic1, on_message_from_lightintensity)
#     client.message_callback_add(topic2, on_message_from_lightswitch)
    client.message_callback_add(topic3, on_message_from_rfid)
    client.loop_start()
    
def send_led_email_check(lightvalue):         # send email and increase the email counter to know there is an email sent
      global email_counter
      if lightvalue < light_threshold and email_counter == 0:
         print("passed here in send_led_email_check")
         sendLedStatusEmail()
         email_counter += 1

@app.callback([Output('email_heading', 'children'), Output('light-bulb', 'src')], Input('led-email-status-update', 'n_intervals'))       # update email sent message
def update_email_status(value):
    lightvalue = esp_message
    send_led_email_check(lightvalue)
    
    if email_counter > 0 and lightvalue < light_threshold:
        GPIO.output(LedPin, GPIO.HIGH)
        return "Email has been sent. Lightbulb is ON", light_bulb_on
    elif email_counter > 0 and lightvalue > light_threshold:
        GPIO.output(LedPin, GPIO.LOW)
        return "Email has been sent. Lightbulb is OFF", light_bulb_off
    else:
        GPIO.output(LedPin, GPIO.LOW)
        return "No email has been sent. Lightbulb is OFF", light_bulb_off
   
@app.callback(Output('rfid_heading', 'children'), Input('rfid-code-update', 'n_intervals'))  
def update_output(value):
    #run()
#     if (send_user_email_counter == 0):
#         sendUserEnteredEmail(esp_rfid_message)
#         send_user_email_counter += 1
    return "RFID FROM MQTT: " + esp_rfid_message

@app.callback(Output('bluetooth_heading', 'children'), Input('bluetooth-update', 'n_intervals'))
def update_bluetooth(value):
    return "Number of Bluetooth devices: " + str(scanNumberOfBluetoothDevices())

def scanNumberOfBluetoothDevices():
    number_of_devices = 0
    output = subprocess.check_output(['bluetoothctl', 'devices'])
    for word in output.split():
        if word == b'Device':
            number_of_devices += 1
    
    return number_of_devices
        
run()
if __name__ == '__main__':
   app.run_server(debug=True)
#     app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)

