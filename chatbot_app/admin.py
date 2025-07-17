from django.contrib import admin

# Register your models here.
from .models import ChatbotRule, KnowledgeBaseEntry, ChatSession, ChatMessage

@admin.register(ChatbotRule)
class ChatbotRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic', 'allowed', 'is_active')
    list_filter = ('allowed', 'is_active')
    search_fields = ('name', 'topic', 'description')
    list_editable = ('allowed', 'is_active') # Memungkinkan edit langsung dari list view

@admin.register(KnowledgeBaseEntry)
class KnowledgeBaseEntryAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'information_snippet', 'last_updated', 'is_active')
    search_fields = ('keyword', 'information')
    list_filter = ('is_active',)
    list_editable = ('is_active',)

    def information_snippet(self, obj):
        return obj.information[:75] + '...' if len(obj.information) > 75 else obj.information
    information_snippet.short_description = 'Potongan Informasi'

class ChatMessageInline(admin.TabularInline): # Atau admin.StackedInline
    model = ChatMessage
    extra = 0 # Jumlah form kosong yang ditampilkan
    readonly_fields = ('role', 'message_content', 'timestamp') # Pesan tidak boleh diubah dari admin session

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'created_at', 'message_count')
    readonly_fields = ('session_id', 'created_at')
    inlines = [ChatMessageInline] # Menampilkan pesan terkait langsung di detail sesi

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Jumlah Pesan'

