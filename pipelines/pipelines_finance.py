pipeline_plus_faible_marge = [
    {"$sort": {"marge_prix": 1}},  # Tri croissant
    {"$limit": 1},                 # Garder le premier
    {"$project": {
        "_id": 0,
        "nom_medicament": 1,
        "medicament_categorie": 1,
        "marge_prix": 1,
        "prix_unitaire": 1,
        "prix_fournisseur": 1,
        "lot_id": 1
    }}
]

pipeline_plus_forte_marge = [
    {"$sort": {"marge_prix": -1}},  # Tri décroissant
    {"$limit": 1},                  # Garder le premier
    {"$project": {
        "_id": 0,
        "nom_medicament": 1,
        "medicament_categorie": 1,
        "marge_prix": 1,
        "prix_unitaire": 1,
        "prix_fournisseur": 1,
        "lot_id": 1
    }}
]

pipeline_marge_moyenne = [
    {
        "$group": {
            "_id": None,
            "marge_moyenne": {"$avg": "$marge_prix"}
        }
    },
    {
        "$project": {
            "_id": 0,
            "marge_moyenne": 1
        }
    }
]