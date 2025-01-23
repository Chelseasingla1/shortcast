from tasks import celery
@celery.task
def add_numbers(a, b):
    return a / b
