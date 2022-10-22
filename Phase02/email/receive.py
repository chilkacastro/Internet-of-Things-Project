import email
import imaplib
import getpass
EMAIL = 'nicholasciobanu@outlook.com'
PASSWORD = getpass.getpass('Password:')

SERVER = 'outlook.office365.com'

def activateFan():
    print("ACTIVATE THE FAN")

message = ''
mail_content = ''
#SETUP PERMANENT EMAIL AND HARD CODED PASSWORD
while True:
    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')
    
    status, data = mail.search(None,'(FROM "nicholasciobanu@outlook.com" SUBJECT "FAN CONTROL" UNSEEN)')
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
                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            #THE CODE SHOULD ALWAYS END UP HERE, CAN'T CONVERT mail_content to string
                            mail_content += part.as_string()
                            #mail_content += part.get_payload()
                            print(f'{mail_content}')
                else:
                    mail_content = message.get_payload()
                    print(f'mail_content is defined')
                    
    if mail_content == "YES" or message == "YES":
        activateFan()
        print(f'From: {mail_from}')
        print(f'Subject: {mail_subject}')
        print(f'Content: {mail_content}')
                    


