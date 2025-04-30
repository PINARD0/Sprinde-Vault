function toggleHardware(locationCode, activate) {
    const url = activate ? `/enable_hardware/${locationCode}` : `/disable_hardware/${locationCode}`;
    
    fetch(url, { method: "POST" })
    .then(response => response.json())
    .then(data => {
        location.reload(); // Recargar la página para reflejar los cambios
    })
    .catch(error => console.error("Error:", error));
}

let locationCodeToDelete = null;

function confirmDelete(id, locationName) {
    // Guardar la información del Location Code a eliminar
    locationCodeToDelete = { id, locationName };

    // Mostrar el modal de la contraseña maestra
    document.getElementById('deleteLocationCodePassword').value = '';
    document.getElementById('deleteLocationCodeError').style.display = 'none';
    new bootstrap.Modal(document.getElementById('deleteLocationCodeModal')).show();
    
    return false; // Prevenir que se envíe el formulario de inmediato
}

async function confirmDeleteLocationCode() {
    const password = document.getElementById('deleteLocationCodePassword').value;

    const res = await fetch('/verify-master-password-bbdd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: password })
    });

    const result = await res.json();

    if (res.ok && result.valid) {
        // Contraseña válida, proceder con eliminación
        fetch(`/delete_location_code`, {
            method: 'POST',
            body: new URLSearchParams({
                'id': locationCodeToDelete.id
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                // Mostrar el mensaje de éxito
                alert(data.message);  // Mostrar el mensaje de éxito

                // Redirigir a la página de location_code
                window.location.href = data.redirect_url;
            } else {
                // Mostrar error si no fue exitosa
                alert("Error al eliminar el Location Code.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Ocurrió un problema al eliminar el Location Code.");
        });

        // Cerrar el modal
        let modal = bootstrap.Modal.getInstance(document.getElementById('deleteLocationCodeModal'));
        if (modal) modal.hide();

    } else {
        document.getElementById('deleteLocationCodeError').style.display = 'block';
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