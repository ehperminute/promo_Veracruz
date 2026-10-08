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


const clusterFilter =
    document.getElementById(
        "cluster-filter"
    );


const destinationList =
    document.getElementById(
        "destination-list"
    );


const languageSelect =
    document.getElementById(
        "language-select"
    );



const destinationDialog =
    document.createElement(
        "dialog"
    );


destinationDialog.className =
    "destination-dialog";


document.body.appendChild(
    destinationDialog
);



function translate(key) {

    return translations[key] || key;

}



function updateStaticText() {

    document
        .querySelectorAll(
            "[data-i18n]"
        )
        .forEach(element => {

            const key =
                element.dataset.i18n;

            element.textContent =
                translate(key);

        });


    document
        .querySelectorAll(
            "[data-i18n-placeholder]"
        )
        .forEach(element => {

            const key =
                element.dataset.i18nPlaceholder;

            element.placeholder =
                translate(key);

        });


    document.title =
        translate("title");


    document.documentElement.lang =
        currentLanguage;

}



function populateThemeFilter() {

    const previous =
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
        previous;

}



function populateClusterFilter() {

    const previous =
        clusterFilter.value;


    const clusters =
        [
            ...new Set(
                destinations.map(
                    destination =>
                        destination.cluster.id
                )
            )
        ].sort(
            (a, b) => a - b
        );


    clusterFilter.innerHTML =
        "";


    const allOption =
        document.createElement(
            "option"
        );


    allOption.value = "";

    allOption.textContent =
        translate(
            "all_clusters"
        );


    clusterFilter.appendChild(
        allOption
    );


    clusters.forEach(cluster => {

        const option =
            document.createElement(
                "option"
            );


        option.value =
            String(cluster);


        option.textContent =
            `${translate("cluster")} ${cluster}`;


        clusterFilter.appendChild(
            option
        );

    });


    clusterFilter.value =
        previous;

}



function createThemeTags(
    destination
) {

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



function createMemberTags(
    destination
) {

    return destination.cluster.members
        .map(
            member => `
                <span class="member-tag">
                    ${member}
                </span>
            `
        )
        .join("");

}



function createStructuralAnalogues(
    destination
) {

    if (
        destination
            .structural_analogues
            .length === 0
    ) {

        return `
            <p class="muted">
                ${translate(
                    "no_structural_analogues"
                )}
            </p>
        `;

    }


    const items =
        destination
            .structural_analogues
            .map(analogue => {

                const percentage =
                    (
                        analogue.similarity *
                        100
                    ).toFixed(1);


                return `
                    <li>
                        <strong>
                            ${analogue.name}
                        </strong>

                        <span class="analogue-score">
                            ${percentage}%
                        </span>
                    </li>
                `;

            })
            .join("");


    return `
        <ul class="analogue-list">
            ${items}
        </ul>

        <p class="method-note">
            ${translate(
                "structural_note"
            )}
        </p>
    `;

}



function openDestination(
    destination
) {

    openDestinationName =
        destination.name;


    const themes =
        createThemeTags(
            destination
        );


    const members =
        createMemberTags(
            destination
        );


    const analogues =
        createStructuralAnalogues(
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


    const silhouette =
        destination.cluster.silhouette
            .toFixed(3);


    const medoidDistance =
        destination.cluster
            .distance_to_medoid
            .toFixed(3);


    const borderline =
        destination.cluster.borderline
            ? `
                <span class="borderline-label">
                    ${translate(
                        "borderline"
                    )}
                </span>
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


        <div class="detail-section">

            <h3>
                ${translate(
                    "local_similarity_group"
                )}
            </h3>


            <p class="cluster-large">

                ${translate("cluster")}
                ${destination.cluster.id}

            </p>


            <div class="detail-stats">

                <div>

                    <span>
                        ${translate(
                            "representative_destination"
                        )}
                    </span>

                    <strong>
                        ${destination.cluster.medoid}
                    </strong>

                </div>


                <div>

                    <span>
                        ${translate(
                            "group_size"
                        )}
                    </span>

                    <strong>
                        ${destination.cluster.size}
                    </strong>

                </div>


                <div>

                    <span>
                        ${translate(
                            "distance_to_medoid"
                        )}
                    </span>

                    <strong>
                        ${medoidDistance}
                    </strong>

                </div>


                <div>

                    <span>
                        ${translate(
                            "silhouette"
                        )}
                    </span>

                    <strong>
                        ${silhouette}
                    </strong>

                    ${borderline}

                </div>

            </div>


            <h4>
                ${translate(
                    "cluster_members"
                )}
            </h4>

            <div class="member-tags">
                ${members}
            </div>


            <p class="method-note">

                ${translate(
                    "cluster_note"
                )}

            </p>

        </div>


        <div class="detail-section">

            <h3>
                ${translate(
                    "structural_analogues"
                )}
            </h3>

            ${analogues}

        </div>

    `;


    document
        .getElementById(
            "dialog-close"
        )
        .addEventListener(
            "click",
            () => {

                destinationDialog.close();

            }
        );


    if (!destinationDialog.open) {

        destinationDialog.showModal();

    }

}



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



function renderDestinations() {

    const searchText =
        searchInput.value
            .trim()
            .toLowerCase();


    const selectedTheme =
        themeFilter.value;


    const selectedCluster =
        clusterFilter.value;


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


                const matchesCluster =
                    selectedCluster === "" ||
                    String(
                        destination.cluster.id
                    ) === selectedCluster;


                return (
                    matchesSearch &&
                    matchesTheme &&
                    matchesCluster
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


            card.tabIndex = 0;

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

                <div class="card-heading">

                    <h3>
                        ${destination.name}
                    </h3>

                    <span class="cluster-badge">

                        ${translate("cluster")}
                        ${destination.cluster.id}

                    </span>

                </div>


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



async function loadDestinations() {

    const response =
        await fetch(
            "data/destinations.json?v=4"
        );


    if (!response.ok) {

        throw new Error(
            "Could not load destinations.json"
        );

    }


    destinations =
        await response.json();

}



async function loadLanguage(
    language
) {

    const response =
        await fetch(
            `i18n/${language}.json?v=4`
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

    populateClusterFilter();

    renderDestinations();

    renderOpenDestination();

}



searchInput.addEventListener(
    "input",
    renderDestinations
);


themeFilter.addEventListener(
    "change",
    renderDestinations
);


clusterFilter.addEventListener(
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

        openDestinationName = null;

    }
);



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