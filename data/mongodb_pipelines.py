from datetime import datetime, timedelta

# Date actuelle en timestamp (ms)
now_dt = datetime.utcnow()
now_ms = int(datetime.utcnow().timestamp() * 1000)
in_30_days_ms = int((datetime.utcnow() + timedelta(days=30)).timestamp() * 1000)

today = datetime.utcnow()
in_30_days = today + timedelta(days=30)

# 1. Valeur totale du stock
pipeline_valeur_totale_stock = [
    {
        "$lookup": {
            "from": "vente",
            "localField": "id_medicament",
            "foreignField": "id_medicament",
            "as": "ventes"
        }
    },
    {
        "$addFields": {
            "total_ventes": { 
                "$sum": "$ventes.quantite"
            }
        }
    },
    {
        "$project": {
            "nom": 1,
            "prix_unitaire": 1,
            "Quantity_arrival": 1,
            "total_ventes": { "$ifNull": ["$total_ventes", 0] },
            "stock_restant": {
                "$subtract": ["$Quantity_arrival", { "$ifNull": ["$total_ventes", 0] }]
            }
        }
    },
    {
        "$addFields": {
            "valeur_stock_restant": {
                "$multiply": ["$stock_restant", "$prix_unitaire"]
            }
        }
    },
    {
        "$group": {
            "_id": None,
            "valeur_totale_stock": { "$sum": "$valeur_stock_restant" }
        }
    }
]

pipeline_somme_valeur_stock = [
    {
        "$lookup": {
            "from": "vente",
            "localField": "id_medicament",
            "foreignField": "id_medicament",
            "as": "ventes"
        }
    },
    {
        "$addFields": {
            "total_ventes": {
                "$sum": "$ventes.quantite"
            }
        }
    },
    {
        "$addFields": {
            "total_ventes": { "$ifNull": ["$total_ventes", 0] },
            "stock_restant": {
                "$subtract": ["$Quantity_arrival", { "$ifNull": ["$total_ventes", 0] }]
            },
            "valeur_stock": {
                "$multiply": [
                    { "$subtract": ["$Quantity_arrival", { "$ifNull": ["$total_ventes", 0] }] },
                    "$prix_unitaire"
                ]
            }
        }
    },
    {
        "$group": {
            "_id": None,
            "valeur_totale_stock": {
                "$sum": "$valeur_stock"
            }
        }
    }
]

# 2. Ventes complètes
pipeline_ventes_completes = [
        # 🔗 Jointure avec medicament
        {
            "$lookup": {
                "from": "medicament",
                "localField": "id_medicament",
                "foreignField": "id_medicament",
                "as": "medicament_info"
            }
        },
        { "$unwind": "$medicament_info" },

        # 🔗 Jointure avec employe
        {
            "$lookup": {
                "from": "employe",
                "localField": "id_employe",
                "foreignField": "id_employe",
                "as": "employe_info"
            }
        },
        { "$unwind": "$employe_info" },

        # 🧼 Projection finale
        {
            "$project": {
                "_id": 0,
                "date_de_vente": 1,
                "quantite": 1,
                "medecin": 1,

                # 🧪 Infos médicament
                "nom_medicament": "$medicament_info.nom",
                "categorie_medicament": "$medicament_info.categorie",
                "prix_unitaire": "$medicament_info.prix_unitaire",
                "prix_fournisseur": "$medicament_info.prix_fournisseur",
                "fournisseur": "$medicament_info.fournisseur",
                "date_expiration": "$medicament_info.date_expiration",
                "date_arrivee": "$medicament_info.arrival_date",
                "quantite_arrivee": "$medicament_info.Quantity_arrival",
                "retard_jour": "$medicament_info.retard_jour",

                # 👤 Infos employé
                "nom_employe": { "$concat": ["$employe_info.prenom", " ", "$employe_info.nom"] },
                "date_naissance": "$employe_info.date_naissance",
                "date_embauche": "$employe_info.date_embauche",
                "fonction": "$employe_info.fonction",
                "categorie_employe": "$employe_info.categorie",
                "salaire": "$employe_info.salaire",
                "sexe": "$employe_info.sex"
            }
        }
]

# 3. Chiffre d'affaire total
pipeline_chiffre_affaire = [
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
            "quantite": 1,
            "prix_unitaire": "$medicament_info.prix_unitaire",
            "montant_vente": { "$multiply": ["$quantite", "$medicament_info.prix_unitaire"] }
        }
    },
    {
        "$group": {
            "_id": None,
            "montant_total": { "$sum": "$montant_vente" }
        }
    }
]

# 4. Nombre total d'alimentations
pipeline_nombre_alimentations = [
    {
        "$count": "nombre_total_alimentations"
    }
]

# 5. Total des pertes dues aux medicaments invendus
pipeline_pertes_medicaments = [
    {
        "$match": {
            "date_expiration": { "$lt":now_dt  } 
        }
    },
    {
        "$lookup": {
            "from": "vente",
            "localField": "id_medicament",
            "foreignField": "id_medicament",
            "as": "ventes"
        }
    },
    {
        "$addFields": {
            "total_ventes": { "$sum": "$ventes.quantite" }
        }
    },
    {
        "$addFields": {
            "total_ventes": { "$ifNull": ["$total_ventes", 0] },
            "stock_perdu": {
                "$subtract": ["$Quantity_arrival", { "$ifNull": ["$total_ventes", 0] }]
            },
            "valeur_perte": {
                "$multiply": [
                    { "$subtract": ["$Quantity_arrival", { "$ifNull": ["$total_ventes", 0] }] },
                    "$prix_unitaire"
                ]
            }
        }
    },
    {
        "$group": {
            "_id": None,
            "valeur_totale_perte": { "$sum": "$valeur_perte" }
        }
    }
]

pipeline_valeur_perte = [
    {
        "$match": {
            "date_expiration": { "$lt": today }
        }
    },
    {
        "$project": {
            "_id": 0,
            "nom": 1,
            "date_expiration": 1,
            "prix_unitaire": 1,
            "Quantity_arrival": 1,
            "valeur_perte": {
                "$multiply": ["$prix_unitaire", "$Quantity_arrival"]
            }
        }
    },
    {
        "$group": {
            "_id": None,
            "perte_totale": { "$sum": "$valeur_perte" }
        }
    }
]




# 6. Nombre de medicaments expirés
pipeline_medicaments_expirants = [
    {
        "$match": {
            "date_expiration": { "$lte": in_30_days_ms }  # Médicaments expirés ou bientôt expirés
        }
    },
    {
        "$addFields": {
            "jours_restants": {
                "$floor": {
                    "$divide": [
                        { "$subtract": [ "$date_expiration", now_ms ] },
                        1000 * 60 * 60 * 24
                    ]
                }
            }
        }
    },
    {
        "$addFields": {
            "etat": {
                "$cond": {
                    "if": { "$lt": ["$jours_restants", 0] },
                    "then": "Expiré",
                    "else": "Bientôt expiré"
                }
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "id_medicament": 1,
            "nom": 1,
            "categorie": 1,
            "fournisseur": 1,
            "prix_unitaire": 1,
            "Quantity_arrival": 1,
            "date_expiration": 1,
            "jours_restants": 1,
            "etat": 1
        }
    }
]

pipeline_expirations = [
    {
        "$match": {
            "date_expiration": {
                "$lte": in_30_days  # Médicaments expirés ou expirant dans les 30 jours
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "nom": 1,
            "date_expiration": 1,
            "categorie": 1,
            "lot_ID": 1,
            "fournisseur": 1,
            "Quantity_arrival": 1
        }
    }
]


