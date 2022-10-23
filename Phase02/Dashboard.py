from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import RPi.GPIO as GPIO
import time
from time import sleep
import Freenove_DHT as DHT
import smtplib, ssl, getpass, imaplib, email

EMAIL = 'iotdashboard2022@outlook.com'
PASSWORD = 'iotpassword123'

SERVER = 'outlook.office365.com'

DHTPin = 40 #equivalent to GPIO21
FanPin = 22  #just a pin for the fan
FanStatusIndicator = "Off"  #Indicator for fan

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
#DC motor pins(USING BOARD/Physical addressing)
Motor1 = 35 # Enable Pin
Motor2 = 37 # Input Pin
Motor3 = 33 # Input Pin

GPIO.setup(Motor1,GPIO.OUT)
GPIO.output(Motor1,GPIO.LOW)

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
        scale={'start': -40, 'interval': 5},
        label="Temperature",
        showCurrentValue=True,
        units="C",
        color="red",
    ),
    daq.Indicator(  #indicator for fan, has like a light that should switch color if true/false and label
        id='my-fan-1',
        label="Fan Status: " + FanStatusIndicator
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
        interval = 1*10000,   #lower than 5000 for temperature wouldn't show the temp on the terminal
        n_intervals = 0
    ),
    dcc.Interval(   # interval for fan to update it regularly (not tested)
        id = 'fan-update',
        disabled=False,
        interval = 1*5000,  #not sure of the value for interval for fan if needed so just copy pasted same batch of code
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
        if (dht.temperature >= 23):
             sendEmail()
             receiveEmail()
#             
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
 

def receiveEmail():
    #SETUP PERMANENT EMAIL AND HARD CODED PASSWORD
    while True:
        mail = imaplib.IMAP4_SSL(SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select('inbox')
        #SUBJECT is set to fan control so it detects that its a reply probably
        status, data = mail.search(None,'(FROM "iotdashboard2022@outlook.com" SUBJECT "FAN CONTROL" UNSEEN)')
        #status, data = mail.search(None,'(SUBJECT "FAN CONTROL" UNSEEN)')

        #most of this is useless stuff, check the comments 
        mail_ids = []
        for block in data:
            mail_ids += block.split()
        
        for i in mail_ids:
            status, data = mail.fetch(i, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])
                    mail_from = message['from']
                    mail_subject = message['subject']
                    if message.is_multipart():
                        mail_content = ''

                        for part in message.get_payload():
                            #this is where the code activates when we reply YES or anything else
                            if part.get_content_type() == 'text/plain':
                                mail_content += part.get_payload()
                               
                                #print(f'MAIL CONTENT: {mail_content}')
                                replybody = str(mail_content.split('\n', 1)[0])
                                print(f'IF THIS IS NOT YES WHEN YOU REPLY TO THE ORIGINAL EMAIL ITS BAD: {replybody}')
                                replybody = (replybody.upper()).strip()
                                # Uncomment these print lines just check values for testing purpose
    #                             print(replybody)
    #                             print(len(str(replybody)))
    #                             print(replybody.__eq__("YES"))
    #                             print(len(str(replybody)) == 3)
                                
                                # Makes sure only "YES" would activate the fan
                                if replybody.__eq__("YES") and len(str(replybody)) == 3:
                                    activateFan()
                                
                    else:
                        #This part gets called when the email is not a reply (left for testing)
                        mail_content = message.get_payload()
                        print(f'From: {mail_from}')
                        print(f'Subject: {mail_subject}')
                        print(f'Content: {mail_content}')          


# physical fan(DC motor)
def activateFan():
    print("pass here")
    GPIO.setup(Motor1,GPIO.OUT)
    GPIO.setup(Motor2,GPIO.OUT)
    GPIO.setup(Motor3,GPIO.OUT)
    
    GPIO.output(Motor1,GPIO.HIGH)
    GPIO.output(Motor2,GPIO.LOW)
    GPIO.output(Motor3,GPIO.HIGH)
    
def deactivateFan():
    GPIO.output(Motor1,GPIO.LOW)
    GPIO.cleanup()

@app.callback(Output('my-fan-1', 'value'), Input('fan-update', 'n_intervals'))      #  Fan here (CODE NOT TESTED), uses update_fanstatus method to say on/off, returns true if output is high which means the indicator will switch colors, true/false will make the indicator have different colors
def update_output(value):
    update_fanstatus(FanStatusIndicator)
    return True if GPIO.input(FanPin) else False

def update_fanstatus(FanStatusIndicator):  # just change text on indicator if gpio high or not... not tested
    if GPIO.input(FanPin):
        FanStatusIndicator = "On"
    else:
        FanStatusIndicator = "Off"
    return FanStatusIndicator

if __name__ == '__main__':
    app.run_server(debug=True)

        