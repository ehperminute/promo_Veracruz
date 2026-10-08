const THEME_KEYS = [
    "beach_coast",
    "nature",
    "culture_history",
    "archaeology",
    "adventure",
    "gastronomy_coffee",
    "wellness_spiritual",
    "urban_services"
];


let destinations = [];

let translations = {};

let currentLanguage = "en";

let openDestinationName = null;



const searchInput =
    document.getElementById(
        "destination-search"
    );


const themeFilter =
    document.getElementById(
        "theme-filter"
    );


const destinationList =
    document.getElementById(
        "destination-list"
    );


const languageSelect =
    document.getElementById(
        "language-select"
    );



/* ---------------------------------------------
   CREATE DETAIL DIALOG
--------------------------------------------- */

const destinationDialog =
    document.createElement("dialog");


destinationDialog.className =
    "destination-dialog";


document.body.appendChild(
    destinationDialog
);



/* ---------------------------------------------
   TRANSLATION
--------------------------------------------- */

function translate(key) {

    return translations[key] || key;

}



function updateStaticText() {

    const elements =
        document.querySelectorAll(
            "[data-i18n]"
        );


    elements.forEach(element => {

        const key =
            element.dataset.i18n;


        element.textContent =
            translate(key);

    });


    const placeholderElements =
        document.querySelectorAll(
            "[data-i18n-placeholder]"
        );


    placeholderElements.forEach(
        element => {

            const key =
                element.dataset.i18nPlaceholder;


            element.placeholder =
                translate(key);

        }
    );


    document.title =
        translate("title");


    document.documentElement.lang =
        currentLanguage;

}



/* ---------------------------------------------
   THEME FILTER
--------------------------------------------- */

function populateThemeFilter() {

    const previousSelection =
        themeFilter.value;


    themeFilter.innerHTML = "";


    const allOption =
        document.createElement(
            "option"
        );


    allOption.value = "";


    allOption.textContent =
        translate("all_themes");


    themeFilter.appendChild(
        allOption
    );


    THEME_KEYS.forEach(theme => {

        const option =
            document.createElement(
                "option"
            );


        option.value =
            theme;


        option.textContent =
            translate(
                `theme_${theme}`
            );


        themeFilter.appendChild(
            option
        );

    });


    themeFilter.value =
        previousSelection;

}



/* ---------------------------------------------
   THEME TAG HTML
--------------------------------------------- */

function createThemeTags(destination) {

    return destination.themes
        .map(
            theme => `

                <span class="theme-tag">

                    ${translate(
                        `theme_${theme}`
                    )}

                </span>

            `
        )
        .join("");

}



/* ---------------------------------------------
   DESTINATION DETAIL
--------------------------------------------- */

function openDestination(destination) {

    openDestinationName =
        destination.name;


    const themes =
        createThemeTags(
            destination
        );


    const puebloMagico =
        destination.pueblo_magico
            ? `

                <p class="pueblo-magico">

                    ${translate(
                        "pueblo_magico"
                    )}

                </p>

              `
            : "";


    destinationDialog.innerHTML = `

        <button
            class="dialog-close"
            id="dialog-close"
            aria-label="Close"
        >
            ×
        </button>


        <div class="detail-header">

            <h2>
                ${destination.name}
            </h2>

            <p class="detail-region">
                ${destination.region}
            </p>

            ${puebloMagico}

        </div>


        <div class="detail-section">

            <h3>
                ${translate(
                    "tourism_profile"
                )}
            </h3>


            <div class="theme-tags">

                ${themes}

            </div>

        </div>


        <div class="detail-section detail-future">

            <strong>
                ${translate(
                    "analysis_section"
                )}
            </strong>

            <p>
                ${translate(
                    "analysis_placeholder"
                )}
            </p>

        </div>

    `;


    const closeButton =
        document.getElementById(
            "dialog-close"
        );


    closeButton.addEventListener(
        "click",
        () => {

            destinationDialog.close();

        }
    );


    destinationDialog.showModal();

}



/* ---------------------------------------------
   RE-RENDER OPEN DESTINATION AFTER
   LANGUAGE CHANGE
--------------------------------------------- */

function renderOpenDestination() {

    if (!openDestinationName) {

        return;

    }


    const destination =
        destinations.find(
            item =>
                item.name ===
                openDestinationName
        );


    if (destination) {

        openDestination(
            destination
        );

    }

}



/* ---------------------------------------------
   DESTINATION CARDS
--------------------------------------------- */

function renderDestinations() {

    const searchText =
        searchInput.value
            .trim()
            .toLowerCase();


    const selectedTheme =
        themeFilter.value;


    const filtered =
        destinations.filter(
            destination => {

                const matchesSearch =
                    destination.name
                        .toLowerCase()
                        .includes(
                            searchText
                        );


                const matchesTheme =
                    selectedTheme === "" ||
                    destination.themes.includes(
                        selectedTheme
                    );


                return (
                    matchesSearch &&
                    matchesTheme
                );

            }
        );


    destinationList.innerHTML =
        "";


    if (filtered.length === 0) {

        const message =
            document.createElement(
                "p"
            );


        message.className =
            "no-results";


        message.textContent =
            translate(
                "no_results"
            );


        destinationList.appendChild(
            message
        );


        return;

    }


    filtered.forEach(
        destination => {

            const card =
                document.createElement(
                    "article"
                );


            card.className =
                "destination-card";


            card.tabIndex =
                0;


            card.setAttribute(
                "role",
                "button"
            );


            const themes =
                createThemeTags(
                    destination
                );


            const puebloMagico =
                destination.pueblo_magico
                    ? `

                        <p class="pueblo-magico">

                            ${translate(
                                "pueblo_magico"
                            )}

                        </p>

                      `
                    : "";


            card.innerHTML = `

                <h3>
                    ${destination.name}
                </h3>


                <p class="region">
                    ${destination.region}
                </p>


                <div class="theme-tags">

                    ${themes}

                </div>


                ${puebloMagico}

            `;


            card.addEventListener(
                "click",
                () => {

                    openDestination(
                        destination
                    );

                }
            );


            card.addEventListener(
                "keydown",
                event => {

                    if (
                        event.key === "Enter" ||
                        event.key === " "
                    ) {

                        event.preventDefault();


                        openDestination(
                            destination
                        );

                    }

                }
            );


            destinationList.appendChild(
                card
            );

        }
    );

}



/* ---------------------------------------------
   LOAD DESTINATION DATA
--------------------------------------------- */

async function loadDestinations() {

    const response =
        await fetch(
            "data/destinations.json"
        );


    if (!response.ok) {

        throw new Error(
            "Could not load destinations.json"
        );

    }


    destinations =
        await response.json();

}



/* ---------------------------------------------
   LOAD LANGUAGE FILE
--------------------------------------------- */

async function loadLanguage(
    language
) {

    const response =
        await fetch(
            `i18n/${language}.json`
        );


    if (!response.ok) {

        throw new Error(
            `Could not load language: ${language}`
        );

    }


    translations =
        await response.json();


    currentLanguage =
        language;


    updateStaticText();


    populateThemeFilter();


    renderDestinations();


    renderOpenDestination();

}



/* ---------------------------------------------
   EVENTS
--------------------------------------------- */

searchInput.addEventListener(
    "input",
    renderDestinations
);


themeFilter.addEventListener(
    "change",
    renderDestinations
);


languageSelect.addEventListener(
    "change",
    async event => {

        await loadLanguage(
            event.target.value
        );

    }
);



destinationDialog.addEventListener(
    "click",
    event => {

        if (
            event.target ===
            destinationDialog
        ) {

            destinationDialog.close();

        }

    }
);



destinationDialog.addEventListener(
    "close",
    () => {

        openDestinationName =
            null;

    }
);



/* ---------------------------------------------
   INITIALIZE WEBSITE
--------------------------------------------- */

async function init() {

    try {

        await loadDestinations();


        await loadLanguage(
            "en"
        );

    }

    catch (error) {

        console.error(
            error
        );


        destinationList.textContent =
            "Error loading website data.";

    }

}



init();