pipeline_top_vendeurs = [
    {
        "$group": {
            "_id": "$id_employe",
            "total_quantite_vendue": { "$sum": "$quantite" }
        }
    },
    {
        "$sort": { "total_quantite_vendue": -1 }
    },
    {
        "$limit": 3
    },
    {
        "$lookup": {
            "from": "employe",
            "localField": "_id",
            "foreignField": "id_employe",
            "as": "employe_info"
        }
    },
    { "$unwind": "$employe_info" },
    {
        "$project": {
            "_id": 0,
            "id_employe": "$_id",
            "nom": "$employe_info.nom",
            "prenom": "$employe_info.prenom",
            "fonction": "$employe_info.fonction",
            "total_quantite_vendue": 1
        }
    }
]

pipeline_vendeurs_non_habilite = [
    {
        "$group": {
            "_id": "$id_employe",
            "total_quantite_vendue": { "$sum": "$quantite" }
        }
    },
    {
        "$sort": { "total_quantite_vendue": 1 }
    },
    {
        "$limit":3
    },
    {
        "$lookup": {
            "from": "employe",
            "localField": "_id",
            "foreignField": "id_employe",
            "as": "employe_info"
        }
    },
    { "$unwind": "$employe_info" },
    {
        "$project": {
            "_id": 0,
            "id_employe": "$_id",
            "nom": "$employe_info.nom",
            "prenom": "$employe_info.prenom",
            "fonction": "$employe_info.fonction",
            "total_quantite_vendue": 1
        }
    }
]

pipeline_medicaments_plus_vendus = [
    {
        "$group": {
            "_id": "$id_medicament",
            "quantite_totale_vendue": { "$sum": "$quantite" }
        }
    },
    { "$sort": { "quantite_totale_vendue": -1 } },
    { "$limit": 3 },
    {
        "$lookup": {
            "from": "medicament",
            "localField": "_id",
            "foreignField": "id_medicament",
            "as": "medicament_info"
        }
    },
    { "$unwind": "$medicament_info" },
    {
        "$project": {
            "_id": 0,
            "id_medicament": "$_id",
            "nom": "$medicament_info.nom",
            "categorie": "$medicament_info.categorie",
            "quantite_totale_vendue": 1
        }
    }
]

pipeline_medicaments_moins_vendus = [
    {
        "$group": {
            "_id": "$id_medicament",
            "quantite_totale_vendue": { "$sum": "$quantite" }
        }
    },
    { "$sort": { "quantite_totale_vendue": 1 } },
    { "$limit": 3 },
    {
        "$lookup": {
            "from": "medicament",
            "localField": "_id",
            "foreignField": "id_medicament",
            "as": "medicament_info"
        }
    },
    { "$unwind": "$medicament_info" },
    {
        "$project": {
            "_id": 0,
            "id_medicament": "$_id",
            "nom": "$medicament_info.nom",
            "categorie": "$medicament_info.categorie",
            "quantite_totale_vendue": 1
        }
    }
]

pipeline_medicament_plus_cher = [
    { "$sort": { "prix_unitaire": -1 } },
    { "$limit": 1 },
    {
        "$project": {
            "_id": 0,
            "id_medicament": 1,
            "nom": 1,
            "categorie": 1,
            "prix_unitaire": 1
        }
    }
]

pipeline_medicament_moins_cher = [
    { "$sort": { "prix_unitaire": 1 } },
    { "$limit": 1 },
    {
        "$project": {
            "_id": 0,
            "id_medicament": 1,
            "nom": 1,
            "categorie": 1,
            "prix_unitaire": 1
        }
    }
]

pipeline_medicament_plus_rentable = [
    {
        "$lookup": {
            "from": "medicament",
            "localField": "id_medicament",
            "foreignField": "id_medicament",
            "as": "medicament_info"
        }
    },
    { "$unwind": "$medicament_info" },
    {
        "$project": {
            "id_medicament": 1,
            "quantite": 1,
            "prix_unitaire": "$medicament_info.prix_unitaire",
            "nom": "$medicament_info.nom",
            "revenu": { "$multiply": ["$quantite", "$medicament_info.prix_unitaire"] }
        }
    },
    {
        "$group": {
            "_id": "$id_medicament",
            "nom": { "$first": "$nom" },
            "revenu_total": { "$sum": "$revenu" }
        }
    },
    { "$sort": { "revenu_total": -1 } },
    { "$limit": 1 }
]

pipeline_medicament_moins_rentable = [
    {
        "$lookup": {
            "from": "medicament",
            "localField": "id_medicament",
            "foreignField": "id_medicament",
            "as": "medicament_info"
        }
    },
    { "$unwind": "$medicament_info" },
    {
        "$project": {
            "id_medicament": 1,
            "quantite": 1,
            "prix_unitaire": "$medicament_info.prix_unitaire",
            "nom": "$medicament_info.nom",
            "revenu": { "$multiply": ["$quantite", "$medicament_info.prix_unitaire"] }
        }
    },
    {
        "$group": {
            "_id": "$id_medicament",
            "nom": { "$first": "$nom" },
            "revenu_total": { "$sum": "$revenu" }
        }
    },
    { "$sort": { "revenu_total": 1 } },
    { "$limit": 1 }
]

pipeline_overview_medicament_vente = [
    {
        "$lookup": {
            "from": "medicament",
            "localField": "id_medicament",
            "foreignField": "id_medicament",
            "as": "medicament_info"
        }
    },
    {
        "$unwind": {
            "path": "$medicament_info",
            "preserveNullAndEmptyArrays": True  # Pour simuler LEFT JOIN
        }
    },
    {
        "$project": {
            # Champs de la table "vente"
            "id_vente": 1,
            "date_vente": 1,
            "id_medicament": 1,
            "quantite": 1,
            "client_id": 1,
            "employe_id": 1,
            "date_de_vente":1,
            "autres_champs": 1,  # Remplace par les vrais noms si d'autres champs sont là

            # Champs de la table "medicament"
            "nom_medicament": "$medicament_info.nom",
            "medicament_categorie": "$medicament_info.categorie",
            "date_expiration": "$medicament_info.date_expiration",
            "arrival_date": "$medicament_info.arrival_date",
            "quantity_arrival": "$medicament_info.quantity_arrival",
            "prix_unitaire": "$medicament_info.prix_unitaire",
            "prix_fournisseur": "$medicament_info.prix_fournisseur",
            "lot_id": "$medicament_info.lot_id",
            "fournisseur": "$medicament_info.fournisseur",
            "retard_jour": "$medicament_info.retard_jour",

            # Champs calculés
            "quantite_restante": {
                "$subtract": ["$medicament_info.quantity_arrival", "$quantite"]
            },
            "prix_vente": {
                "$multiply": ["$medicament_info.prix_unitaire", "$quantite"]
            },
            "marge_prix": {
                "$subtract": ["$medicament_info.prix_unitaire", "$medicament_info.prix_fournisseur"]
            }
        }
    }
]


