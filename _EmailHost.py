from smtplib import *
from email import *
from email.mime.text import MIMEText
from _utils import *

class VIEmailHost:
    Client: SMTP_SSL

    def __init__(this):
        PRTS.EmailHost = this
        this.Client = SMTP_SSL(PRTS.EmailHostAddress)
        this.Client.connect(PRTS.EmailHostAddress, 465)
        this.Client.login(PRTS.EmailAccount, PRTS.EmailPassword)

    def testConnect(this):
        try:
            status = this.Client.noop()[0]
        except:
            status = -1
        return True if status == 250 else False
    
    def sendEmail(this, toAddr: str, subject: str, content: str):
        message = MIMEText(content, "plain", "utf-8")
        message["From"] = PRTS.EmailAccount
        message["To"] = toAddr
        message["Subject"] = PRTS.EmailTitle + " - " + subject
        if not this.testConnect():
            this.Client = SMTP_SSL(PRTS.EmailHostAddress)
            this.Client.connect(PRTS.EmailHostAddress, 465)
            this.Client.login(PRTS.EmailAccount, PRTS.EmailPassword)
        this.Client.sendmail(PRTS.EmailAccount, toAddr, message.as_string())

    def __del__(this):
        this.Client.quit()

