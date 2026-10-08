from pathlib import Path
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

DESTINATIONS_FILE = (
    ROOT / "data" / "processed" / "destination_master.csv"
)

MEMBERSHIP_FILE = (
    ROOT
    / "outputs"
    / "mining"
    / "clustering"
    / "cluster_membership.csv"
)

PROFILES_FILE = (
    ROOT
    / "outputs"
    / "mining"
    / "clustering"
    / "cluster_profiles.csv"
)

SILHOUETTES_FILE = (
    ROOT
    / "outputs"
    / "mining"
    / "clustering"
    / "destination_silhouettes.csv"
)

SIMILARITY_FILE = (
    ROOT
    / "outputs"
    / "mining"
    / "similarity"
    / "undermeasured_anchor_similarity.csv"
)

OUTPUT_FILE = (
    ROOT
    / "site"
    / "data"
    / "destinations.json"
)


THEME_COLUMNS = {
    "theme_beach_coast": "beach_coast",
    "theme_nature": "nature",
    "theme_culture_history": "culture_history",
    "theme_archaeology": "archaeology",
    "theme_adventure": "adventure",
    "theme_gastronomy_coffee": "gastronomy_coffee",
    "theme_wellness_spiritual": "wellness_spiritual",
    "theme_urban_services": "urban_services",
}


def split_members(value):
    if pd.isna(value):
        return []

    return [
        item.strip()
        for item in str(value).split("|")
        if item.strip()
    ]


def main():

    destinations_df = pd.read_csv(
        DESTINATIONS_FILE
    )

    membership_df = pd.read_csv(
        MEMBERSHIP_FILE
    )

    profiles_df = pd.read_csv(
        PROFILES_FILE
    )

    silhouettes_df = pd.read_csv(
        SILHOUETTES_FILE
    )

    similarity_df = pd.read_csv(
        SIMILARITY_FILE
    )


    membership_lookup = (
        membership_df
        .set_index("destination")
        .to_dict("index")
    )


    silhouette_lookup = (
        silhouettes_df
        .set_index("destination")
        .to_dict("index")
    )


    profile_lookup = {
        int(row["cluster"]): row
        for _, row in profiles_df.iterrows()
    }


    similarity_lookup = {}

    for destination, group in similarity_df.groupby(
        "target_destination"
    ):

        group = group.sort_values(
            "similarity_rank"
        )

        similarity_lookup[destination] = [
            {
                "name": row["anchor_destination"],
                "rank": int(
                    row["similarity_rank"]
                ),
                "similarity": float(
                    row[
                        "gower_structural_similarity"
                    ]
                ),
            }
            for _, row in group.iterrows()
        ]


    output = []


    for _, row in destinations_df.iterrows():

        destination_name = row["destination"]


        themes = [
            public_name
            for column_name, public_name
            in THEME_COLUMNS.items()
            if row[column_name] == 1
        ]


        membership = membership_lookup[
            destination_name
        ]

        silhouette_data = silhouette_lookup[
            destination_name
        ]


        cluster_id = int(
            membership["cluster"]
        )


        profile = profile_lookup[
            cluster_id
        ]


        municipality_code = str(
            int(row["clave_municipio"])
        ).zfill(5)


        record = {

            "name":
                destination_name,

            "municipality_code":
                municipality_code,

            "region":
                row[
                    "region_turistica_preliminar"
                ],

            "pueblo_magico":
                bool(
                    row["pueblo_magico"] == 1
                ),

            "themes":
                themes,

            "model_role":
                row["model_role_v1"],

            "cluster": {

                "id":
                    cluster_id,

                "medoid":
                    membership[
                        "cluster_medoid"
                    ],

                "distance_to_medoid":
                    float(
                        membership[
                            "distance_to_medoid"
                        ]
                    ),

                "silhouette":
                    float(
                        silhouette_data[
                            "silhouette"
                        ]
                    ),

                "borderline":
                    bool(
                        silhouette_data[
                            "borderline"
                        ]
                    ),

                "size":
                    int(
                        profile[
                            "n_destinations"
                        ]
                    ),

                "dominant_region":
                    profile[
                        "dominant_region"
                    ],

                "members":
                    split_members(
                        profile["members"]
                    ),
            },

            "structural_analogues":
                similarity_lookup.get(
                    destination_name,
                    []
                ),
        }


        output.append(
            record
        )


    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2
        )


    print(
        f"Exported {len(output)} destinations"
    )

    print(
        f"Clusters: "
        f"{membership_df['cluster'].nunique()}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()