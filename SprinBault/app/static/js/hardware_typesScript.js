// Función para confirmar si el usuario está seguro de eliminar el tipo de hardware
/*function confirmDelete(typeId) {
    // Primer aviso de confirmación
    if (confirm("¿Estás seguro de que deseas eliminar este tipo de hardware?")) {
        // Segundo aviso que explica las consecuencias
        if (confirm("¡Atención! Se eliminarán todos los registros de hardware asociados a este tipo.")) {
            // Si el usuario confirma ambas alertas, proceder con la eliminación
            document.getElementById("deleteForm" + typeId).submit();
        }
    }
}*/

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