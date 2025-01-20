import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPException, SMTPAuthenticationError
from celery.signals import task_success, task_failure
from app import create_app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
app, celery = create_app()


@celery.task(bind=True, max_retries=3,name="app.emailservice.emailservice.send_verification_email")
def send_verification_email(self, email, token):
    try:
        sender_email = os.environ.get("EMAIL_ADDR")
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
        raise self.retry(exc=e)  # Optionally retry the task
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise self.retry(exc=e)  # Retry for other exceptions


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """
    Called when a task succeeds.
    """
    logger.info(f"Task succeeded: {sender.name}, result: {result}")


@task_failure.connect
def task_failure_handler(sender=None, exception=None, **kwargs):
    """
    Called when a task fails.
    """
    logger.error(f"Task failed: {sender.name}, exception: {exception}")
