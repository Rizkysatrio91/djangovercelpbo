// Jalankan script ini setelah seluruh halaman HTML dimuat
document.addEventListener("DOMContentLoaded", function () {
  // Inisialisasi AOS untuk animasi scroll
  AOS.init({
    duration: 800,
    once: true,
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const navbar = document.querySelector(".navbar");
  // Dapatkan posisi atas navbar
  const navbarOffsetTop = navbar.offsetTop;

  window.onscroll = function () {
    // Jika posisi scroll sudah melewati posisi awal navbar
    if (window.pageYOffset > navbarOffsetTop) {
      navbar.classList.add("navbar-scrolled");
    } else {
      navbar.classList.remove("navbar-scrolled");
    }
  };
});