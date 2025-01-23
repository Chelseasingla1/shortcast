from tasks import celery
@celery.task(bind=True)
def add_numbers(self,a, b):
    self.request.args = (a, b)
    print(self.request.args)
    return a / b
