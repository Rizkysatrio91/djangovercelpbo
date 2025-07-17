# pendaftaran_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, DetailView
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

import PyPDF2
import json
import re
import google.generativeai as genai

from .forms import BerkasPendaftaranForm, FilePDFForm, PasFotoForm
from .models import BerkasPendaftaran, FilePDF, PasFoto, BasisPengetahuan, KonfigurasiUnggah
from Tampilanutama_app.models import SiteConfiguration, MenuItem, TopBarConfig


# Konfigurasi Gemini API key
genai.configure(api_key=settings.GEMINI_API_KEY)

# ==============================================================================
# HELPER/UTILITY FUNCTIONS
# ==============================================================================
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                if page.extract_text():
                    text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text

def call_gemini_for_document_extraction(text_content: str, document_name: str, fields_to_extract: list):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt_parts = [
        f"Anda adalah asisten cerdas yang menganalisis formulir pendaftaran. Saya akan memberikan Anda teks dari sebuah dokumen PDF bernama '{document_name}'. Tugas Anda adalah mengekstrak semua informasi penting berikut dalam format JSON. Jika suatu field kosong atau tidak ditemukan dalam teks, berikan nilai 'null' untuk field tersebut. Untuk daftar atau tabel, berikan sebagai array objek jika memungkinkan. Untuk field status seperti 'Indikasi Materai', berikan status 'Ditemukan' atau 'Tidak Ditemukan' dan alasan jika tidak ditemukan.",
        "\n\n**Daftar Field yang Harus Diekstrak:**"
    ]

    json_structure_hints = []
    for field in fields_to_extract:
        prompt_parts.append(f"- **{field.display_name}** (`{field.field_name}`): {field.description}. Format yang diharapkan: '{field.expected_format_hint}'. Wajib: {field.is_required}.")
        
        if "daftar" in field.description.lower() or "tabel" in field.description.lower() or "pengalaman" in field.description.lower() or "pendidikan" in field.description.lower():
            json_structure_hints.append(f'   "{field.field_name}": [...] // Array of objects or strings')
        elif "status" in field.display_name.lower() or "indikasi" in field.display_name.lower():
            json_structure_hints.append(f'   "{field.field_name}": {{"status": "Ditemukan/Tidak Ditemukan", "alasan": "..."}}')
        else:
            json_structure_hints.append(f'   "{field.field_name}": "..." // Value of the field')
            
    prompt_parts.append("\n\n**Teks dari Dokumen:**")
    prompt_parts.append(text_content)

    prompt_parts.append("\n\n**Format Output JSON yang Diinginkan:**")
    prompt_parts.append("```json")
    prompt_parts.append("{")
    prompt_parts.extend(json_structure_hints)
    prompt_parts.append("}")
    prompt_parts.append("```")
    prompt_parts.append("Mohon pastikan output Anda HANYA berupa JSON. Jangan tambahkan penjelasan lain di luar blok JSON.")

    full_prompt = "\n".join(prompt_parts)
    
    gemini_response_text = None 
    try:
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1,
        )
        response = model.generate_content(full_prompt, generation_config=generation_config)
        gemini_response_text = response.text.strip()
        
        return json.loads(gemini_response_text)

    except json.JSONDecodeError as e:
        print(f"JSON parsing error dari respon Gemini: {e}. Respon mentah: {gemini_response_text}")
        return {
            "error": "Gagal parsing JSON dari AI. Format tidak sesuai.",
            "raw_response": gemini_response_text
        }
    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        return {
            "error": f"Error saat memanggil AI: {str(e)}",
            "raw_response": gemini_response_text
        }
        
def analisis_berkas_dengan_ai(pendaftaran_obj: BerkasPendaftaran):
    print(f"--- Memulai analisis untuk Pendaftaran ID: {pendaftaran_obj.pk} ---")
    
    extracted_data_by_doc = {}
    overall_status = "Lengkap"
    issues_found = []

    fields_to_extract = BasisPengetahuan.objects.filter(aktif=True).order_by('pk')
    if not fields_to_extract.exists():
        issues_found.append("Tidak ada field ekstraksi AI yang aktif di Basis Pengetahuan.")
        overall_status = "Tidak Lengkap"

    pdf_files_to_analyze = pendaftaran_obj.file_pdfs.all()
    if not pdf_files_to_analyze.exists() and fields_to_extract.filter(is_required=True).exists():
        issues_found.append("Tidak ada dokumen PDF diunggah, padahal ada field wajib yang harus diekstrak.")
        overall_status = "Tidak Lengkap"

    for pdf_file_obj in pdf_files_to_analyze:
        print(f"Menganalisis PDF: {pdf_file_obj.file.path}")
        text_from_pdf = extract_text_from_pdf(pdf_file_obj.file.path)
        
        doc_key = f'Dokumen_{pdf_file_obj.jenis_dokumen}'
        
        if not text_from_pdf:
            extracted_data_by_doc[doc_key] = {"error": "Gagal membaca teks dari PDF ini."}
            issues_found.append(f"Dokumen '{pdf_file_obj.jenis_dokumen}': Tidak dapat dibaca untuk analisis.")
            overall_status = "Tidak Lengkap"
            continue
        
        gemini_extraction_result = call_gemini_for_document_extraction(
            text_from_pdf, 
            document_name=pdf_file_obj.jenis_dokumen, 
            fields_to_extract=list(fields_to_extract)
        )
        
        extracted_data_by_doc[doc_key] = gemini_extraction_result

        if "error" in gemini_extraction_result:
            issues_found.append(f"Dokumen '{pdf_file_obj.jenis_dokumen}': Gagal ekstraksi AI ({gemini_extraction_result.get('error')}).")
            overall_status = "Tidak Lengkap"
        else:
            for field in fields_to_extract:
                if field.aktif and field.is_required:
                    extracted_value = gemini_extraction_result.get(field.field_name)
                    if extracted_value is None or \
                       (isinstance(extracted_value, str) and extracted_value.lower() == 'null') or \
                       (isinstance(extracted_value, (list, dict)) and not extracted_value):
                        issues_found.append(f"Dokumen '{pdf_file_obj.jenis_dokumen}', Field '{field.display_name}': Wajib diisi tapi kosong/tidak ditemukan.")
                        overall_status = "Tidak Lengkap"
                    elif isinstance(extracted_value, dict) and 'status' in extracted_value and extracted_value['status'].lower() == 'tidak ditemukan':
                        issues_found.append(f"Dokumen '{pdf_file_obj.jenis_dokumen}', Field '{field.display_name}': {extracted_value.get('alasan', 'Tidak ditemukan.')}")
                        overall_status = "Tidak Lengkap"

    konfigurasi = KonfigurasiUnggah.objects.first()
    if konfigurasi and konfigurasi.max_photos > 0 and not pendaftaran_obj.pas_fotos.exists():
        issues_found.append("Pas foto tidak diunggah.")
        overall_status = "Tidak Lengkap"
    elif konfigurasi and konfigurasi.max_photos > 0 and pendaftaran_obj.pas_fotos.exists():
        print(f"Ada {pendaftaran_obj.pas_fotos.count()} pas foto yang diunggah.")

    final_analysis_result = {
        "overall_status": overall_status,
        "extracted_data": extracted_data_by_doc,
        "validation_issues": issues_found
    }
    
    pendaftaran_obj.hasil_seleksi = final_analysis_result
    pendaftaran_obj.save()
    print(f"Hasil analisis disimpan untuk Pendaftaran ID: {pendaftaran_obj.pk}")

    subjek_email = f"Hasil Seleksi Berkas Pendaftaran Anda - {pendaftaran_obj.nama_pendaftar}"
    if overall_status == "Lengkap":
        pesan_email = f"Yth. {pendaftaran_obj.nama_pendaftar},\n\nTerima kasih telah mendaftar. Berkas pendaftaran Anda telah kami terima dan dinyatakan LENGKAP.\n\nKami akan segera menghubungi Anda untuk informasi lebih lanjut mengenai tahap selanjutnya.\n\nTerima kasih,\nPanitia Pendaftaran"
    else:
        pesan_email = f"Yth. {pendaftaran_obj.nama_pendaftar},\n\nTerima kasih telah mendaftar. Setelah melakukan pemeriksaan, kami menemukan beberapa kekurangan pada berkas Anda:\n\n"
        pesan_email += "\n".join([f"- {item}" for item in issues_found])
        pesan_email += "\n\nMohon perbaiki kekurangan tersebut dan unggah kembali berkas Anda melalui sistem kami.\n\nTerima kasih,\nPanitia Pendaftaran"

    try:
        send_mail(
            subjek_email, pesan_email,
            settings.DEFAULT_FROM_EMAIL, [pendaftaran_obj.email_pendaftar],
            fail_silently=False,
        )
        print(f"Email feedback berhasil dikirim ke: {pendaftaran_obj.email_pendaftar}")
    except Exception as e:
        print(f"Gagal mengirim email ke {pendaftaran_obj.email_pendaftar}: {e}")

# ==============================================================================
# CLASS-BASED VIEWS
# ==============================================================================

class BerandaView(TemplateView):
    template_name = 'pendaftaran_app/beranda.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        konfigurasi = KonfigurasiUnggah.objects.first()
        
        context['site_config'] = SiteConfiguration.objects.first()
        context['top_bar'] = TopBarConfig.objects.first()
        context['menu_items'] = MenuItem.objects.filter(is_active=True, parent__isnull=True).order_by('order') 
        
        context.update({
            'form_pendaftaran': BerkasPendaftaranForm(),
            'form_pdf': FilePDFForm(),
            'form_foto': PasFotoForm(),
            'berkas_list': BerkasPendaftaran.objects.all().order_by('-tanggal_unggah'),
            'konfigurasi': konfigurasi
        })
        return context

class UnggahBerkasView(View):
    def post(self, request, *args, **kwargs):
        form_pendaftaran = BerkasPendaftaranForm(request.POST)
        form_pdf = FilePDFForm(request.POST, request.FILES) 
        form_foto = PasFotoForm(request.POST, request.FILES)

        konfigurasi = KonfigurasiUnggah.objects.first()
        if not konfigurasi:
            messages.error(request, "Pengaturan unggah belum dikonfigurasi oleh administrator.")
            return redirect('pendaftaran_app:beranda')

        if form_pendaftaran.is_valid():
            pendaftaran = form_pendaftaran.save()
            errors = []

            # Validasi PDF
            pdf_files = request.FILES.getlist('file_pdf')
            is_pdf_required = BasisPengetahuan.objects.filter(aktif=True, is_required=True).exists()
            if is_pdf_required and not pdf_files:
                errors.append("Mohon unggah setidaknya satu file PDF karena ada field wajib yang harus diekstrak.")
            elif len(pdf_files) > konfigurasi.max_pdfs:
                errors.append(f"Jumlah file PDF ({len(pdf_files)}) melebihi batas maksimal ({konfigurasi.max_pdfs}).")
            else:
                for pdf_file in pdf_files:
                    if pdf_file.size > konfigurasi.max_pdf_size_mb * 1024 * 1024:
                        errors.append(f"Ukuran file PDF '{pdf_file.name}' melebihi batas {konfigurasi.max_pdf_size_mb} MB.")
                    if not pdf_file.name.lower().endswith('.pdf'):
                        errors.append(f"File '{pdf_file.name}' bukan format PDF.")
                    
                    if not errors: 
                        FilePDF.objects.create(pendaftaran=pendaftaran, file=pdf_file,
                                               jenis_dokumen=pdf_file.name.split('.')[0].replace('_', ' ').title())

            # Validasi Pas Foto
            pas_foto_files = request.FILES.getlist('pas_foto')
            is_photo_required = konfigurasi.max_photos > 0
            if is_photo_required and not pas_foto_files:
                errors.append("Mohon unggah pas foto.")
            elif len(pas_foto_files) > konfigurasi.max_photos:
                errors.append(f"Jumlah pas foto ({len(pas_foto_files)}) melebihi batas maksimal ({konfigurasi.max_photos}).")
            else:
                for foto_file in pas_foto_files:
                    if foto_file.size > konfigurasi.max_photo_size_mb * 1024 * 1024:
                        errors.append(f"Ukuran pas foto '{foto_file.name}' melebihi batas {konfigurasi.max_photo_size_mb} MB.")
                    if not foto_file.content_type.startswith('image/'):
                        errors.append(f"File '{foto_file.name}' bukan format gambar.")
                    if not errors: 
                        PasFoto.objects.create(pendaftaran=pendaftaran, file=foto_file)

            # Penanganan Error atau Sukses
            if errors:
                pendaftaran.delete() 
                for error_msg in errors:
                    messages.error(request, error_msg)
                return redirect('pendaftaran_app:beranda')

            analisis_berkas_dengan_ai(pendaftaran)
            
            # Pesan sukses untuk pop-up SweetAlert2
            messages.success(request, "Berkas Anda berhasil dikirim. Silakan cek email Anda secara berkala untuk feedback.")
            
            return redirect('pendaftaran_app:beranda')
        
        else:
            for field, field_errors in form_pendaftaran.errors.items():
                for error in field_errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            return redirect('pendaftaran_app:beranda')

class DetailBerkasView(DetailView):
    model = BerkasPendaftaran
    template_name = 'pendaftaran_app/detail_berkas.html'
    context_object_name = 'berkas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['site_config'] = SiteConfiguration.objects.first()
        context['top_bar'] = TopBarConfig.objects.first()
        context['menu_items'] = MenuItem.objects.filter(is_active=True, parent__isnull=True).order_by('order') 
        
        berkas = self.get_object()
        context['hasil_seleksi'] = berkas.hasil_seleksi
        
        return context