const forms = document.querySelectorAll("form.admin"),
    spanner = document.getElementById("admin_spanner");

forms.forEach(function(form) {
    form.addEventListener("submit", async function(event) {
        event.preventDefault();
        spanner.classList.add("show");

        const formData = new FormData(form),
            method = form.method.toUpperCase(),
            url = form.getAttribute("action");

        const fetchOptions = {
            method: method,
            body: formData
        };

        await fetch(url, fetchOptions)
            .then(response => {
                return response.json();
            })
            .catch(error => { console.error("Error:", error); })

        const reload = document.createElement("form");
        reload.action = url;
        reload.method = "POST";
        reload.style.visibility = "hidden";

        document.body.appendChild(reload);
        reload.submit();
        spanner.classList.remove("show");
    });
});
