// Ocultar los mensajes después de 5 segundos
window.onload = function() {
    setTimeout(function() {
        let updateSuccessMessage = document.getElementById('updateSuccessMessage');
        let deleteSuccessMessage = document.getElementById('deleteSuccessMessage');
        
        if (updateSuccessMessage) updateSuccessMessage.style.display = 'none';
        if (deleteSuccessMessage) deleteSuccessMessage.style.display = 'none';
    }, 5000);
}

let formDataDeleteHardware = null;
let deleteHardwareModal = new bootstrap.Modal(document.getElementById('deleteHardwareModal'), { keyboard: true });

document.getElementById("deletePasswordForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const confirmDelete = confirm("¿Estás seguro de que deseas eliminar este hardware? Esta acción no se puede deshacer.");

    if (!confirmDelete) return;

    formDataDeleteHardware = new FormData(this);  // Guardamos datos temporalmente

    // Limpiar campos antes de mostrar
    document.getElementById('deleteHardwarePassword').value = '';
    document.getElementById('deleteHardwareError').style.display = 'none';

    // Mostrar modal ya inicializado
    deleteHardwareModal.show();

    // Dar foco al input automáticamente
    setTimeout(() => {
        document.getElementById('deleteHardwarePassword').focus();
    }, 300);
});

async function confirmDeleteHardware() {
    const password = document.getElementById('deleteHardwarePassword').value;

    const res = await fetch('/verify-master-password-bbdd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: password })
    });

    const result = await res.json();

    if (res.ok && result.valid) {
        // Contraseña válida, proceder con eliminación
        try {
            const response = await fetch('/delete_hardware', {
                method: 'POST',
                body: formDataDeleteHardware
            });

            if (!response.ok) {
                throw new Error('Fallo en la respuesta');
            }

            let data = await response.json();

            if (data.message) {
                document.getElementById("deleteMessage").innerHTML = `<p class="text-success">${data.message}</p>`;

                // Cerrar modal correctamente
                deleteHardwareModal.hide();

                // Redirigir
                setTimeout(() => {
                    window.location.href = "/modify_hardware?delete_success=true";
                }, 500);
            } else if (data.error) {
                document.getElementById("deleteMessage").innerHTML = `<p class="text-danger">${data.error}</p>`;
            } else {
                document.getElementById("deleteMessage").innerHTML = `<p class="text-danger">Respuesta inesperada del servidor.</p>`;
            }
        } catch (error) {
            console.error(error);
            document.getElementById("deleteMessage").innerHTML = `<p class="text-danger">Hubo un error al eliminar el hardware.</p>`;
        }

    } else {
        document.getElementById('deleteHardwareError').style.display = 'block';
    }
}

// Manejar la actualización de contraseñas con fetch
document.getElementById("managePasswordsForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let successMessage = document.getElementById("successMessage");
    if (!successMessage) {
        successMessage = document.createElement("div");
        successMessage.id = "successMessage";
        this.appendChild(successMessage);
    }
    successMessage.innerHTML = ''; // Limpiar mensaje previo

    let formData = new FormData(this);
    const masterPassword = document.getElementById("masterPassword").value;
    formData.append("master_password", masterPassword);

    fetch('/manage_passwords', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Respuesta del servidor:", data); // IMPRIMIR RESPUESTA

        if (data.message) {
            successMessage.innerHTML = `<p class="text-success">${data.message}</p>`;

            // Cerrar el modal correctamente
            $('#managePasswordsModal').modal('hide');

            // Redirigir con mensaje de éxito
            setTimeout(() => {
                window.location.href = "/modify_hardware?update_success=true";
            }, 500);
        } else if (data.error) {
            successMessage.innerHTML = `<p class="text-danger">${data.error}</p>`;

            // Limpiar los campos si la contraseña maestra es incorrecta
            if (data.error === "Contraseña maestra incorrecta") {
                document.querySelector('input[name="new_password"]').value = '';
                document.querySelector('input[name="confirm_new_password"]').value = '';
                document.getElementById("masterPassword").value = '';
            }
        }
    })
    .catch(error => {
        console.error("Error en la petición:", error); // IMPRIMIR ERROR
        successMessage.innerHTML = `<p class="text-danger">Hubo un error al actualizar la contraseña.</p>`;
    });
});

// Función para manejar el envío del formulario con fetch()
function handleFormSubmit(formId, successMessageId, endpoint) {
    document.getElementById(formId).addEventListener("submit", function(event) {
        event.preventDefault(); // Evitar el envío tradicional del formulario

        let formData = new FormData(this);

        fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Crear el div de éxito si no existe
            let successMessage = document.getElementById(successMessageId);
            if (!successMessage) {
                successMessage = document.createElement('div');
                successMessage.id = successMessageId;
                this.appendChild(successMessage); // Agregar al formulario o a un contenedor adecuado
            }

            if (data.message) {
                successMessage.innerHTML = `<p class="text-success">${data.message}</p>`;
                successMessage.style.display = 'block';

                // Redirigir a /hardware después de 1,5 segundos
                setTimeout(() => {
                    window.location.href = "/hardware";
                }, 1500);
            } else if (data.error) {
                successMessage.innerHTML = `<p class="text-danger">${data.error}</p>`;
                successMessage.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
}

// Activar la función para el formulario de actualización
handleFormSubmit("form_update", "success_update", "/update_hardware");