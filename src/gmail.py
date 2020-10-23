import smtplib
from email.mime.text import MIMEText

class Gmail:
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.sent_from = user


    def send_mail(self, recipients, subject, body):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.sent_from
        if not isinstance(recipients, list):
            msg['To'] = recipients
        else:
            msg['To'] = ", ".join(recipients)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(self.user, self.password)
        server.sendmail(self.sent_from, recipients, msg.as_string())
        server.close()

        print('Email sent!')
    