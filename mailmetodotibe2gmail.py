import smtplib
####invio mail
server = smtplib.SMTP(host='smtp.gmail.com', port=587)
server.ehlo()
server.starttls()
#log
server.login('ccp.project.22@gmail.com', 'claudiocomputing1!')
#create msg
subject = 'This is my subject'
body = 'This is the message in the email'
###
message = f'Subject: {subject}\n\n{body}'
###
server.sendmail('ccp.project.22@gmail.com', 'ccp.project.22@gmail.com', message)
server.quit()
print("ok")
####