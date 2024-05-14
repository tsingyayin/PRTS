from smtplib import *
from email import *
from email.mime.text import MIMEText
from ._Utils import *
from ._Config import *
class PRTSEmailHost:
    Client: SMTP_SSL
    Enable: bool = False
    def __init__(this):
        if PRTSConfig.Instance["EmailHost"]["HostAddress"] != "":
            this.Enable = True
            this.Client = SMTP_SSL(PRTSConfig.Instance["EmailHost"]["HostAddress"])
            this.Client.connect(PRTSConfig.Instance["EmailHost"]["HostAddress"], PRTSConfig.Instance["EmailHost"]["HostPort"])
            this.Client.login(PRTSConfig.Instance["EmailHost"]["Account"], PRTSConfig.Instance["EmailHost"]["Password"])
        else:
            print("PRTS can not send email because the host address is empty.")

    def testConnect(this):
        if not this.Enable:
            return False
        try:
            status = this.Client.noop()[0]
        except:
            status = -1
        return True if status == 250 else False
    
    def sendEmail(this, toAddr: str, subject: str, content: str):
        if not this.Enable:
            return
        if not this.testConnect():
            this.Client = SMTP_SSL(PRTSConfig.Instance["EmailHost"]["HostAddress"])
            this.Client.connect(PRTSConfig.Instance["EmailHost"]["HostAddress"], 
                                PRTSConfig.Instance["EmailHost"]["HostPort"])
            this.Client.login(PRTSConfig.Instance["EmailHost"]["Account"], 
                                PRTSConfig.Instance["EmailHost"]["Password"])
        message = MIMEText(content, "plain", "utf-8")
        message["From"] = PRTSConfig.Instance["EmailHost"]["Account"]
        message["To"] = toAddr
        message["Subject"] = PRTSConfig.Instance["EmailHost"]["Title"] + " - " + subject

    def __del__(this):
        if this.Enable:
            this.Client.quit()

