import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polyvoice.settings')

app = Celery('polyvoice')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()