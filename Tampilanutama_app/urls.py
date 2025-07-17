from django.urls import path
# Impor nama Class view yang sudah dibuat
from .views import HomePageView, NewsDetailView, VisiMisiPageView, OrganizationStructurePageView, HistoryPageView

app_name = 'tampilan_utama_app' # Memberi namespace pada URL app ini

urlpatterns = [
    # Gunakan .as_view() untuk mengubah Class menjadi fungsi view yang bisa dipanggil
    path('', HomePageView.as_view(), name='home'),
    path('berita/<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
    path('visi-misi/', VisiMisiPageView.as_view(), name='visi_misi'),
    path('struktur-organisasi/', OrganizationStructurePageView.as_view(), name='struktur_organisasi'),
    path('sejarah/', HistoryPageView.as_view(), name='sejarah'),
    # Tambahkan path lain di sini jika ada view tambahan.
]
