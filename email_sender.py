import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject: str, html_body: str) -> None:
    try:
        sender = os.getenv("EMAIL_USER")
        app_password = os.getenv("EMAIL_APP_PASSWORD")
        recipient = os.getenv("RECEIVER_MAIL")
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient
        msg.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_password)
            server.sendmail(sender, recipient, msg.as_string())            
    except:
        print("Error Occured while sending email at email_sender.py")