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



function clusterName(destination) {
    return destination.cluster.name?.[currentLanguage] ||
        `${translate("cluster")} ${destination.cluster.id}`;
}


function clusterDescription(destination) {
    return destination.cluster.description?.[currentLanguage] || "";
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


        const example = destinations.find(d => d.cluster.id === cluster);
        option.textContent = example ? clusterName(example) : `${translate("cluster")} ${cluster}`;


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



// Explain the existing S4 assignment, without inventing travel or demand claims.
// We compare the displayed S4 feature flags with the actual cluster medoid.
// This is an illustration of the comparison, not a reconstruction of PAM.
function explainClusterFeatures(destination) {
    const representative = destinations.find(item => item.name === destination.cluster.medoid);
    if (!representative) {
        return `<p class="method-note">${translate("representative_unavailable")}</p>`;
    }

    const shared = destination.themes.filter(theme => representative.themes.includes(theme));
    const destinationOnly = destination.themes.filter(theme => !representative.themes.includes(theme));
    const representativeOnly = representative.themes.filter(theme => !destination.themes.includes(theme));
    const describe = themes => themes.length
        ? themes.map(theme => translate(`theme_${theme}`)).join(", ")
        : translate("no_distinct_themes");

    const magicComparison = destination.pueblo_magico && representative.pueblo_magico
        ? `<p>${translate("both_pueblos_magicos")}</p>`
        : destination.pueblo_magico !== representative.pueblo_magico
            ? `<p>${translate("pueblo_status_differs")}</p>`
            : "";

    return `
        <details class="why-group">
            <summary>${translate("why_group_heading")}</summary>
            <p>${translate("comparison_intro")} <strong>${representative.name}</strong>.</p>
            <dl class="feature-comparison">
                <div><dt>${translate("shared_themes")}</dt><dd>${describe(shared)}</dd></div>
                <div><dt>${translate("only_selected")}</dt><dd>${describe(destinationOnly)}</dd></div>
                <div><dt>${translate("only_representative")}</dt><dd>${describe(representativeOnly)}</dd></div>
            </dl>
            ${magicComparison}
            <p class="method-note">${translate("comparison_limit")}</p>
        </details>
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
        <button class="dialog-close" id="dialog-close" aria-label="Close">×</button>
        <div class="detail-header">
            <h2>${destination.name}</h2>
            <p class="detail-region">${destination.region}</p>
            ${puebloMagico}
        </div>
        <div class="detail-section">
            <h3>${translate("tourism_profile")}</h3>
            <div class="theme-tags">${themes}</div>
        </div>
        <div class="detail-section">
            <h3>${clusterName(destination)}</h3>
            <p class="cluster-description">${clusterDescription(destination)}</p>
            <h4>${translate("more_in_experience")}</h4>
            <div class="member-tags">${members}</div>
            <p class="method-note">${translate("groups_not_routes")}</p>
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

                        ${clusterName(destination)}

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
            "data/destinations.json?v=7"
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
            `i18n/${language}.json?v=7`
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

    renderExperienceGallery();

    renderAlgorithmDemo();

    renderOpenDestination();

}




// Visual experience groups use the published cluster assignments and translated
// editorial names. Counts and common tags are computed from the same S4 JSON.
const EXPERIENCE_SYMBOLS = {
    beach_coast: "🏖️", nature: "🌿", culture_history: "🏛️",
    archaeology: "🏺", adventure: "🥾", gastronomy_coffee: "☕",
    wellness_spiritual: "✨", urban_services: "🏙️"
};

function renderExperienceGallery() {
    const gallery = document.getElementById("experience-gallery");
    if (!gallery) return;
    gallery.replaceChildren();
    const ids = [...new Set(destinations.map(d => d.cluster.id))].sort((a,b) => a-b);
    for (const id of ids) {
        const members = destinations.filter(d => d.cluster.id === id);
        const label = clusterName(members[0]);
        const counts = THEME_KEYS.map(key => ({key, n: members.filter(d => d.themes.includes(key)).length}))
            .filter(item => item.n > 0).sort((a,b) => b.n - a.n || THEME_KEYS.indexOf(a.key)-THEME_KEYS.indexOf(b.key));
        const representative = members.find(d => d.name === members[0].cluster.medoid) || members[0];
        const card = document.createElement('button');
        card.type = 'button'; card.className = 'experience-card';
        const icon = document.createElement('span'); icon.className = 'experience-symbol';
        icon.textContent = EXPERIENCE_SYMBOLS[counts[0]?.key] || '📍';
        const head = document.createElement('strong'); head.className = 'experience-name'; head.textContent = label;
        const count = document.createElement('span'); count.className = 'experience-count';
        count.textContent = `${members.length} ${translate('group_places')}`;
        const tags = document.createElement('span'); tags.className = 'experience-themes';
        tags.textContent = counts.slice(0, 3).map(item => translate(`theme_${item.key}`)).join(' · ');
        const example = document.createElement('span'); example.className = 'experience-example';
        example.textContent = `${translate('example_places')}: ${members.slice(0,3).map(d=>d.name).join(', ')}`;
        const cta = document.createElement('span'); cta.className = 'experience-cta';
        cta.textContent = `${translate('group_show')} →`;
        card.append(icon, head, count, tags, example, cta);
        card.addEventListener('click', () => {
            searchInput.value = ''; themeFilter.value = '';
            clusterFilter.value = String(id);
            renderDestinations();
            document.getElementById('destinations').scrollIntoView({behavior:'smooth',block:'start'});
        });
        gallery.append(card);
    }
}

// Matches scripts/mining/common.py for the active nine S4 clustering features:
// eight asymmetric binary tourism themes and one symmetric Pueblo Mágico flag.
function explainPair(a,b) {
    let different = 0, comparable = 0;
    const rows = THEME_KEYS.map(key => {
        const aa = a.themes.includes(key), bb = b.themes.includes(key);
        const considered = aa || bb;
        if (considered) { comparable += 1; if (aa !== bb) different += 1; }
        return {key, aa, bb, considered, different:aa !== bb};
    });
    const mag = a.pueblo_magico !== b.pueblo_magico;
    comparable += 1; if (mag) different += 1;
    rows.push({key:'magic',aa:a.pueblo_magico,bb:b.pueblo_magico,considered:true,different:mag});
    return {different,comparable,distance:different/comparable,rows};
}
function fmtCost(x) { return x.toFixed(3); }
function updateDistanceDemo() {
    const a = destinations.find(d => d.name === document.getElementById('demo-a').value);
    const b = destinations.find(d => d.name === document.getElementById('demo-b').value);
    if (!a || !b) return;
    const result = explainPair(a,b);
    const place = document.getElementById('demo-distance');
    place.replaceChildren();
    const value = document.createElement('div'); value.className = 'distance-value';
    const heading = document.createElement('span'); heading.textContent = translate('compare_result');
    const number = document.createElement('strong'); number.textContent = `${result.different} / ${result.comparable} = ${fmtCost(result.distance)}`;
    const expl = document.createElement('p'); expl.textContent = translate('compare_explanation');
    value.append(heading,number,expl); place.append(value);
    const rows = document.getElementById('demo-comparison'); rows.replaceChildren();
    for (const item of result.rows) {
        const line = document.createElement('div'); line.className = 'compare-row';
        const feature = document.createElement('strong');
        feature.textContent = item.key === 'magic' ? translate('compare_magic') : translate(`theme_${item.key}`);
        const flags = document.createElement('span');
        flags.textContent = `${a.name}: ${item.aa?translate('compare_yes'):translate('compare_no')} · ${b.name}: ${item.bb?translate('compare_yes'):translate('compare_no')}`;
        const state = document.createElement('span'); state.className = item.considered ? (item.different?'compare-diff':'compare-match'):'compare-excluded';
        state.textContent = !item.considered?translate('compare_skip'):(item.different?translate('compare_different'):translate('compare_same'));
        line.append(feature,flags,state); rows.append(line);
    }
}
function computeMiniPam() {
    const names = ['Catemaco','Calcahualco','Coatepec','Papantla'];
    const items = names.map(name => destinations.find(d => d.name === name));
    if (items.some(x=>!x)) return null;
    const d = items.map(a=>items.map(b=>explainPair(a,b).distance));
    const score = medoids => d.reduce((sum,row)=> sum+ Math.min(...medoids.map(k=>row[k])),0);
    const sumDistances = d.map(row=>row.reduce((a,b)=>a+b,0));
    let first = 0;
    for (let i=1;i<4;i++) if (sumDistances[i]<sumDistances[first]-1e-12) first=i;
    let second=null,secondCost=Infinity;
    for (let i=0;i<4;i++) { if (i===first) continue; const c=score([first,i]);
       if(c<secondCost-1e-12 || (Math.abs(c-secondCost)<=1e-12 && (second===null||i<second))){second=i;secondCost=c;}}
    let meds=[first,second].sort((a,b)=>a-b), cost=score(meds), swaps=[];
    for(let iter=0;iter<100;iter++) {
        let best=null,bestCost=cost;
        for(const old of meds) for(let neu=0;neu<4;neu++) {
            if(meds.includes(neu)) continue;
            const proposed=meds.map(x=>x===old?neu:x).sort((a,b)=>a-b), c=score(proposed);
            if(c<bestCost-1e-10) {best=proposed;bestCost=c;}
        }
        if(!best) break;
        swaps.push({from:meds.map(i=>names[i]).join(', '),to:best.map(i=>names[i]).join(', '),cost:bestCost});
        meds=best;cost=bestCost;
    }
    const assign=items.map((item,i)=>({name:item.name,medoid:names[meds[d[i][meds[0]]<=d[i][meds[1]]?0:1]],distance:Math.min(...meds.map(j=>d[i][j]))}));
    return {names,first,sumDistances,second,secondCost,meds,swaps,cost,assign};
}
function renderMiniPam() {
    const panel=document.getElementById('demo-pam'); panel.replaceChildren();
    const x=computeMiniPam(); if(!x) {panel.textContent=translate('lab_missing');return;}
    const steps=[
        [translate('pam_step1'),`${x.names[x.first]} · ${translate('pam_cost')}: ${fmtCost(x.sumDistances[x.first])}`,translate('pam_step1_desc')],
        [translate('pam_step2'),`${x.names[x.second]} · ${translate('pam_cost')}: ${fmtCost(x.secondCost)}`,translate('pam_step2_desc')],
        [translate('pam_step3'),x.swaps.length?x.swaps.map(y=>`${y.from} → ${y.to} (${fmtCost(y.cost)})`).join(' ; '):translate('pam_no_swap'),translate('pam_step3_desc')],
        [translate('pam_final'),`${x.meds.map(i=>x.names[i]).join(' + ')} · ${translate('pam_cost')}: ${fmtCost(x.cost)}`,x.assign.map(o=>`${o.name} → ${o.medoid} (${fmtCost(o.distance)})`).join(' · ')]
    ];
    for(const [heading,data,description] of steps){
        const article=document.createElement('div');article.className='pam-step';
        const h=document.createElement('strong');h.textContent=heading;
        const p=document.createElement('p');p.textContent=description;
        const output=document.createElement('div');output.className='pam-value';output.textContent=data;
        article.append(h,p,output);panel.append(article);
    }
}
function renderAlgorithmDemo() {
    const a=document.getElementById('demo-a'), b=document.getElementById('demo-b');
    if (!a||!b||!destinations.length) return;
    const valueA=a.value||'Catemaco',valueB=b.value||'Calcahualco';
    for(const el of [a,b]){
        el.replaceChildren();
        for(const item of [...destinations].sort((x,y)=>x.name.localeCompare(y.name))){
            const option=document.createElement('option');option.value=item.name;option.textContent=item.name;el.append(option);
        }
    }
    a.value=valueA;b.value=valueB;
    if(!a.value) a.selectedIndex=0;if(!b.value)b.selectedIndex=1;
    updateDistanceDemo();renderMiniPam();
}
document.getElementById('demo-a').addEventListener('change', updateDistanceDemo);
document.getElementById('demo-b').addEventListener('change', updateDistanceDemo);

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
