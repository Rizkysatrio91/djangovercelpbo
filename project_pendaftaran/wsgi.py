import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_pendaftaran.settings')

# Ubah 'application' menjadi 'handler' di baris ini
handler = get_wsgi_application()
# Ubah 'application' menjadi 'handler' di baris ini
handler = WhiteNoise(handler, root=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'staticfiles'))