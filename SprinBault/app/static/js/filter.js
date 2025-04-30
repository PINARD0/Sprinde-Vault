// Función para filtrar por ID
function filterByID() {
    let input = document.getElementById("idFilter").value.toLowerCase();
    let table = document.getElementById("dataTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) { // Empezamos en 1 para evitar la cabecera
        let cell = rows[i].getElementsByTagName("td")[0]; // ID está en la primera columna
        if (cell) {
            let textValue = cell.textContent || cell.innerText;
            rows[i].style.display = textValue.toLowerCase().includes(input) ? "" : "none";
        }
    }
}

// Función para filtrar por nombre
function filterByName() {
    let input = document.getElementById("nameFilter").value.toLowerCase();
    let table = document.getElementById("dataTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) { // Empezamos en 1 para evitar la cabecera
        let cell = rows[i].getElementsByTagName("td")[3]; // Nombre está en la cuarta columna
        if (cell) {
            let textValue = cell.textContent || cell.innerText;
            rows[i].style.display = textValue.toLowerCase().includes(input) ? "" : "none";
        }
    }
}

// Función para filtrar por nombre de tipo de hardware
function filterByHwName() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("nameFilter");
    filter = input.value.toUpperCase();
    table = document.getElementById("dataTable");
    tr = table.getElementsByTagName("tr");

    for (i = 1; i < tr.length; i++) {  // Comienza en 1 para no filtrar el encabezado
        td = tr[i].getElementsByTagName("td")[1]; // Filtra por la segunda columna (Nombre)
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().startsWith(filter)) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }       
    }
}

// Función para filtrar por localización
function filterByLocation() {
    let selectedLocation = document.getElementById("locationFilter").value.toLowerCase();
    let rows = document.querySelectorAll("#dataTable tbody tr");

    rows.forEach(row => {
        let location = row.cells[4].textContent.toLowerCase(); // Columna de Localización
        row.style.display = (selectedLocation === "" || location === selectedLocation) ? "" : "none";
    });
}

// Función para filtrar por CodeName
function filterByCodeName() {
    let input = document.getElementById("codeNameFilter").value.toLowerCase();
    let table = document.getElementById("dataTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) { // Empezamos en 1 para evitar la cabecera
        let cell = rows[i].getElementsByTagName("td")[1]; // CodeName está en la segunda columna
        if (cell) {
            let textValue = cell.textContent || cell.innerText;
            rows[i].style.display = textValue.toLowerCase().includes(input) ? "" : "none";
        }
    }
}

// Función para filtrar por correo
function filterByEmail() {
    let input = document.getElementById("emailFilter").value.toLowerCase();
    let table = document.getElementById("dataTable");
    let rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) { // Empezamos en 1 para evitar la cabecera
        let cell = rows[i].getElementsByTagName("td")[1]; // Correo está en la tercera columna (ajusta si es diferente)
        if (cell) {
            let textValue = cell.textContent || cell.innerText;
            rows[i].style.display = textValue.toLowerCase().includes(input) ? "" : "none";
        }
    }
}

// Función para filtrar por grupo de correos
function filterByGroup() {
    let selectedGroup = document.getElementById("groupFilter").value.toLowerCase();
    let rows = document.querySelectorAll("#dataTable tbody tr");

    rows.forEach(row => {
        let group = row.cells[2].textContent.toLowerCase();
        row.style.display = selectedGroup === "" || group === selectedGroup ? "" : "none";
    });
}

// Función para filtrar por tipo de hardware
function filterByHardwareType() {
    let selectedType = document.getElementById("hardwareTypeFilter").value.toLowerCase();
    let rows = document.querySelectorAll("#dataTable tbody tr");

    rows.forEach(row => {
        let type = row.cells[5].textContent.toLowerCase(); // Columna de Tipo de Hardware
        row.style.display = (selectedType === "" || type === selectedType) ? "" : "none";
    });
}

// Función para filtrar por nombre de Location Code
function filterByLocName() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("nameFilter");
    filter = input.value.toLowerCase();
    table = document.getElementById("dataTable");
    tr = table.getElementsByTagName("tr");

    for (i = 1; i < tr.length; i++) {  // Comenzar desde 1 para evitar la cabecera
        td = tr[i].getElementsByTagName("td")[1];  // Columna "name" (segunda columna)
        if (td) {
            txtValue = td.textContent || td.innerText;
            // Usar startsWith para filtrar por los nombres que comienzan con el valor ingresado
            if (txtValue.toLowerCase().startsWith(filter)) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}