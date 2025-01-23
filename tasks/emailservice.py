import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPException, SMTPAuthenticationError
import logging
from tasks import celery
import re
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def is_valid_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email)

@celery.task(bind=True, max_retries=3)
def send_verification_email(self,email, token):
    try:

        if not is_valid_email(email):
            raise ValueError(f"Invalid email address: {email}")

        sender_email = os.environ.get("EMAIL_ADRR")
        password = os.environ.get("EMAIL_PASS")

        if not sender_email or not password:
            raise ValueError("Email credentials are not properly configured in the environment variables.")

        # Email content
        message = MIMEMultipart("alternative")
        message["Subject"] = "Email Verification"
        message["From"] = sender_email
        message["To"] = email

        subscribe_link = f"https://example.com/subscribe?token={token}"
        unsubscribe_link = f"https://example.com/unsubscribe?token={token}"

        text = "We’re thrilled to have you on board! By subscribing, you’ll receive exclusive content."
        html = f"""
        <html>
        <body>
            <p>{text}</p>
            <a href="{subscribe_link}">Subscribe Now</a><br>
            <a href="{unsubscribe_link}">Unsubscribe</a>
        </body>
        </html>
        """
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        # Sending email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, email, message.as_string())
        logger.info("Email sent successfully")
        return f"Email sent to {email}"

    except (SMTPAuthenticationError, SMTPException, ValueError) as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise self.retry(exc=e,countdown =60)  # Optionally retry the task
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise self.retry(exc=e,countdown =60)  # Retry for other exceptions
