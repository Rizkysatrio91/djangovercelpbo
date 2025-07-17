import os

from django.core.wsgi import get_wsgi_application
# Hapus baris ini: from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_pendaftaran.settings')

handler = get_wsgi_application()
# Hapus baris ini: handler = WhiteNoise(handler, root=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'staticfiles'))