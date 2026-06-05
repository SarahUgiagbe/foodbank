/* ============================================
   SHARED JS — We Share & Care Food Bank
   Toast helper used by all pages
   ============================================ */

function showToast(message) {
    document.getElementById('toastMessage').textContent = message;
    const toastEl = document.getElementById('liveToast');
    const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
    toast.show();
}