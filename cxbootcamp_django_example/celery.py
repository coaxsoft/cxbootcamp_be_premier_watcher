from __future__ import absolute_import, unicode_literals

import os

import celery
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cxbootcamp_django_example.settings')


@celery.signals.setup_logging.connect
def on_celery_setup_logging(**kwargs):
    pass


app = Celery('cxbootcamp_django_example')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
