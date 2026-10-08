fetch("data/destinations.json")
    .then(response => response.json())
    .then(destinations => {

        const select = document.getElementById("destination-select");
        const details = document.getElementById("destination-details");

        destinations.forEach(destination => {

            const option = document.createElement("option");

            option.value = destination.name;
            option.textContent = destination.name;

            select.appendChild(option);
        });


        select.addEventListener("change", () => {

            const selectedName = select.value;

            const destination = destinations.find(
                item => item.name === selectedName
            );


            if (!destination) {
                details.innerHTML = "";
                return;
            }


            details.innerHTML = `
                <h3>${destination.name}</h3>

                <p>
                    <strong>Region:</strong>
                    ${destination.region}
                </p>

                <p>
                    <strong>Pueblo Mágico:</strong>
                    ${destination.pueblo_magico ? "Yes" : "No"}
                </p>

                <p>
                    <strong>Tourism themes:</strong>
                    ${destination.themes.join(", ")}
                </p>
            `;
        });

    });

    const languageSelect = document.getElementById("language-select");

async function loadLanguage(language) {

    const response = await fetch(`i18n/${language}.json`);

    const translations = await response.json();

    const elements = document.querySelectorAll("[data-i18n]");

    elements.forEach(element => {

        const key = element.dataset.i18n;

        element.textContent = translations[key];

    });
}

languageSelect.addEventListener("change", event => {

    loadLanguage(event.target.value);

});

loadLanguage("en");