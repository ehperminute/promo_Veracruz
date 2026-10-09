from pathlib import Path
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

S4_PROFILES_FILE = (
    ROOT / "data" / "interim" / "destination_profiles_s4.csv"
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

LABELS_FILE = (
    ROOT / "data" / "reference" / "cluster_display_labels.csv"
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
        S4_PROFILES_FILE
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

    labels_df = pd.read_csv(LABELS_FILE, dtype={"cluster": int})
    required_clusters = set(membership_df["cluster"].astype(int))
    labeled_clusters = set(labels_df["cluster"].astype(int))
    if not labels_df["cluster"].is_unique or required_clusters != labeled_clusters:
        raise ValueError("Marketing group labels must uniquely cover all active clusters")

    labels_lookup = labels_df.set_index("cluster").to_dict("index")
    for _, member in membership_df.iterrows():
        group_id = int(member["cluster"])
        if labels_lookup[group_id]["expected_medoid"] != member["cluster_medoid"]:
            raise ValueError(
                f"Cluster {group_id} changed representative destination; review its public label"
            )

    if not destinations_df["destination"].is_unique:
        raise ValueError("S4 destination profiles contain duplicate destinations")
    if set(destinations_df["destination"]) != set(membership_df["destination"]):
        raise ValueError("S4 profiles and cluster membership have different destinations")


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

        group_label = labels_lookup[cluster_id]
        name = {lang: str(group_label[f"name_{lang}"]) for lang in ("en", "es", "ja")}
        description = {
            lang: str(group_label[f"description_{lang}"]) for lang in ("en", "es", "ja")
        }
        if any(not value.strip() or value == "nan" for value in (*name.values(), *description.values())):
            raise ValueError(f"Missing translated label for cluster {cluster_id}")


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

                "name":
                    name,

                "description":
                    description,

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
        f"Exported {len(output)} destinations from refined S4 profiles"
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
