"""
WSGI configuration for renting_project.

Exposes the WSGI callable as a module-level variable named 'application'.

See https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/ for details.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'renting_project.settings')

application = get_wsgi_application()
