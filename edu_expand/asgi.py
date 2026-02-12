"""
ASGI config for EDU-EXPAND CRM project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_expand.settings')

application = get_asgi_application()
