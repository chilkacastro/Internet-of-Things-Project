from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import RPi.GPIO as GPIO
import base64
from PIL import Image       # use and download PILLOW for it to work  https://pillow.readthedocs.io/en/stable/installation.html
import time
from time import sleep
import Freenove_DHT as DHT
import smtplib, ssl, getpass, imaplib, email

EMAIL = 'iotdashboard2022@outlook.com'
PASSWORD = 'iotpassword123'

SERVER = 'outlook.office365.com'

DHTPin = 40 #equivalent to GPIO21
FanStatusIndicator = ""  #Indicator for fan
#FanImage = '' # set fan image name.


image_path_fanon = 'assets/fanon.png'
image_path_fanoff = 'assets/fanoff.jpg'

#path_result = ''

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
Motor1 = 35 # Enable Pin
Motor2 = 37 # Input Pin
Motor3 = 33 # Input Pin

GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)

sendCount = 0

pil_img_fanon = Image.open("assets/fanon.png")
pil_img_fanoff = Image.open("assets/fanoff.png")

#pil_img_result = ''

def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')

def update_fanimage():  #changes indicator of fan image to change image if fan on/off
    if FanStatusIndicator == "On":
        return 'fanon.png'
    else:
        return 'fanoff.png'
def update_fanimage_path():  # changes path of image to be displayed if fan on/off
    if FanStatusIndicator == "On":
        return image_path_fanon
    else:
        return image_path_fanoff
def update_pilimage():  # changes pil path of image to be displayed if fan on/off
    if FanStatusIndicator == "On":
        return pil_img_fanon
    else:
        return pil_img_fanoff


app = Dash(external_stylesheets=[dbc.themes.SUPERHERO])
nav_menu= dbc.NavbarSimple(

    brand="PHASE02",
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
        scale={'start': -40, 'interval': 5},
        label="Temperature",
        showCurrentValue=True,
        units="C",
        color="red",
    ),
    html.H1('Fan Status'),
    html.Img(src=update_fanimage_path()),                          # passing the direct file path which will be changed by method
    html.Img(src=app.get_asset_url(update_fanimage())),    # set the asset url with the fan image propert
   #html.Img(src=dash.get_asset_url(FanImage))    Or with newer Dash v2.2.0
    html.Img(src=update_pilimage()),                             # using the pillow image variable
    html.Img(src=b64_image(update_fanimage_path())),  # using base64 to encode and decode the image file, again using path result if fan on/off),               
    
    dcc.Interval(
        id = 'humid-update',
        disabled=False,
        interval = 1*10000,  #lower than 3000 for humidity wouldn't show the humidity on the terminal
        n_intervals = 0
    ),
    dcc.Interval(
        id = 'temp-update',
        disabled=False,
        interval = 1*10000,   #lower than 5000 for temperature wouldn't show the temp on the terminal
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
        if (dht.temperature >= 27):
            sendEmail()
          
        return dht.temperature

def sendEmail():
        port = 587  # For starttls
        smtp_server = "smtp-mail.outlook.com"
        sender_email = "iotdashboard2022@outlook.com"
        receiver_email = "iotdashboard2022@outlook.com"
        password = 'iotpassword123'
        subject = "Subject: FAN CONTROL" 
        body = "Your home temperature is greater than 24. Do you wish to turn on the fan. Reply YES if so."
        message = subject + '\n\n' + body
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message) 

def update_fanstatus(FanStatusIndicator):  # WORKS AND TESTED.
    if GPIO.input(Motor1) and not GPIO.input(Motor2) and GPIO.input(Motor3):
        FanStatusIndicator = "On"
    else:
        FanStatusIndicator = "Off"
    return FanStatusIndicator

if __name__ == '__main__':
    app.run_server(debug=True)

        