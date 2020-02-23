from celery import Celery
from celery import task  

# Internal imports
from pythonsolar import start_processing

app = Celery('tasks', broker='redis://guest@localhost//')

@task
def start_solar():
    '''

    from tasks import start_solar
    start_solar.delay()

    '''
    print(f'Starting solar processing...')
    start_processing()
    return True