from django import forms
from .models import BerkasPendaftaran


class BerkasPendaftaranForm(forms.ModelForm):
    class Meta:
        model = BerkasPendaftaran
        fields = ['nama_pendaftar', 'email_pendaftar']

class FilePDFForm(forms.Form):
    file_pdf = forms.FileField(label="Unggah File PDF (Max 5)", required=False)

class PasFotoForm(forms.Form):
    pas_foto = forms.FileField(label="Unggah Pas Foto (Max 2)", required=False)