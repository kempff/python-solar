from celery import Celery
from celery import task  

# Internal imports
from pythonsolar import PythonSolar
from solar.struct_logger import StructLogger

solar_processor = PythonSolar()
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
    solar_processor.start_processing()
    return True

@task
def send_command(command,data):
    '''
    Usage:
    from tasks import send_command
    send_command.delay()

    '''
    the_logger.info(f'Sending command {command}')
    solar_processor.send_command_to_inverter(command, data)
