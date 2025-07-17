// PROJECT_PENDAFTARAN/static/js/custom_login.js

document.addEventListener("DOMContentLoaded", function () {
  // Target logo di halaman login
  const loginLogo = document.querySelector(".login-logo img");

  if (loginLogo) {
    // Atur ukuran yang diinginkan
    loginLogo.style.maxWidth = "150px"; // Contoh, sesuaikan
    loginLogo.style.height = "auto"; // Penting untuk menjaga rasio aspek
    loginLogo.style.width = "auto"; // Juga penting untuk menjaga rasio aspek
    loginLogo.style.objectFit = "contain";

    // Opsional: Untuk memastikan tidak ada gaya lain yang memaksakan
    loginLogo.style.setProperty("width", "auto", "important");
    loginLogo.style.setProperty("height", "auto", "important");
    loginLogo.style.setProperty("max-width", "80px", "important");
    loginLogo.style.setProperty("object-fit", "contain", "important");
  }
});
