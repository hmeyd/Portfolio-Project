function fetchData() {
    const query = document.getElementById("search").value;

    fetch(`/bodacc?q=${query}`)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = "";

            if (data.error) {
                resultsDiv.innerHTML = `<p>${data.error}</p>`;
                return;
            }

            data.records.forEach(record => {
                const info = record.fields;
                const entry = document.createElement("div");
                entry.innerHTML = `
                    <h3>${info.titre || 'Annonce'}</h3>
                    <p>${info.contenu || 'Contenu non disponible'}</p>
                    <hr>
                `;
                resultsDiv.appendChild(entry);
            });
        })
        .catch(error => {
            document.getElementById("results").innerHTML = `<p>Erreur : ${error}</p>`;
        });
}
