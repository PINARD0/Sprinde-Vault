// Ocultar automáticamente las alertas
window.addEventListener('DOMContentLoaded', function() {
    var alertMessage = document.getElementById("alertMessage");
    if (alertMessage) {
        setTimeout(function() {
        alertMessage.style.display = 'none';
        }, 5000);
    }
});

// Actualizar el campo de localización
document.getElementById('codeName').addEventListener('change', function() {
    var selectedOption = this.options[this.selectedIndex];
    var selectedLocationName = selectedOption.getAttribute('data-name');
    document.getElementById('localizacion').value = selectedLocationName;
});