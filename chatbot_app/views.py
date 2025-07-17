from django.shortcuts import render
from django.http import JsonResponse
from django.views import View 
from django.views.generic import TemplateView 
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import uuid

# Impor model dari kedua aplikasi
from Tampilanutama_app.models import SiteConfiguration, MenuItem, TopBarConfig
from .models import ChatbotRule, KnowledgeBaseEntry, ChatSession, ChatMessage

# Impor fungsi dari gemini_client Anda
from .gemini_client import generate_response, construct_prompt_with_rules_and_kb

# ==============================================================================
# VIEW UNTUK MENAMPILKAN HALAMAN CHAT 
# ==============================================================================

class ChatInterfaceView(TemplateView):
    """
    Class-Based View untuk menampilkan halaman antarmuka chat.
    Menggantikan fungsi `chat_interface_view`.
    """
    template_name = 'chatbot_app/chat_interface.html'

    def get_context_data(self, **kwargs):
        """
        Fungsi ini digunakan untuk mengumpulkan semua data yang akan
        dikirim ke template, menggantikan logika di dalam FBV lama.
        """
        # Panggil implementasi dasar dulu untuk mendapatkan context
        context = super().get_context_data(**kwargs)

        # Tambahkan data kita ke dalam context
        context['site_config'] = SiteConfiguration.objects.first()
        context['top_bar'] = TopBarConfig.objects.first()
        context['menu_items'] = MenuItem.objects.filter(is_active=True).select_related('parent')
        
        return context

# ==============================================================================
# VIEW UNTUK MEMPROSES PESAN CHAT (API - CBV)
# ==============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(View):
    """
    Class-Based View untuk menangani logika API chatbot.
    Menggantikan fungsi `chat_api` dan semua helper function-nya.
    """

    def _get_active_rules(self):
        return ChatbotRule.objects.filter(is_active=True)

    def _get_active_knowledge_base(self):
        return KnowledgeBaseEntry.objects.filter(is_active=True)

    def _format_chat_history_for_gemini(self, chat_messages_queryset):
        history = []
        for msg in chat_messages_queryset:
            history.append({'role': msg.role, 'parts': [msg.message_content]})
        return history

    def _store_chat_message(self, session, role, content):
        ChatMessage.objects.create(session=session, role=role, message_content=content)

    def post(self, request, *args, **kwargs):
        """
        Method ini HANYA akan dijalankan untuk request POST,
        menggantikan blok 'if request.method == 'POST''.
        """
        try:
            data = json.loads(request.body)
            user_input = data.get('message')
            session_id = data.get('session_id')

            if not user_input:
                return JsonResponse({'error': 'Pesan tidak boleh kosong'}, status=400)

            # Logika session tetap sama
            if session_id:
                chat_session, created = ChatSession.objects.get_or_create(session_id=session_id)
            else:
                session_id = str(uuid.uuid4())
                chat_session = ChatSession.objects.create(session_id=session_id)

            # Memanggil method internal untuk menyimpan pesan
            self._store_chat_message(chat_session, 'user', user_input)

            db_chat_history = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')
            
            # Logika untuk Gemini tetap sama persis
            history_for_gemini_call = self._format_chat_history_for_gemini(list(db_chat_history)[:-1])
            active_rules = self._get_active_rules()
            active_kb = self._get_active_knowledge_base()
            
            final_prompt_for_gemini = construct_prompt_with_rules_and_kb(user_input, active_rules, active_kb)

            bot_response_text, _ = generate_response(
                prompt_text=final_prompt_for_gemini,
                chat_history=history_for_gemini_call
            )

            # Menyimpan respons dari bot
            self._store_chat_message(chat_session, 'model', bot_response_text)

            return JsonResponse({
                'message': bot_response_text,
                'session_id': session_id,
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON tidak valid'}, status=400)
        except Exception as e:
            print(f"Error di ChatAPIView: {e}") # Diperbarui untuk mencerminkan nama class
            return JsonResponse({'error': 'Terjadi kesalahan internal pada server.'}, status=500)

