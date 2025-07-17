from django.db import models

# Create your models here.
class ChatbotRule(models.Model):
    """
    Model untuk mendefinisikan aturan batasan untuk chatbot.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Nama singkat untuk aturan ini (misalnya, 'Tolak Topik Politik')")
    topic = models.CharField(max_length=255, help_text="Topik atau kata kunci yang diatur (misalnya, 'politik', 'harga saham X')")
    allowed = models.BooleanField(default=True, help_text="Centang jika chatbot BOLEH membahas topik ini. Kosongkan jika TIDAK BOLEH.")
    description = models.TextField(help_text="Deskripsi detail tentang aturan ini dan bagaimana chatbot harus merespons (misalnya, 'Jika ditanya tentang politik, jawab bahwa Anda tidak dapat membahas topik tersebut.')")
    is_active = models.BooleanField(default=True, help_text="Aktifkan atau nonaktifkan aturan ini.")

    def __str__(self):
        return f"{self.name} - {'BOLEH' if self.allowed else 'TIDAK BOLEH'} membahas '{self.topic}'"

    class Meta:
        verbose_name = "Aturan Chatbot"
        verbose_name_plural = "Aturan Chatbot"

class KnowledgeBaseEntry(models.Model):
    """
    Model untuk menyimpan entri basis pengetahuan untuk chatbot.
    """
    keyword = models.CharField(max_length=100, unique=True, help_text="Kata kunci utama untuk entri ini (misalnya, 'Jam Operasional', 'Harga Produk A')")
    information = models.TextField(help_text="Informasi detail yang harus diketahui chatbot terkait kata kunci ini.")
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Aktifkan atau nonaktifkan entri basis pengetahuan ini.")

    def __str__(self):
        return self.keyword

    class Meta:
        verbose_name = "Entri Basis Pengetahuan"
        verbose_name_plural = "Entri Basis Pengetahuan"

class ChatSession(models.Model):
    """
    Model untuk menyimpan histori percakapan.
    """
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.session_id

class ChatMessage(models.Model):
    """
    Model untuk menyimpan setiap pesan dalam sesi chat.
    Struktur history Gemini adalah list of dictionaries: {'role': 'user'/'model', 'parts': ['text']}
    """
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=10) # 'user' atau 'model'
    message_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} ({self.session.session_id}): {self.message_content[:50]}"

    class Meta:
        ordering = ['timestamp']