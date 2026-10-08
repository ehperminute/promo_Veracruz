from pathlib import Path
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "data" / "processed" / "destination_master.csv"
OUTPUT = ROOT / "site" / "data" / "destinations.json"


THEME_COLUMNS = [
    "theme_beach_coast",
    "theme_nature",
    "theme_culture_history",
    "theme_archaeology",
    "theme_adventure",
    "theme_gastronomy_coffee",
    "theme_wellness_spiritual",
    "theme_urban_services",
]


df = pd.read_csv(INPUT)


destinations = []

for _, row in df.iterrows():

    themes = []

    for theme in THEME_COLUMNS:

        if row[theme] == 1:
            themes.append(theme.removeprefix("theme_"))

    destination = {
        "name": row["destination"],
        "municipality_code": str(row["clave_municipio"]).zfill(5),
        "region": row["region_turistica_preliminar"],
        "pueblo_magico": bool(row["pueblo_magico"]),
        "themes": themes,
    }

    destinations.append(destination)


OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as file:
    json.dump(
        destinations,
        file,
        ensure_ascii=False,
        indent=2,
    )


print(f"Exported {len(destinations)} destinations to {OUTPUT}")