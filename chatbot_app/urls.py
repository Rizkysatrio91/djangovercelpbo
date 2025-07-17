# chatbot_app/urls.py
from django.urls import path
# 1. UBAH CARA IMPORT: Impor nama Class-nya secara langsung
from .views import ChatInterfaceView, ChatAPIView

app_name = 'chatbot_app'

urlpatterns = [
    # JIKA SESEORANG MENGAKSES /chatbot/ ATAU /chatbot/chat/ MEREKA AKAN MELIHAT HALAMAN CHAT
    # 2. GUNAKAN .as_view() untuk mengubah Class menjadi fungsi view yang bisa dipanggil
    path('', ChatInterfaceView.as_view(), name='chatbot_home'),
    path('chat/', ChatInterfaceView.as_view(), name='chat_interface_page'),
    
    # INI ADALAH ENDPOINT KHUSUS UNTUK API YANG DIPANGGIL JAVASCRIPT
    # Gunakan .as_view() untuk API juga
    path('api/chat/', ChatAPIView.as_view(), name='chat_api'),
]
