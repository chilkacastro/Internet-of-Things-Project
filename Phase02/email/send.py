import smtplib, ssl, getpass



#code to send the email
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
        

sendEmail()
#put in an infinite loop or something, find a way to feed the temperature data to this method
#if ("THE TEMPERATURE IS ABOVE 24"):
#   sendEmail()


