pipeline_taux_retard = [
    {
        "$group": {
            "_id": "$fournisseur",
            "livraisons_total": {"$sum": 1},
            "livraisons_retard": {
                "$sum": {
                    "$cond": [{"$gt": ["$retard_jour", 0]}, 1, 0]
                }
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "fournisseur": "$_id",
            "livraisons_total": 1,
            "livraisons_retard": 1,
            "taux_retard_pourcent": {
                "$multiply": [
                    {"$divide": ["$livraisons_retard", "$livraisons_total"]},
                    100
                ]
            }
        }
    }
]

pipeline_retard_moyen = [
    {
        "$group": {
            "_id": "$fournisseur",
            "livraisons_total": {"$sum": 1},
            "retard_total": {"$sum": "$retard_jour"},
            "retard_moyen": {"$avg": "$retard_jour"}
        }
    },
    {
        "$project": {
            "_id": 0,
            "fournisseur": "$_id",
            "livraisons_total": 1,
            "retard_total": 1,
            "retard_moyen_jours": {"$round": ["$retard_moyen", 2]}
        }
    }
]

pipeline_nombre_commandes = [
    {
        "$group": {
            "_id": "$fournisseur",
            "nombre_commandes": { "$sum": 1 }
        }
    },
    {
        "$group": {
            "_id": None,
            "total_fournisseurs": { "$sum": 1 },
            "total_commandes": { "$sum": "$nombre_commandes" },
            "commandes_par_fournisseur": { "$push": {
                "fournisseur": "$_id",
                "nombre_commandes": "$nombre_commandes"
            }}
        }
    },
    {
        "$project": {
            "_id": 0,
            "total_fournisseurs": 1,
            "total_commandes": 1,
            "nombre_moyen_commandes_par_fournisseur": {
                "$round": [
                    { "$divide": ["$total_commandes", "$total_fournisseurs"] },
                    2
                ]
            },
            "commandes_par_fournisseur": 1
        }
    }
]




