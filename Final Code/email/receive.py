import email
import imaplib
import getpass
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import RPi.GPIO as GPIO
import time
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
#DC motor pins(USING BOARD/Physical addressing)
Motor1 = 35 # Enable Pin
Motor2 = 37 # Input Pin
Motor3 = 33 # Input Pin

GPIO.setup(Motor1,GPIO.OUT)
GPIO.output(Motor1,GPIO.LOW)

EMAIL = 'iotdashboardother2022@outlook.com'
PASSWORD = 'iotpassword123'

SERVER = 'outlook.office365.com'

# physical fan(DC motor)
def activateFan():
    print("pass here")
    GPIO.setup(Motor1,GPIO.OUT)
    GPIO.setup(Motor2,GPIO.OUT)
    GPIO.setup(Motor3,GPIO.OUT)
    
    GPIO.output(Motor1,GPIO.HIGH)
    GPIO.output(Motor2,GPIO.LOW)
    GPIO.output(Motor3,GPIO.HIGH)
    
message = ''
mail_content = ''
replybody = ''
replylist = [];
#SETUP PERMANENT EMAIL AND HARD CODED PASSWORD
while True:

    mail = imaplib.IMAP4_SSL(SERVER)
    time.sleep(5)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')
    #SUBJECT is set to fan control so it detects that its a reply probably
    status, data = mail.search(None,'(FROM "iotdashboardother2022@outlook.com" SUBJECT "FAN CONTROL" UNSEEN)')
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
                            replylist.append(replybody)
                            print(replylist)
                            # Uncomment these print lines just check values for testing purpose
#                             print(replybody)
#                             print(len(str(replybody)))
#                             print(replybody.__eq__("YES"))
#                             print(len(str(replybody)) == 3)
                            
                            # Makes sure only "YES" would activate the fan
                            if replybody.__eq__("YES") and len(str(replybody)) == 3 and replylist[0] == "YES":
                                activateFan()
                            if replylist[0] == "NO":
                                #status, data = mail.fetch(i, '(RFC822)')
                                status, data = mail.search(None,'(FROM "iotdashboardother2022@outlook.com" SUBJECT "FAN CONTROL" UNSEEN)')
                                for num in data[0].split():
                                    mail.store(num, '+FLAGS', '\\Deleted')
                                mail.expunge()
                                
                                
                            
                            replylist.clear()
                            #print(replylist)
                            
                else:
                    #This part gets called when the email is not a reply (left for testing)
                    mail_content = message.get_payload()
                    print(f'From: {mail_from}')
                    print(f'Subject: {mail_subject}')
                    print(f'Content: {mail_content}')
      

