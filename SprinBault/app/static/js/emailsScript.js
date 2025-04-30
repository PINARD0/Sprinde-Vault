let selectedEmailId = null;

function openModal(emailId) {
    selectedEmailId = Number(emailId);
    $('#passwordModal').modal('show');
}

async function sendPassword() {
    const password = document.getElementById('masterPassword').value;
    const displayElement = document.getElementById("emailPasswordDisplay");

    try {
        const response = await fetch('/verify-master-password-emails', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: password, email_id: selectedEmailId })
        });

        document.getElementById("masterPassword").value = "";

        if (response.ok) {
            const data = await response.json();
            displayElement.style.color = '#0056b3';
            displayElement.innerHTML = `<strong>Contraseña del Email:</strong> <span style="color: black;">${data.email_password}</span>`;
        } else {
            displayElement.style.color = 'red';
            displayElement.textContent = 'Contraseña maestra incorrecta';
        }

    } catch (error) {
        displayElement.style.color = 'red';
        displayElement.textContent = 'Error inesperado al verificar la contraseña.';
    }
}

// Limpiar modal al cerrarse (Bootstrap 4)
$('#passwordModal').on('hidden.bs.modal', function () {
    document.getElementById("emailPasswordDisplay").textContent = '';
    document.getElementById("masterPassword").value = '';
});

let formDataDeleteEmail = null;

function deleteEmail(emailId) {
    // Guardamos el emailId temporalmente y mostramos el modal
    formDataDeleteEmail = { emailId };
    document.getElementById('deleteEmailPassword').value = '';
    document.getElementById('deleteEmailError').style.display = 'none';
    new bootstrap.Modal(document.getElementById('deleteEmailModal')).show();
}

async function confirmDeleteEmail() {
    const password = document.getElementById('deleteEmailPassword').value;

    const res = await fetch('/verify-master-password-bbdd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: password })
    });

    const result = await res.json();

    if (res.ok && result.valid) {
        // Contraseña válida, proceder con eliminación
        fetch(`/delete_email/${formDataDeleteEmail.emailId}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (response.ok) {
                // Recargar la página si se eliminó correctamente
                location.reload();
            } else {
                alert("Error al eliminar el email.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Ocurrió un problema al eliminar el email.");
        });

        // Cerrar el modal
        let modal = bootstrap.Modal.getInstance(document.getElementById('deleteEmailModal'));
        if (modal) modal.hide();

    } else {
        document.getElementById('deleteEmailError').style.display = 'block';
    }
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