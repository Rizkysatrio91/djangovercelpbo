from django.views.generic import TemplateView, DetailView
from collections import OrderedDict # Pastikan ini diimport
from .models import TopBarConfig, SiteConfiguration, JumbotronSlide, KetuaInfo, NewsArticle, MenuItem, VisiMisi, OrganizationMember, HistoryPage

# ==============================================================================
# VIEW UNTUK HALAMAN UTAMA (HOME PAGE)
# ==============================================================================
class HomePageView(TemplateView):
    """
    Menggantikan fungsi `home_page`. Menggunakan TemplateView karena tugasnya
    adalah merender satu template dengan banyak data konteks.
    """
    template_name = 'Tampilanutama_app/home_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ambil pengaturan situs umum
        site_config = SiteConfiguration.objects.first()
        if not site_config:
            site_config = SiteConfiguration(site_name="IMM FTIK UMKO (Default)", total_kader_count=0)

        # Ambil info ketua
        ketua_info = KetuaInfo.objects.filter(is_active=True).first()
        if not ketua_info:
            ketua_info = KetuaInfo(name="Ketua IMM (Default)", welcome_message="Selamat datang di website kami.")

        # Menambahkan semua data yang dibutuhkan oleh template ke dalam context
        context.update({
            'site_config': site_config,
            'top_bar': TopBarConfig.objects.first(),
            'jumbotron_slides': JumbotronSlide.objects.filter(is_active=True).order_by('order'),
            'ketua_info': ketua_info,
            'recent_news': NewsArticle.objects.filter(is_published=True).order_by('-publish_date')[:3],
            'menu_items': MenuItem.objects.filter(is_active=True, parent__isnull=True).order_by('order'),
        })
        return context

# ==============================================================================
# VIEW UNTUK DETAIL BERITA (NEWS DETAIL)
# ==============================================================================
class NewsDetailView(DetailView):
    """
    Menggantikan fungsi `news_detail`. Menggunakan DetailView karena tugasnya
    adalah menampilkan detail dari satu objek model (`NewsArticle`).
    """
    model = NewsArticle
    template_name = 'Tampilanutama_app/news_detail.html'
    context_object_name = 'article' # Menyesuaikan nama variabel di template
    # 'slug' akan secara otomatis digunakan untuk mencari artikel

    def get_queryset(self):
        """
        Memastikan hanya artikel yang sudah dipublikasikan yang bisa diakses.
        """
        return super().get_queryset().filter(is_published=True)

    def get_context_data(self, **kwargs):
        """
        Menambahkan data ekstra ke dalam context, selain data artikel utama.
        """
        context = super().get_context_data(**kwargs)
        article = self.get_object()

        # Menambahkan data layout dan berita terbaru lainnya
        context.update({
            'site_config': SiteConfiguration.objects.first(),
            'top_bar': TopBarConfig.objects.first(),
            'menu_items': MenuItem.objects.filter(is_active=True, parent__isnull=True).order_by('order'),
            'recent_posts': NewsArticle.objects.filter(is_published=True).exclude(pk=article.pk).order_by('-publish_date')[:5],
        })
        return context

# ==============================================================================
# VIEW UNTUK HALAMAN VISI & MISI
# ==============================================================================
class VisiMisiPageView(TemplateView):
    """
    Menggantikan fungsi `visi_misi_page`. Sama seperti HomePageView,
    tugasnya adalah merender template dengan data.
    """
    template_name = 'Tampilanutama_app/visi_misi.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Menambahkan data yang dibutuhkan oleh halaman Visi & Misi
        context.update({
            'site_config': SiteConfiguration.objects.first(),
            'top_bar': TopBarConfig.objects.first(),
            'menu_items': MenuItem.objects.filter(is_active=True).select_related('parent'),
            'visimisi': VisiMisi.objects.first(),
        })
        return context
    
# ==============================================================================
# VIEW UNTUK HALAMAN STRUKTUR ORGANISASI
# ==============================================================================
class OrganizationStructurePageView(TemplateView):
    template_name = 'Tampilanutama_app/struktur_organisasi.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_members = OrganizationMember.objects.filter(is_active=True).order_by(
            'leadership_type', 'division', 'order', 'name'
        )

        hierarchical_data = OrderedDict()

        # --- Bagian 1: Pimpinan Harian Komisiariat ---
        phk_members_list = []
        phk_order_map = {'KetuUm': 1, 'SekUm': 2, 'BendUm': 3} # Urutan spesifik
        phk_qs = all_members.filter(leadership_type__in=['KetuUm', 'SekUm', 'BendUm'])
        phk_members_list = sorted(list(phk_qs), key=lambda x: phk_order_map.get(x.leadership_type, 99))
        
        if phk_members_list:
            hierarchical_data['Pimpinan Harian Komisiariat'] = {'type': 'phk', 'members': phk_members_list}

        # --- Bagian 2: Bidang-Bidang Organisasi ---
        division_groups = OrderedDict()
        
        # Iterasi melalui semua pilihan DIVISI yang ada di model
        for div_code, div_display in OrganizationMember.DIVISION_CHOICES:
            # Lewati 'None' karena itu untuk Pimpinan Harian Komisiariat
            if div_code != 'None': 
                # Filter anggota berdasarkan kode divisi (div_code)
                # dan pastikan leadership_type bukan PHK, serta bukan 'Lainnya' jika Anda punya grup 'Lainnya' terpisah
                division_members = all_members.filter(
                    division=div_code
                ).exclude(
                    leadership_type__in=['KetuUm', 'SekUm', 'BendUm', 'Lainnya'] # Pastikan tidak termasuk PHK atau 'Lainnya'
                ).order_by(
                    'leadership_type', 'order'
                )
                
                if division_members.exists():
                    # Definisikan urutan spesifik untuk posisi di dalam bidang
                    division_order_map = {'KetuBid': 1, 'SekBid': 2, 'Anggota': 3}
                    sorted_div_members = sorted(list(division_members), key=lambda x: division_order_map.get(x.leadership_type, 99))
                    
                    # Kunci untuk dictionary adalah nama tampilan bidang (div_display)
                    division_groups[div_display] = sorted_div_members 

        # Tambahkan Bidang-Bidang Organisasi ke hierarchical_data jika ada anggota di dalamnya
        if division_groups:
            hierarchical_data['Bidang-Bidang Organisasi'] = {'type': 'divisions', 'data': division_groups}
            
        # --- Bagian 3: Posisi Lainnya (jika ada) ---
        # Posisi yang tidak termasuk PHK dan bukan anggota bidang tertentu
        # Asumsikan 'Lainnya' di leadership_type mencakup ini
        other_members = all_members.filter(leadership_type='Lainnya').order_by('order', 'name')
        if other_members.exists():
            hierarchical_data['Posisi Lainnya'] = {'type': 'other', 'members': list(other_members)}

        context.update({
            'site_config': SiteConfiguration.objects.first(),
            'top_bar': TopBarConfig.objects.first(),
            'menu_items': MenuItem.objects.filter(is_active=True).select_related('parent'),
            'hierarchical_data': hierarchical_data, # Nama variabel diubah lagi untuk kejelasan
            'organization_year': "2025-2026", # Pastikan ini sesuai dengan tahun yang ingin Anda tampilkan
        })
        return context
    
class HistoryPageView(TemplateView):
    template_name = 'Tampilanutama_app/history_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ambil satu-satunya objek HistoryPage (karena kita membatasi satu entri di model)
        history_content = HistoryPage.objects.first()
        if not history_content:
            # Sediakan default jika belum ada data di admin
            history_content = HistoryPage(title="Sejarah IMM (Belum Diatur)", content="<p>Konten sejarah belum ditambahkan. Silakan atur di halaman admin.</p>")

        context.update({
            'site_config': SiteConfiguration.objects.first(),
            'top_bar': TopBarConfig.objects.first(),
            'menu_items': MenuItem.objects.filter(is_active=True).select_related('parent'),
            'history_content': history_content, # Variabel yang akan digunakan di template
        })
        return context