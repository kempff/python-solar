from celery import Celery

app = Celery('tasks', broker='redis://guest@localhost//')

@app.task
def add(x, y):
    '''
    Test task, call from another module with:

    from tasks import add
    add.delay(4, 40)
    
    '''
    print(f'Adding {x} and {y}...')
    return x + y