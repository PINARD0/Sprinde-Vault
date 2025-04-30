document.getElementById("form_modify_type").addEventListener("submit", function (event) {
    event.preventDefault();

    let formData = new FormData(this);

    fetch("/modify_hardware_type", {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let successMessage = document.getElementById('successMessage');
        let errorMessage = document.getElementById('errorMessage');

        if (data.success) {
            successMessage.classList.remove("d-none");
            setTimeout(() => {
                window.location.href = "/hardware_types";
            }, 1500);
        } else if (data.error) {
            errorMessage.classList.remove("d-none");
            setTimeout(() => {
                errorMessage.classList.add("d-none");
            }, 3000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});