from celerysetup import make_celery
from app import app

# Create a Celery instance
celery = make_celery(app)

# Import all task modules to ensure tasks are registered

from tasks import testlongtask,emailservice,transcriptionservice
import signals.task_signals

'''
to run celery
celery -A tasks.celery worker --loglevel=info

'''