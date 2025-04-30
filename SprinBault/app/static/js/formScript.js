// Función para verificar la validez del correo
function validateEmail() {
    const email = document.getElementById('email').value;
    const invalidEmailMessage = document.getElementById('invalidEmailMessage');
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/; // Expresión regular para validar un correo

    // Si el correo no cumple con el patrón, mostrar mensaje de error
    if (!emailPattern.test(email)) {
        invalidEmailMessage.style.display = 'block';
        return false;  // Evitar que el formulario se envíe
    } else {
        invalidEmailMessage.style.display = 'none';
        return true;  // Permitir que el formulario se envíe
    }
}

// Verificar si 'error' está en la URL para mostrar el mensaje de credenciales inválidas
window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    const errorParam = urlParams.get('error');

    // Mostrar mensaje de error si las credenciales son inválidas
    if (errorParam === 'invalid_credentials') {
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.style.display = 'block';
        
        // Ocultar el mensaje después de 3 segundos (3000 milisegundos)
        setTimeout(function() {
            errorMessage.style.display = 'none';
        }, 3000); // 3000ms = 3 segundos
    }

    // Mostrar mensaje si el token ha expirado
    if (errorParam === 'token_expired') {
        const tokenExpiredMessage = document.getElementById('tokenExpiredMessage');
        tokenExpiredMessage.style.display = 'block';
    }

    // Mostrar mensaje si el token no fue encontrado
    if (errorParam === 'token_not_found') {
        const tokenNotFoundMessage = document.getElementById('tokenNotFoundMessage');
        tokenNotFoundMessage.style.display = 'block';
    }
}

async function checkIfLoggedIn() {
    try {
        const response = await fetch("/get-role"); // Endpoint que devuelve el estado de autenticación
        if (response.ok) {
            window.location.href = "/dashboard"; // Si el usuario ya está autenticado, redirigirlo
        }
    } catch (error) {
        console.error("No autenticado o error al verificar sesión.");
    }
}

checkIfLoggedIn();