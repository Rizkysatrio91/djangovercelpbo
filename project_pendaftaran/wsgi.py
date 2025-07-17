import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise # <--- TAMBAHAN INI

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_pendaftaran.settings')

application = get_wsgi_application()
# <--- TAMBAHAN BARIS INI UNTUK WHITENOISE
application = WhiteNoise(application, root=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'staticfiles'))