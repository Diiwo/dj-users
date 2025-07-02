import os

from celery import Celery

# Correr celery:
# celery -A demo worker -l info --pool=solo
# celery -A demo beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler # noqa

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
app = Celery('demo', broker='pyamqp://guest@localhost//')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
