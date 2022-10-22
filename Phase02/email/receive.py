import email
import imaplib
import getpass
EMAIL = 'iotdashboard2022@outlook.com'
PASSWORD = 'iotpassword123'

SERVER = 'outlook.office365.com'

def activateFan():
    print("ACTIVATE THE FAN")

message = ''
mail_content = ''
replybody = ''
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
                            #WHY IS THE IF NOT WORKING!!!! STRAIGHT BUGGGGIIN
                            if replybody == "YES":
                                activateFan()
                            
                else:
                    #This part gets called when the email is not a reply (left for testing)
                    mail_content = message.get_payload()
                    print(f'From: {mail_from}')
                    print(f'Subject: {mail_subject}')
                    print(f'Content: {mail_content}')
                    



   
                    


