from celery import Celery
from celery import task  

# Internal imports
from pythonsolar import start_processing, send_command_to_inverter
from solar.struct_logger import StructLogger

the_logger = StructLogger()

app = Celery('tasks', broker='redis://guest@localhost//')

@task
def start_solar():
    '''
    Usage:
    from tasks import start_solar
    start_solar.delay()

    '''
    the_logger.info(f'Starting solar processing...')
    start_processing()
    return True

@task
def send_command(command,data):
    '''
    Usage:
    from tasks import send_command
    send_command.delay()

    '''
    send_command_to_inverter(command, data)