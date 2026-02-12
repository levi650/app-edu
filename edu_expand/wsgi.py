"""
WSGI config for EDU-EXPAND CRM project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_expand.settings')

application = get_wsgi_application()
