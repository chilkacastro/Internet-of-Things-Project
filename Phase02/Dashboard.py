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
FanImage = '' # set fan image name.


image_path_fanon = 'assets/fanon.png'
image_path_fanoff = 'assets/fanoff.jpg'

path_result = ''

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
Motor1 = 35 # Enable Pin
Motor2 = 37 # Input Pin
Motor3 = 33 # Input Pin

GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)

sendCount = 0

pil_img = Image.open("assets/fanon.png")
pil_img = Image.open("assets/fanoff.png")

def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')


def update_fanstatus(FanStatusIndicator):  # WORKS MOVED UP!
    if GPIO.input(Motor1) and not GPIO.input(Motor2) and GPIO.input(Motor3):
        FanStatusIndicator = "On"
    else:
        FanStatusIndicator = "Off"
    return FanStatusIndicator
def update_fanimage(FanImage):  #changes indicator of fan image to change image if fan on/off
    if FanStatusIndicator == "On":
        FanImage = 'fanon.png'
    else:
        FanImage = 'fanoff.png'
    return FanImage
def update_fanimage_path(path_result):  # changes path of image to be displayed if fan on/off
    if FanStatusIndicator == "On":
        path_result = image_path_fanon
    else:
        path_result = image_path_fanoff
    return path_result

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
    html.Img(src=path_result),                          # passing the direct file path which will be changed by method
    html.Img(src=app.get_asset_url(FanImage)),    # set the asset url with the fan image propert
   #html.Img(src=dash.get_asset_url('my-image.png'))    Or with newer Dash v2.2.0
    html.Img(src=pil_img),                             # using the pillow image variable
    html.Img(src=b64_image(path_result)# using base64 to encode and decode the image file, again using path result if fan on/off
    ),               
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




if __name__ == '__main__':
    app.run_server(debug=True)

        