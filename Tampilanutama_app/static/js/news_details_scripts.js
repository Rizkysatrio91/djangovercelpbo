new WOW().init();

function copyToClipboard() {
  // Menggunakan navigator.clipboard yang lebih modern dan aman (memerlukan HTTPS)
  navigator.clipboard.writeText(window.location.href).then(
    function () {
      // Fungsi ini dijalankan jika penyalinan berhasil
      alert("Link berita berhasil disalin!");
    },
    function (err) {
      // Fungsi ini dijalankan jika terjadi error
      alert("Gagal menyalin link.");
      console.error('Could not copy text: ', err);
    }
  );
}