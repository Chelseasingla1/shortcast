import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import celery
from dotenv import load_dotenv
from smtplib import SMTPException, SMTPAuthenticationError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Load environment variables
load_dotenv()


# Send verification email
@celery.task
def send_verification_email(email, token):
    try:
        # Retrieve email credentials from environment variables
        sender_email = os.environ.get("EMAIL_ADRR")
        receiver_email = email
        password = os.environ.get("EMAIL_PASS")

        if not sender_email or not password:
            raise ValueError("Email credentials are not properly configured in the environment variables.")

        # Create the email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Email Verification"
        message["From"] = sender_email
        message["To"] = email

        subscribe_link = f"https://example.com/subscribe?token={token}"
        unsubscribe_link = f"https://example.com/unsubscribe?token={token}"

        text = ("We’re thrilled to have you on board! By subscribing, you’ll receive the latest news, updates, "
                "and exclusive content directly to your inbox.")

        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    width: 100%;
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .header img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px 8px 0 0;
                }}
                h1 {{
                    color: #333333;
                    text-align: center;
                }}
                p {{
                    font-size: 16px;
                    color: #555555;
                    line-height: 1.6;
                    text-align: center;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 20px;
                    background-color: #28a745;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    text-align: center;
                    font-size: 16px;
                    margin: 20px auto;
                    display: block;
                }}
                .unsubscribe {{
                    display: inline-block;
                    padding: 12px 20px;
                    background-color: #dc3545;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    text-align: center;
                    font-size: 16px;
                    margin: 20px auto;
                    display: block;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://via.placeholder.com/600x200?text=Shortcast+Subscription" alt="Shortcast Branding">
                </div>
                <h1>Subscribe to Our Updates</h1>
                <p>{text}</p>
                <a href="{subscribe_link}" class="btn">Subscribe Now</a>
                <p>Changed your mind? You can unsubscribe at any time by clicking the button below:</p>
                <a href="{unsubscribe_link}" class="unsubscribe">Unsubscribe</a>
            </div>
        </body>
        </html>
        """

        # Attach plain text and HTML parts to the email
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        # Send the email using an SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        logger.info('Email sent successfully')
        print("Email sent successfully")

    except SMTPAuthenticationError:
        logger.error('Error: Authentication failed. Check your email addreass and password')
        print("Error: Authentication failed. Check your email address and password.")
    except SMTPException as e:
        logger.error('SMTP error occurred')
        print(f"SMTP error occurred: {e}")
    except ValueError as e:
        logger.error(f'Configuration error: {e}')
        print(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f'An unexpected error occurred: {e}')
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    send_verification_email('edeanijerry@gmail.com', 'sample_token')
