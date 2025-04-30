let userIdToDelete = null;

function openPasswordModal(userId) {
    userIdToDelete = userId;
    document.getElementById('masterPasswordInput').value = '';
    document.getElementById('errorMsg').classList.add('d-none');
    new bootstrap.Modal(document.getElementById('masterPasswordModal')).show();
}

async function confirmDelete() {
    const password = document.getElementById('masterPasswordInput').value;

    const res = await fetch('/verify-master-password-bbdd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
    });

    const result = await res.json();

    if (res.ok && result.valid) {
        document.getElementById(`deleteForm-${userIdToDelete}`).submit();
    } else {
        document.getElementById('errorMsg').classList.remove('d-none');
    }
}

if (document.cookie.includes("message=")) {
    document.cookie = "message=; Max-Age=0; path=/";
}

$(document).ready(function () {
    $('#dataTable').DataTable({
        pageLength: 10,
        lengthMenu: [5, 10, 25, 50, 100],
        language: {
            url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
        },
        dom: '<"top"l>rt<"bottom"ip><"clear">'
    });
});