from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class BerkasPendaftaran(models.Model):
    nama_pendaftar = models.CharField(max_length=255)
    email_pendaftar = models.EmailField(max_length=255)
    hasil_seleksi = models.JSONField(blank=True, null=True) # Akan menyimpan hasil ekstraksi dan validasi
    tanggal_unggah = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pendaftaran oleh {self.nama_pendaftar} ({self.tanggal_unggah.strftime('%d-%m-%Y')})"

    def get_absolute_url(self):
        return reverse('admin:pendaftaran_app_berkaspendaftaran_change', args=[self.pk])


class FilePDF(models.Model):
    pendaftaran = models.ForeignKey(BerkasPendaftaran, related_name='file_pdfs', on_delete=models.CASCADE)
    nama_file = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='berkas_pendaftaran/pdfs/')
    jenis_dokumen = models.CharField(max_length=100, blank=True, null=True,
                                     help_text="Contoh: Formulir Pendaftaran, Surat Pernyataan")

    def save(self, *args, **kwargs):
        if not self.nama_file and self.file:
            self.nama_file = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama_file} ({self.jenis_dokumen or 'PDF'}) untuk {self.pendaftaran.nama_pendaftar}"

class PasFoto(models.Model):
    pendaftaran = models.ForeignKey(BerkasPendaftaran, related_name='pas_fotos', on_delete=models.CASCADE)
    nama_file = models.CharField(max_length=255, blank=True)
    file = models.ImageField(upload_to='berkas_pendaftaran/pas_fotos/')
    ukuran_asli = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.nama_file and self.file:
            self.nama_file = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama_file} (Pas Foto) untuk {self.pendaftaran.nama_pendaftar}"

class BasisPengetahuan(models.Model):
    # Field yang akan diekstrak oleh AI
    field_name = models.CharField(max_length=255, unique=True, help_text="Nama field yang akan diekstrak (misal: nama_lengkap, alamat_email, pengalaman_organisasi)")
    display_name = models.CharField(max_length=255, help_text="Nama tampilan untuk field ini (misal: Nama Lengkap, Alamat Email)")
    is_required = models.BooleanField(default=True, help_text="Apakah field ini wajib diisi?")
    expected_format_hint = models.TextField(blank=True, help_text="Petunjuk untuk AI tentang format yang diharapkan (misal: 'tanggal dengan format DD Bulan YYYY', 'email valid')")
    description = models.TextField(blank=True, help_text="Deskripsi detail untuk instruksi AI atau validasi tambahan.")
    
    # Menunjukkan apakah kriteria ini aktif untuk ekstraksi
    aktif = models.BooleanField(default=True, help_text="Apakah field ini aktif untuk diekstrak oleh AI?")

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name_plural = "Field Ekstraksi AI" # Ubah nama di admin
        verbose_name = "Field Ekstraksi AI"

class KonfigurasiUnggah(models.Model):
    max_pdfs = models.PositiveIntegerField(default=5, help_text="Jumlah maksimal file PDF yang bisa diunggah per pendaftaran.")
    max_pdf_size_mb = models.PositiveIntegerField(default=10, help_text="Ukuran maksimal per file PDF dalam MB.")
    max_photos = models.PositiveIntegerField(default=2, help_text="Jumlah maksimal pas foto yang bisa diunggah per pendaftaran.")
    max_photo_size_mb = models.PositiveIntegerField(default=5, help_text="Ukuran maksimal per pas foto dalam MB.")

    class Meta:
        verbose_name_plural = "Konfigurasi Unggah"
        constraints = [
            models.UniqueConstraint(fields=['id'], name='unique_konfigurasi_unggah')
        ]

    def __str__(self):
        return "Pengaturan Unggah Berkas Pendaftaran"