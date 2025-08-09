import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "online_shop.settings")

project = Celery('online_shop')
project.config_from_object('django.conf:settings', namespace='CELERY')
project.autodiscover_tasks()