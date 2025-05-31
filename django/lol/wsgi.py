import os
from django.core.wsgi import get_wsgi_application

# Ensure the correct settings module is loaded
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lol.settings")



application = get_wsgi_application()
