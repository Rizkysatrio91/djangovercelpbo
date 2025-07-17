from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # URL root sekarang mengarah ke Tampilanutama_app
    path('', include('Tampilanutama_app.urls')), 
    path('admin/', admin.site.urls),
    path('pendaftaran/', include('pendaftaran_app.urls')), # Pastikan ini ada
    path('chatbot/', include('chatbot_app.urls')),
    path('tinymce/', include('tinymce.urls')),
]

# Konfigurasi untuk melayani file statis dan media selama pengembangan
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)