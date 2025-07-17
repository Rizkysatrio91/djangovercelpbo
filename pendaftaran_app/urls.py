# pendaftaran_app/urls.py
from django.urls import path
# Impor nama-nama Class dari views
from .views import BerandaView, UnggahBerkasView, DetailBerkasView

app_name = 'pendaftaran_app' # <--- TAMBAHKAN BARIS INI

urlpatterns = [
    # Gunakan .as_view() untuk setiap class-based view
    path('', BerandaView.as_view(), name='beranda'),
    path('unggah/', UnggahBerkasView.as_view(), name='unggah_berkas'),
    path('berkas/<int:pk>/', DetailBerkasView.as_view(), name='detail_berkas'),
]