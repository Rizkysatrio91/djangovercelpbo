# Tampilanutama_app/admin.py

from django.contrib import admin
from .models import TopBarConfig, SiteConfiguration, MenuItem, JumbotronSlide, KetuaInfo, NewsArticle, VisiMisi, OrganizationMember, HistoryPage
from django.db import models 
from django.utils.html import format_html

#TOP Bar
@admin.register(TopBarConfig)
class TopBarConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'phone_number', 'email')
    # Membuat fieldset agar tampilan di admin lebih rapi
    fieldsets = (
        ('Informasi Kontak', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Tautan Media Sosial', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'youtube_url')
        }),
    )

    # Mencegah penambahan objek baru dari halaman admin jika sudah ada satu
    def has_add_permission(self, request):
        return not TopBarConfig.objects.exists()

# Inline untuk MenuItem jika ingin diatur dari SiteConfiguration (opsional)
class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ('title', 'url_name', 'custom_url', 'order', 'is_active', 'parent') # Tidak menampilkan parent di inline ini
    ordering = ('order',)

# --- PERUBAHAN DIMULAI DI SINI ---
@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    # 'footer_text' dihapus dan diganti dengan field yang lebih relevan
    list_display = ('site_name', 'total_kader_count', 'footer_email', 'site_logo_preview') 
    
    # 'fields' diganti dengan 'fieldsets' untuk tampilan admin yang lebih rapi
    # dan menggunakan field-field footer yang baru
    fieldsets = (
        ('Informasi Umum Situs', {
            'fields': ('site_name', 'site_logo', 'total_kader_count')
        }),
        ('Informasi Kontak di Footer', {
            'fields': ('footer_address', 'footer_email', 'footer_phone', 'footer_website')
        }),
        ('Teks Hak Cipta', {
            'fields': ('copyright_text',)
        }),
    )
    
    # inlines = [MenuItemInline] # Aktifkan jika ingin MenuItem diatur dari sini

    # Memastikan hanya ada satu instance dari model ini
    def has_add_permission(self, request):
        # Logika ini sudah benar, tidak perlu diubah
        return not SiteConfiguration.objects.exists() and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False # Tidak bisa dihapus
    
    def site_logo_preview(self, obj):
        if obj.site_logo:
            return format_html('<img src="{}" width="50" height="auto" />', obj.site_logo.url)
        return "(No Logo)"
    site_logo_preview.short_description = "Logo Preview"
# --- AKHIR PERUBAHAN ---

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'parent', 'get_target_url')
    list_filter = ('is_active', 'parent')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'url_name', 'custom_url')
    # Memungkinkan parent menunjuk ke diri sendiri
    raw_id_fields = ('parent',)

    def get_target_url(self, obj):
        return obj.get_absolute_url()
    get_target_url.short_description = "Target URL"


@admin.register(JumbotronSlide)
class JumbotronSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'image_preview')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'subtitle')

    def image_preview(self, obj):
        if obj.image:
            # Menggunakan format_html untuk keamanan
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "(No image)"
    image_preview.short_description = "Preview Gambar"


@admin.register(KetuaInfo)
class KetuaInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'photo_preview')
    fields = ('name', 'photo', 'welcome_message', 'is_active')
    # formfield_overrides = { # Aktifkan ini jika menggunakan CKEditor
    #     models.TextField: {'widget': CKEditorWidget},
    # }

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100" height="auto" />', obj.photo.url)
        return "(No photo)"
    photo_preview.short_description = "Preview Foto"

    # Memastikan hanya ada satu instance dari model ini
    def has_add_permission(self, request):
        return not KetuaInfo.objects.exists() and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False # Tidak bisa dihapus


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish_date', 'author', 'is_published', 'thumbnail_preview')
    list_filter = ('is_published', 'publish_date', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)} # Otomatis isi slug dari title
    date_hierarchy = 'publish_date' # Hirarki tanggal untuk navigasi
    ordering = ('-publish_date',)
    # formfield_overrides = { # Aktifkan ini jika menggunakan CKEditor
    #     models.TextField: {'widget': CKEditorWidget},
    # }

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user # Otomatis set penulis ke user yang sedang login
        super().save_model(request, obj, form, change)

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="80" height="auto" />', obj.thumbnail.url)
        return "(No thumbnail)"
    thumbnail_preview.short_description = "Preview Thumbnail"

# Daftarkan model VisiMisi
admin.site.register(VisiMisi)


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    # list_display diperbarui
    list_display = ('name', 'get_full_position_display', 'leadership_type', 'division', 'period', 'order', 'is_active', 'photo_preview')
    # list_filter diperbarui
    list_filter = ('is_active', 'leadership_type', 'division', 'period') 
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'position', 'bio_or_description')
    # ordering diperbarui agar konsisten dengan Meta.ordering di models.py
    ordering = ('leadership_type', 'division', 'order', 'name') 

    # fieldsets diperbarui untuk menyertakan field baru
    fieldsets = (
        (None, {
            'fields': ('name', 'position', 'leadership_type', 'division', 'period', 'photo', 'bio_or_description')
        }),
        ('Pengaturan Tampilan', {
            'fields': ('order', 'is_active'),
            'classes': ('collapse',) 
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="80" height="auto" />', obj.photo.url)
        return "(No Photo)"
    photo_preview.short_description = "Preview Foto"

    # Custom method for displaying full position in list_display
    # Ini adalah method yang menyebabkan error karena belum ada di kode Anda sebelumnya
    def get_full_position_display(self, obj):
        return obj.get_full_position_display() # Memanggil method dari instance model
    get_full_position_display.short_description = "Posisi Lengkap"

# Register HistoryPage model
@admin.register(HistoryPage)
class HistoryPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_updated')