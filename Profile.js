/* ============================================
   PROFILE PAGE JS
   ============================================ */

function saveProfile() {
    const firstName = document.getElementById('profileFirstName').value.trim();
    const lastName  = document.getElementById('profileLastName').value.trim();
    const email     = document.getElementById('profileEmail').value.trim();
    const phone     = document.getElementById('profilePhone').value.trim();

    // Update the volunteer card on the right
    document.getElementById('profileCardName').textContent  = `${firstName} ${lastName}`;
    document.getElementById('profileCardEmail').textContent = email;
    document.getElementById('profileCardPhone').textContent = phone;

    showToast('Profile saved successfully!');
}