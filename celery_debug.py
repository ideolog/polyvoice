from celery import shared_task

@shared_task
def debug_task(x, y):
    print(f"Debug task running: {x} + {y} = {x + y}")
    return x + y
