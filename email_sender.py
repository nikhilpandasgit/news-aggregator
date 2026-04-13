import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject: str, html_body: str) -> None:
    sender = os.getenv("EMAIL_USER")
    app_password = os.getenv("EMAIL_APP_PASSWORD")
    recipient = os.getenv("RECEIVER_MAIL")
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html"))
        
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_password)
            server.sendmail(sender, recipient, msg.as_string())    

    except smtplib.SMTPAuthenticationError as exc:
        raise RuntimeError("Gmail authentication failed — check EMAIL_USER and EMAIL_APP_PASSWORD.") from exc
    except smtplib.SMTPException as exc:
        raise RuntimeError(f"SMTP error while sending email: {exc}") from exc
    except OSError as exc:
        raise RuntimeError(f"Network error while connecting to Gmail: {exc}") from exc