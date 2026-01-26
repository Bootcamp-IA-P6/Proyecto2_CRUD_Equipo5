"""
ASGI configuration for renting_project.

Exposes the ASGI callable as a module-level variable named 'application'.

See https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/ for details.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'renting_project.settings')

application = get_asgi_application()
