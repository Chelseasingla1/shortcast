from app import create_app

app, celery = create_app()
from app.views.emailservice.emailservice import send_verification_email
if __name__ == '__main__':
    celery.start()

# celery -A celerysetup.celery worker --loglevel=info
