# https://github.com/wsvincent/django-microframework

import os

from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
os.environ.setdefault("DJANGO_RUNSERVER_HIDE_WARNING", "true")

if __name__ == "__main__":
    execute_from_command_line()
else:
    application = get_wsgi_application()