# pendaftaran_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
import json

from .models import BerkasPendaftaran, FilePDF, PasFoto, BasisPengetahuan, KonfigurasiUnggah

class FilePDFInline(admin.TabularInline):
    model = FilePDF
    extra = 1

class PasFotoInline(admin.TabularInline):
    model = PasFoto
    extra = 1

@admin.register(BerkasPendaftaran)
class BerkasPendaftaranAdmin(admin.ModelAdmin):
    list_display = ('nama_pendaftar', 'email_pendaftar', 'tanggal_unggah', 'display_status_ai_simple', 'view_detail_link')
    
    readonly_fields = ('tanggal_unggah', 'display_full_hasil_seleksi',)
    inlines = [FilePDFInline, PasFotoInline]

    def display_status_ai_simple(self, obj):
        if obj.hasil_seleksi and isinstance(obj.hasil_seleksi, dict) and 'overall_status' in obj.hasil_seleksi:
            status = obj.hasil_seleksi['overall_status']
            if status == "Lengkap":
                return format_html('<span style="color: green; font-weight: bold;">Lengkap</span>')
            else:
                return format_html('<span style="color: red; font-weight: bold;">Tidak Lengkap</span>')
        return "Belum dianalisis"
    display_status_ai_simple.short_description = "Status AI"
    # Menghapus admin_order_field karena struktur hasil_seleksi berubah

    def view_detail_link(self, obj):
        return format_html('<a href="{}">Lihat Detail</a>', obj.get_absolute_url())
    view_detail_link.short_description = "Detail Berkas"

    def display_full_hasil_seleksi(self, obj):
        if obj.hasil_seleksi:
            data = obj.hasil_seleksi
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return format_html('<p style="color: red;">Format JSON tidak valid atau data lama.</p>')

            return format_html('<pre style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; overflow-x: auto;"><code>{}</code></pre>', json.dumps(data, indent=2, ensure_ascii=False))
        return "Belum dianalisis"
    display_full_hasil_seleksi.short_description = "Hasil Analisis AI Lengkap"

    fieldsets = (
        (None, {
            'fields': ('nama_pendaftar', 'email_pendaftar',)
        }),
        ('Informasi Waktu', {
            'fields': ('tanggal_unggah',),
            'classes': ('collapse',),
        }),
        ('Hasil Seleksi AI', {
            'fields': ('display_full_hasil_seleksi',),
            'description': 'Hasil analisis AI secara rinci untuk semua dokumen yang diunggah.'
        }),
    )

@admin.register(BasisPengetahuan) # Nama kelas ini tidak berubah, hanya isinya
class BasisPengetahuanAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'field_name', 'is_required', 'aktif')
    list_filter = ('is_required', 'aktif',)
    search_fields = ('display_name', 'field_name', 'description')

@admin.register(KonfigurasiUnggah)
class KonfigurasiUnggahAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return KonfigurasiUnggah.objects.count() == 0

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(FilePDF)
admin.site.register(PasFoto)