$('#passwordModal').on('hidden.bs.modal', function () {
    document.getElementById("hardwarePasswordDisplay").textContent = '';
    document.getElementById("masterPassword").value = '';
});

let selectedHardwareId = null;

function openModal(hardwareId) {
    selectedHardwareId = Number(hardwareId);
    $('#passwordModal').modal('show');
}

async function sendPassword() {
    const password = document.getElementById('masterPassword').value;
    const displayElement = document.getElementById("hardwarePasswordDisplay");

    try {
        const response = await fetch('/verify-master-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: password, hardware_id: selectedHardwareId })
        });

        const data = await response.json();
        document.getElementById("masterPassword").value = "";

        if (response.ok && data.hardware_password) {
            displayElement.style.color = '#0056b3';
            displayElement.innerHTML = `<strong>Contraseña de Hardware:</strong> <span style="color: black;">${data.hardware_password}</span>`;
        } else {
            displayElement.style.color = 'red';
            displayElement.textContent = data.message || 'Contraseña maestra incorrecta';
        }

    } catch (error) {
        displayElement.style.color = 'red';
        displayElement.textContent = 'Error inesperado al verificar la contraseña.';
    }
}

const modalElement = document.getElementById("passwordModal");
modalElement.addEventListener('click', function(event) {
    if (event.target === modalElement) {
    }
});

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