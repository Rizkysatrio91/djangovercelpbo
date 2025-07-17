# Tampilanutama_app/models.py

from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.urls import reverse, NoReverseMatch
from tinymce.models import HTMLField


class TopBarConfig(models.Model):
    # --- Informasi Kontak ---
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Nomor Telepon")
    email = models.EmailField(blank=True, null=True, verbose_name="Alamat Email")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Alamat Singkat")

    # --- Media Sosial ---
    facebook_url = models.URLField(blank=True, null=True, verbose_name="URL Facebook")
    twitter_url = models.URLField(blank=True, null=True, verbose_name="URL Twitter")
    instagram_url = models.URLField(blank=True, null=True, verbose_name="URL Instagram")
    youtube_url = models.URLField(blank=True, null=True, verbose_name="URL YouTube")

    class Meta:
        verbose_name = "Konfigurasi Top Bar"
        verbose_name_plural = "Konfigurasi Top Bar"

    def __str__(self):
        return "Konfigurasi Top Bar Situs"

    def save(self, *args, **kwargs):
        # Memastikan hanya ada satu objek TopBarConfig yang bisa dibuat
        if not self.pk and TopBarConfig.objects.exists():
            # Jika sudah ada, jangan buat yang baru
            raise ValidationError('Hanya boleh ada satu Konfigurasi Top Bar.')
        return super(TopBarConfig, self).save(*args, **kwargs)


# Model untuk Pengaturan Situs Umum (Singleton)
class SiteConfiguration(models.Model):
    # Field untuk informasi yang tampil di beberapa tempat
    site_name = models.CharField(max_length=200, default="IMM FTIK UMKO", help_text="Nama situs utama (misal: IMM FTIK UMKO)")
    total_kader_count = models.PositiveIntegerField(default=0, help_text="Jumlah total Kader IMM FTIK UMKO")

    site_logo = models.ImageField(
        upload_to='site_logos/', 
        blank=True, 
        null=True,
        help_text="Logo situs (opsional)"
    )
    
    # --- PERUBAHAN FOOTER DIMULAI DI SINI ---
    
    # Field lama ini kita non-aktifkan dengan memberinya komentar
    # footer_text = models.TextField(blank=True, help_text="Teks singkat di footer")
    
    # Field-field baru yang lebih spesifik untuk footer
    footer_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Alamat Sekretariat di Footer")
    footer_email = models.EmailField(blank=True, null=True, verbose_name="Email Kontak di Footer")
    footer_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telepon Kontak di Footer")
    footer_website = models.URLField(blank=True, null=True, verbose_name="Website di Footer (contoh: https://domain.com)")
    
    # Field copyright tetap digunakan
    copyright_text = models.CharField(max_length=200, default="© 2025 IMM FTIK UMKO. All rights reserved.", help_text="Teks Copyright di footer")
    
    # --- AKHIR PERUBAHAN FOOTER ---

    class Meta:
        verbose_name = "Pengaturan Situs"
        verbose_name_plural = "Pengaturan Situs"
        # Memastikan hanya ada satu instance dari model ini
        constraints = [
            models.UniqueConstraint(fields=['id'], name='unique_site_configuration')
        ]

    def __str__(self):
        return self.site_name

# Model untuk Item Navigasi (Navbar)
class MenuItem(models.Model):
    title = models.CharField(max_length=100, help_text="Teks yang akan ditampilkan di navigasi")
    url_name = models.CharField(max_length=200, help_text="URL name Django (misal: 'home', 'pendaftaran', 'chatbot_app:home')", blank=True, null=True)
    custom_url = models.URLField(max_length=200, blank=True, null=True, help_text="URL kustom jika tidak menggunakan URL name Django (misal: 'https://example.com')")
    order = models.PositiveIntegerField(default=0, help_text="Urutan tampilan di navigasi")
    is_active = models.BooleanField(default=True, help_text="Apakah item navigasi ini aktif?")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', help_text="Jika ini adalah sub-menu dari menu lain")

    class Meta:
        verbose_name = "Item Navigasi"
        verbose_name_plural = "Item Navigasi"
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Seluruh blok ini sekarang memiliki indentasi yang benar
        if self.custom_url:
            return self.custom_url
        if self.url_name:
            try:
                # Mencoba dengan namespace
                return reverse(f'tampilan_utama_app:{self.url_name}')
            except NoReverseMatch:
                try:
                    # Fallback tanpa namespace
                    return reverse(self.url_name)
                except NoReverseMatch:
                    return "#url-not-found"
        return "#"


# Model untuk Jumbotron Slider (Gambar Bergeser)
class JumbotronSlide(models.Model):
    image = models.ImageField(upload_to='jumbotron_slides/', help_text="Gambar untuk slide jumbotron")
    title = models.CharField(max_length=200, blank=True, help_text="Judul besar di slide (opsional)")
    subtitle = models.CharField(max_length=300, blank=True, help_text="Sub-judul di slide (opsional)")
    link_url = models.URLField(max_length=200, blank=True, help_text="Link yang terkait dengan slide (opsional)")
    order = models.PositiveIntegerField(default=0, help_text="Urutan slide")
    is_active = models.BooleanField(default=True, help_text="Apakah slide ini aktif dan ditampilkan?")

    class Meta:
        verbose_name = "Slide Jumbotron"
        verbose_name_plural = "Slide Jumbotron"
        ordering = ['order']

    def __str__(self):
        return f"Slide {self.order}: {self.title or 'Tanpa Judul'}"


# Model untuk Info Ketua IMM FTIK UMKO
class KetuaInfo(models.Model):
    name = models.CharField(max_length=200, help_text="Nama Ketua IMM FTIK UMKO")
    photo = models.ImageField(upload_to='ketua_photos/', help_text="Foto Ketua")
    welcome_message = models.TextField(help_text="Kata sambutan Ketua") # Gunakan RichTextField jika CKEditor diinstal
    # welcome_message = RichTextField(help_text="Kata sambutan Ketua") # Jika menggunakan CKEditor
    is_active = models.BooleanField(default=True, help_text="Apakah info Ketua ini aktif?")

    class Meta:
        verbose_name = "Info Ketua"
        verbose_name_plural = "Info Ketua"
        # Memastikan hanya ada satu instance dari model ini
        constraints = [
            models.UniqueConstraint(fields=['id'], name='unique_ketua_info')
        ]

    def __str__(self):
        return self.name

# Model untuk Berita Ikatan
class NewsArticle(models.Model):
    title = models.CharField(max_length=255, help_text="Judul Berita")
    slug = models.SlugField(unique=True, help_text="Slug untuk URL berita (otomatis terisi)")
    thumbnail = models.ImageField(upload_to='news_thumbnails/', blank=True, null=True, help_text="Gambar kecil/thumbnail berita")
    content = HTMLField(help_text="Isi berita lengkap") # Gunakan RichTextField jika CKEditor diinstal
    # content = RichTextField(help_text="Isi berita lengkap") # Jika menggunakan CKEditor
    publish_date = models.DateTimeField(auto_now_add=True, help_text="Tanggal publikasi")
    author = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, help_text="Penulis berita")
    is_published = models.BooleanField(default=True, help_text="Apakah berita ini sudah dipublikasikan?")

    class Meta:
        verbose_name = "Berita Ikatan"
        verbose_name_plural = "Berita Ikatan"
        ordering = ['-publish_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Perbaikan kecil: Seharusnya 'tampilan_utama_app:news_detail' sesuai url Anda
        return reverse('tampilan_utama_app:news_detail', args=[self.slug])
    
    # === MODEL BARU UNTUK HALAMAN VISI MISI ===
class VisiMisi(models.Model):
    title = models.CharField(max_length=200, default="Visi - Misi", verbose_name="Judul Halaman")
    logo = models.ImageField(upload_to='visimisi/', blank=True, null=True, verbose_name="Logo Perusahaan/Organisasi")
    subtitle = models.CharField(max_length=200, blank=True, null=True, verbose_name="Teks di Bawah Logo", help_text="Contoh: AHU-0066022-AH.01.14 Tahun 2021")
    
    visi_title = models.CharField(max_length=50, default="VISI", verbose_name="Judul Kolom Visi")
    # GANTI TextField MENJADI HTMLField
    visi_content = HTMLField(verbose_name="Isi Visi")

    misi_title = models.CharField(max_length=50, default="MISI", verbose_name="Judul Kolom Misi")
    # GANTI TextField MENJADI HTMLField
    misi_content = HTMLField(verbose_name="Isi Misi")

    class Meta:
        verbose_name = "Halaman Visi & Misi"
        verbose_name_plural = "Halaman Visi & Misi"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk and VisiMisi.objects.exists():
            raise ValidationError('Hanya boleh ada satu entri untuk Halaman Visi & Misi.')
        return super(VisiMisi, self).save(*args, **kwargs)
    
# Model baru untuk Struktur Organisasi
class OrganizationMember(models.Model):
    LEADERSHIP_TYPE_CHOICES = [
        ('KetuUm', 'Ketua Umum'),
        ('SekUm', 'Sekretaris Umum'),
        ('BendUm', 'Bendahara Umum'),
        ('KetuBid', 'Ketua Bidang'),
        ('SekBid', 'Sekretaris Bidang'),
        ('Anggota', 'Anggota Bidang'),
        ('Lainnya', 'Lainnya'),
    ]

    DIVISION_CHOICES = [
        ('None', 'None (Untuk Ketua/Sekum/Bendahara Umum)'),
        ('Organisasi', 'Bidang Organisasi'), # Mengganti 'Organisasi' dengan 'Bidang Organisasi'
        ('Kaderisasi', 'Bidang Kaderisasi'), # Menambahkan
        ('Riset & Pengembangan Keilmuan', 'Bidang Riset & Pengembangan Keilmuan'), # Mengganti 'Riset & Pengembangan Keilmuan'
        ('Tablig, Kajian, & Keislaman', 'Bidang Tablig, Kajian, dan Keislaman'), # Menambahkan
        ('Hikmah, Politik, & Kebijakan Publik', 'Bidang Hikmah, Politik, dan Kebijakan Publik'), # Mengganti 'Hikmah, Politik, & Kebijakan Publik'
        ('Immawati', 'Bidang Immawati'), # Menambahkan
        ('Media & Komunikasi', 'Bidang Media dan Komunikasi'), # Mengganti 'Media & Komunikasi'
        ('Sosial & Pemberdayaan Masyarakat', 'Bidang Sosial dan Pemberdayaan Masyarakat'), # Menambahkan
        ('Lingkungan Hidup', 'Bidang Lingkungan Hidup'), # Menambahkan
        ('Ekonomi & Kewirausahaan', 'Bidang Ekonomi dan Kewirausahaan'), # Menambahkan
        ('Seni, Budaya, & Olahraga', 'Bidang Seni, Budaya, dan Olahraga'), # Menambahkan
        # Pastikan ini semua nama bidang yang ingin Anda tampilkan
        # Sesuaikan dengan nama bidang yang ada di screenshot Anda
        # Misal: Bidang DPM, Bidang SBO, Bidang IMMawati, dll.
    ]

    name = models.CharField(max_length=200, verbose_name="Nama Lengkap")
    position = models.CharField(max_length=200, verbose_name="Jabatan Spesifik") # Misal: "Ketua", "Sekretaris", "Anggota"
    leadership_type = models.CharField(max_length=10, choices=LEADERSHIP_TYPE_CHOICES, default='Lainnya', verbose_name="Jenis Kepemimpinan")
    division = models.CharField(max_length=100, choices=DIVISION_CHOICES, default='None', verbose_name="Bidang/Divisi")
    period = models.CharField(max_length=100, blank=True, null=True, verbose_name="Periode Jabatan")
    photo = models.ImageField(upload_to='organization_members/', blank=True, null=True, verbose_name="Foto Anggota")
    bio_or_description = models.TextField(blank=True, null=True, verbose_name="Biografi Singkat/Deskripsi Tugas")
    order = models.PositiveIntegerField(default=0, help_text="Urutan tampilan dalam satu kelompok/level.")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Anggota Struktur Organisasi"
        verbose_name_plural = "Anggota Struktur Organisasi"
        # Urutkan berdasarkan jenis kepemimpinan (untuk PHK), lalu divisi, lalu jenis kepemimpinan dalam divisi, lalu order
        ordering = ['leadership_type', 'division', 'order', 'name']

    def __str__(self):
        if self.leadership_type != 'Lainnya':
            if self.division != 'None':
                return f"{self.name} ({self.get_leadership_type_display()} {self.get_division_display()})"
            return f"{self.name} ({self.get_leadership_type_display()})"
        return f"{self.name} ({self.position})"

    def get_full_position_display(self):
        # Ini akan menjadi label yang tampil di bawah nama anggota di kartu (misal: Ketua, Sekretaris, Anggota)
        if self.leadership_type == 'KetuUm': return "Ketua Umum"
        if self.leadership_type == 'SekUm': return "Sekretaris Umum"
        if self.leadership_type == 'BendUm': return "Bendahara Umum"
        if self.leadership_type == 'KetuBid': return "Ketua"
        if self.leadership_type == 'SekBid': return "Sekretaris"
        if self.leadership_type == 'Anggota': return "Anggota"
        return self.position # Default untuk 'Lainnya'
    
class HistoryPage(models.Model):
    title = models.CharField(max_length=200, default="Sejarah IMM", verbose_name="Judul Halaman")
    # Menggunakan HTMLField untuk konten yang bisa diedit dengan TinyMCE
    content = HTMLField(verbose_name="Isi Halaman Sejarah")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Terakhir Diperbarui")

    class Meta:
        verbose_name = "Halaman Sejarah"
        verbose_name_plural = "Halaman Sejarah"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Memastikan hanya ada satu entri untuk halaman sejarah
        if not self.pk and HistoryPage.objects.exists():
            raise ValidationError('Hanya boleh ada satu entri untuk Halaman Sejarah.')
        return super(HistoryPage, self).save(*args, **kwargs)