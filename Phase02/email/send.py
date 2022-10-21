import smtplib, ssl, getpass

port = 587  # For starttls
smtp_server = "smtp-mail.outlook.com"
sender_email = "nicholasciobanu@outlook.com"
receiver_email = "nicholasciobanu@outlook.com"
password = getpass.getpass('Password:')
print('Subject:')
subject = "Subject: " + input()
print('Body:')
body = input()
message = subject + '\n\n' + body

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)