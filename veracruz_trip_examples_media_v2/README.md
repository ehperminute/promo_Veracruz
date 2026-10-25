# Veracruz trip-example media and expense preview

This additive release changes the **four editorial route examples only**, not real traveler submissions or provider offers.

### What changes
- Four location-specific photographs, referenced through Wikimedia Commons with author, license, and source links.
- Each sample card displays a **hypothetical itemized travel budget** for two people, with stops and expense categories.
- Clicking **View itinerary / Ver ruta / 旅程を見る** opens the same route and shows its photo and illustrative budget in a separate panel.
- Clicking **Use as template / Usar como plantilla** preserves the route but **does not copy fictional expenses into the user's actual spending record**.
- The traveler expense diary still accepts actual self-reported purchases as before.

Important: Photos are references depicting specific Veracruz locations/activities, **not pictures supplied by an actual traveler**. Budget entries are **hypothetical allowances**, not observed expenses, current prices, supplier bookings or receipts. Published traveler stories are preserved.

### Install

Copy the ZIP to `/workspaces/promo_Veracruz` and run:

```sh
unzip -o VERACRUZ_TRIP_EXAMPLES_PHOTOS_BUDGET_2026-10-25.zip
python veracruz_trip_examples_media_v2/install.py .
python -m unittest discover -s veracruz_trip_examples_media_v2/tests -v
node --check site/js/trip-gallery.js
node --check site/js/trip-example-budget.js
python -m http.server 8110 -d site
```

Open `/viajes.html`. A browser refresh (Ctrl+Shift+R) may be needed after deployment.

### Image credits

| Example | Photo | Author | License | Source |
|---|---|---|---|---|
| Coffee, mountains, river | Rafting Río Salvaje, Jalcomulco | Kiubu | Public domain | https://commons.wikimedia.org/wiki/File:Rafting_Rio_Salvaje.JPG |
| Totonac heritage | El Tajín | JEAFotoarte75 | CC BY-SA 4.0 | https://commons.wikimedia.org/wiki/File:El_Taj%C3%ADn_zona_arqueol%C3%B3gica_precolombina_35_Papantla_de_Olarte,_Veracruz,_M%C3%A9xico.jpg |
| Los Tuxtlas | Boats on Lake Catemaco | Koffer | CC BY-SA 3.0 | https://commons.wikimedia.org/wiki/File:Laguna_de_Catemaco_con_lanchas.jpg |
| Crafts | Clay crafts, Naolinco | B.jars | CC BY-SA 4.0 | https://commons.wikimedia.org/wiki/File:Artesan%C3%ADas_de_barro_en_Naolinco.jpg |

These images are remotely loaded from Wikimedia Commons; they are not yet downloaded into static site assets, so availability depends on Wikimedia serving them. The site shows normal card text and budgets if a remote photo is unavailable. If redistributing local derivatives of CC BY-SA images later, retain proper attribution, modification notices, and applicable share-alike terms.
