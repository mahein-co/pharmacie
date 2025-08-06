import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime, timedelta, timezone

from data.mongodb_client import MongoDBClient

# CONSTANTS
TODAY = datetime.today()
# TODAY = datetime.now(timezone.utc)
dans_30_jours = TODAY + timedelta(days=30)

# COLLECTION
overview_collection = MongoDBClient(collection_name="overview")

# Récupération de tous les documents de la collection overview
# overview_docs = overview_collection.find_all_documents()

# Création d'un DataFrame à partir des documents
# df = pd.DataFrame(overview_docs)


# KPIs 
# 1. Chiffre d'affaires total
pipeline_chiffre_affaire_total = [
    {
        "$match": {
            "quantite": { "$ne": None },
            "prix_unitaire": { "$ne": None }
        }
    },
    {
        "$project": {
            "quantite": { "$toDouble": "$quantite" },
            "prix_unitaire": { "$toDouble": "$prix_unitaire" }
        }
    },
    {
        "$group": {
            "_id": None,
            "chiffre_affaire_total": {
                "$sum": { "$multiply": ["$quantite", "$prix_unitaire"] }
            }
        }
    }
]

# 2. Valeur total des stocks
pipeline_valeur_totale_stock = [
    {
        "$match": {
            "date_expiration": { "$gt": TODAY },
            "quantite_restante": { "$gt": 0 }
        }
    },
    {
        "$group": {
            "_id": None,
            "valeur_stock_totale": {
                "$sum": {
                    "$multiply": ["$quantite_restante", "$prix_unitaire"]
                }
            }
        }
    }
]

# 3. Medicaments déjà expirés
pipeline_medicament_expired = [
    {
        "$match": {
            "date_expiration": {
                "$lte": TODAY
            },
            "quantite_restante": {"$gt": 0 }
        }
    },
    {
        "$project": {
            "_id": 0,
            "nom_medicament": 1,
            "lot_id": 1,
            "date_expiration": 1,
            "quantite_restante": 1,
            "jours_restants": {
                "$dateDiff": {
                    "startDate": TODAY,
                    "endDate": "$date_expiration",
                    "unit": "day"
                }
            }
        }
    },
    {
      "$group": {
        "_id": "$lot_id",
        "nom_medicament": { "$first": "$nom_medicament" },
        "date_expiration": { "$first": "$date_expiration" },
        "quantite_totale_restante": { "$first": "$quantite_restante" },
        "jours_restants": {
          "$first": {
            "$cond": [
              { "$lte": ["$jours_restants", 0] }, 0, "$jours_restants"
            ]
          }
        }
      }
    },
    {
        "$sort": {
            "date_expiration": 1
        }
    }
]

# 4. Medicament bientôt expirés (dans 3 mois)
three_months_later = TODAY + timedelta(days=90)
pipeline_medicament_bientot_expire = [
    {
        "$match": {
            "date_expiration": {
                "$gte": TODAY, 
                "$lte": three_months_later,
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "nom_medicament": 1,
            "lot_id": 1,
            "date_expiration": 1,
            "quantite_restante": 1,
            "jours_restants": {
                "$dateDiff": {
                    "startDate": TODAY,
                    "endDate": "$date_expiration",
                    "unit": "day"
                }
            }
        }
    },
    {
        "$group": {
            "_id": "$lot_id",
            "nom_medicament": { "$first": "$nom_medicament" },
            "date_expiration": { "$first": "$date_expiration" },
            "quantite_totale_restante": { "$first": "$quantite_restante" },
            "jours_restants": { "$first": "$jours_restants" }
        }
    },
    {
        "$sort": {
            "date_expiration": 1
        }
    }
]

# 5. Total de pertes dues aux medicaments expirés
pipeline_pertes_expiration = [
    {
        "$match": {
            "date_expiration": { "$lt": TODAY },
            "quantite_restante": { "$gt": 0 }
        }
    },
    {
        "$project": {
            "perte": {
                "$multiply": ["$quantite_restante", "$prix_unitaire"]
            }
        }
    },
   {
  "$group": {
    "_id": None,
    "total_pertes": {
      "$sum": {
        "$subtract": [
          { "$divide": ["$perte", 4] },
          350
        ]
      }
    }
  }
}
]

# 6. Nombre total d'employés
# total_employees = df['nom_employe'].nunique()

# 7. Nombre total d'approvisionnements
total_approvisionnements = overview_collection.count_distinct_agg(field_name="lot_id")

# 8. Quantité totale de médicaments approvisionnés
pipeline_quantite_totale_approvisionnement = [
    {
        "$match": {
            "quantity_arrival": { "$ne": None }
        }
    },
    {
        "$project": {
            "quantity_arrival": { "$toDouble": "$quantity_arrival" }
        }
    },
    {
        "$group": {
            "_id": None,
            "quantite_totale_approvisionnee": {
                "$sum": "$quantity_arrival"
            }
        }
    }
]

# 9. Nombre total de ventes
total_sales = overview_collection.count_distinct_agg(field_name="id_vente")

# 10. Nombre total de fournisseurs
nb_fournisseur = overview_collection.count_distinct_agg(field_name="fournisseur")

#11.commande moyen par fournisseurs
pipeline_commande_moyen =  [
    {
        "$group": {
            "_id": "$fournisseur",
            "nombre_commandes": { "$sum": 1 }
        }
    },
    {
        "$group": {
            "_id": None,
            "moyenne_commandes_par_fournisseur": { "$avg": "$nombre_commandes" }
        }
    }
]

# 12. Médicaments en surplus (>500 unités)
pipeline_medicament_surplus = [
    {
        "$match": {
            "quantite_restante": { "$gt": 700 }
        }
    },
    {
        "$group": {
            "_id": "$nom_medicament",
            "total_quantite": { "$first": "$quantite_restante" },
            "lots": {
                "$push": {
                    "lot_id": "$lot_id",
                    "nom_medicament" : "$nom_medicament",
                    "fournisseur": "$fournisseur",
                    "quantite": "$quantite_restante",
                    "expiration": "$date_expiration"
                }
            }
        }
    },
    {
        "$sort": {
            "total_quantite": 1
        }
    }
]

# 13. Medicaments critical en stock
pipeline_medicament_critique = [
    {
        "$match": {
            "quantite_restante": { "$lt": 70 }
        }
    },
    {
        "$group": {
            "_id": "$nom_medicament",
            "total_quantite": { "$first": "$quantite_restante" },
            "lots": {
                "$push": {
                    "lot_id": "$lot_id",
                    "fournisseur": "$fournisseur",
                    "quantite": "$quantite_restante",
                    "expiration": "$date_expiration"
                }
            }
        }
    },
    {
        "$sort": {
            "total_quantite": 1
        }
    }
]

# 14. Repture de stock sur les 4 derniers mois
pipeline_rupture_stock = [
  {
    "$match": {
      "quantite_restante": 0,
      "date_de_vente": {
        "$gte": TODAY - timedelta(days=400)
      }
    }
  },
  {
    "$group": {
      "_id": {
        "lot_id": "$lot_id",
        "nom_medicament": "$nom_medicament"
      },
      "rupture_count": { "$sum": 1 },
      "derniere_vente": { "$max": "$date_de_vente" },
      "categorie": { "$first": "$medicament_categorie" },
      "fournisseur": { "$first": "$fournisseur" }
    }
  },
  {
    "$sort": {
      "derniere_vente": -1
    }
  }
]

# 15. Médicament avec la plus forte rotation
pipeline_medicament_forte_rotation = [
  {
    "$match": {
      "date_de_vente": {
        "$gte": TODAY - timedelta(days=120)
      }
    }
  },
  {
    "$group": {
      "_id": "$nom_medicament",
      "quantite_totale_vendue": { "$sum": "$quantite" },
      "nombre_de_ventes": { "$sum": 1 },
      "categorie": { "$first": "$medicament_categorie" },
      "fournisseur": { "$first": "$fournisseur" }
    }
  },
  {
    "$sort": {
      "quantite_totale_vendue": -1
    }
  },
  {
    "$limit": 3 
  }
]

# 16. Médicament avec la plus faible rotation
pipeline_medicament_faible_rotation = [
  {
    "$match": {
      "date_de_vente": {
        "$gte": TODAY - timedelta(days=120)
      }
    }
  },
  {
    "$group": {
      "_id": "$nom_medicament",
      "quantite_totale_vendue": { "$sum": "$quantite" },
      "nombre_de_ventes": { "$sum": 1 },
      "categorie": { "$first": "$medicament_categorie" },
      "fournisseur": { "$first": "$fournisseur" }
    }
  },
  {
    "$sort": {
      "quantite_totale_vendue": 1
    }
  },
  {
    "$limit": 3 
  }
]

# 17. Médicaments les plus vendus (Top 3)
pipeline_medicaments_plus_vendus = [
  {
    "$group": {
      "_id": "$nom_medicament",
      "quantite_totale_vendue": { "$sum": "$quantite" },
      "nombre_de_ventes": { "$sum": 1 },
      "categorie": { "$first": "$medicament_categorie" },
      "fournisseur": { "$first": "$fournisseur" }
    }
  },
  {
    "$sort": {
      "quantite_totale_vendue": -1
    }
  },
  {
    "$limit": 3
  }
]

# 18. Médicaments les moins vendus (Bottom 3)
pipeline_medicaments_moins_vendus = [
  {
    "$group": {
      "_id": "$nom_medicament",
      "quantite_totale_vendue": { "$sum": "$quantite" },
      "nombre_de_ventes": { "$sum": 1 },
      "categorie": { "$first": "$medicament_categorie" },
      "fournisseur": { "$first": "$fournisseur" }
    }
  },
  {
    "$sort": {
      "quantite_totale_vendue": 1
    }
  },
  {
    "$limit": 3
  }
]

# 19. Chiffre d’affaires par jour/semaine/mois
pipeline_chiffre_affaire_daily = [
  {
    "$addFields": {
      "date_jour": {
        "$dateToString": {
          "format": "%Y-%m-%d",
          "date": "$date_de_vente"
        }
      }
    }
  },
  {
    "$group": {
      "_id": "$date_jour",
      "chiffre_affaires": { "$sum": "$prix_total" },
      "nombre_de_ventes": { "$sum": 1 }
    }
  },
  {
    "$sort": {
      "_id": 1
    }
  }
]
pipeline_chiffre_affaire_weekly = [
  {
    "$addFields": {
      "annee": { "$isoWeekYear": "$date_vente" },
      "semaine": { "$isoWeek": "$date_vente" }
    }
  },
  {
    "$group": {
      "_id": {
        "annee": "$annee",
        "semaine": "$semaine"
      },
      "chiffre_affaires": { "$sum": "$prix_total" },
      "nombre_de_ventes": { "$sum": 1 }
    }
  },
  {
    "$sort": {
      "_id.annee": 1,
      "_id.semaine": 1
    }
  }
]
pipeline_chiffre_affaire_monthly = [
  {
    "$addFields": {
      "annee": { "$year": "$date_vente" },
      "mois": { "$month": "$date_vente" }
    }
  },
  {
    "$group": {
      "_id": {
        "annee": "$annee",
        "mois": "$mois"
      },
      "chiffre_affaires": { "$sum": "$prix_total" },
      "nombre_de_ventes": { "$sum": 1 }
    }
  },
  {
    "$sort": {
      "_id.annee": 1,
      "_id.mois": 1
    }
  }
]
pipeline_chiffre_affaire_yearly = [
  {
    "$addFields": {
      "annee": { "$year": "$date_vente" }
    }
  },
  {
    "$group": {
      "_id": "$annee",
      "chiffre_affaires": { "$sum": "$prix_total" },
      "nombre_de_ventes": { "$sum": 1 }
    }
  },
  {
    "$sort": {
      "_id": 1
    }
  }
]

# 20. Marge bénéficiaire moyenne
pipeline_marge_beneficiaire_moyenne = [
  # {
  #   "$project": {
  #     # "nom_medicament": 1,
  #     "prix_unitaire": 1,
  #     "prix_fournisseur": 1,
  #     "marge_pourcentage": {
  #       "$multiply": [
  #         { "$divide": ["$marge_prix", "$prix_unitaire"] },
  #         100
  #       ]
  #     }
  #   }
  # },
  {
    "$group": {
      "_id": None,
      "prix_unitaire": {"$avg":"$prix_unitaire"},
      "prix_fournisseur": {"$avg":"$prix_fournisseur"},
      "marge_prix": { "$avg": "$marge_prix" }
    }
  }
  # {
  #   "$sort": { "marge_pourcentage_moyenne": -1 }
  # }
]

# 21. Médicament qui rapporte le plus
pipeline_medicament_rapporte_plus = [
  {
    "$project": {
      "nom_medicament": 1,
      "gain_total": {
        "$multiply": ["$marge_prix", "$quantite"]
      }
    }
  },
  {
    "$group": {
      "_id": "$nom_medicament",
      "total_gain": { "$sum": "$gain_total" }
    }
  },
  {
    "$sort": { "total_gain": -1 }
  },{
      "$limit":3
  }
]

# 22. Medicament qui rapporte le moins
pipeline_medicament_rapporte_moins = [
  {
    "$project": {
      "nom_medicament": 1,
      "gain_total": {
        "$multiply": ["$marge_prix", "$quantite"]
      }
    }
  },
  {
    "$group": {
      "_id": "$nom_medicament",
      "total_gain": { "$sum": "$gain_total" }
    }
  },
  {
    "$sort": { "total_gain": 1 }
  },{
      "$limit":3
  }
]

# 23. Quantité de medicaments approvisionnés
pipeline_quatite_medicament_approvisionne = [
  {
    "$addFields": {
      "date_expiration": { "$toDate": "$date_expiration" }
    }
  },
  {
    "$match": {
      "date_expiration": { "$gte": TODAY }
    }
  },
  {
    "$group": {
      "_id": "$nom_medicament",
      "quantite_totale_approvisionnee": { "$sum": "$quantity_arrival" },
      "valeur_stock_active": {
        "$sum": { "$multiply": ["$quantity_arrival", "$prix_unitaire"] }
      }
    }
  },
  {
    "$sort": { "valeur_stock_active": -1 }
  }
] 


# 24. Médicament avec la plus faible marge
pipeline_plus_faible_marge = [
    {
        "$group": {
            "_id": "$nom_medicament",
            "marge_min": {"$min": "$marge_prix"},
            "categorie": {"$first": "$medicament_categorie"},
            "prix_unitaire": {"$first": "$prix_unitaire"},
            "prix_fournisseur": {"$first": "$prix_fournisseur"},
            "lot_id": {"$first": "$lot_id"}
        }
    },
    {"$sort": {"marge_min": 1}},  # Tri par marge croissante
    {"$limit": 3},
    {
        "$project": {
            "_id": 0,
            "nom_medicament": "$_id",
            "marge_prix": "$marge_min",
            "medicament_categorie": "$categorie",
            "prix_unitaire": 1,
            "prix_fournisseur": 1,
            "lot_id": 1
        }
    }
]

# pipeline_plus_faible_marge = [
#     {"$sort": {"marge_prix": 1}},  # Tri croissant
#     {"$limit": 3},                 # Garder le premier
#     {"$project": {
#         "_id": 0,
#         "nom_medicament": 1,
#         "medicament_categorie": 1,
#         "marge_prix": 1,
#         "prix_unitaire": 1,
#         "prix_fournisseur": 1,
#         "lot_id": 1
#     }}
# ]



# # 25. Médicament avec la plus forte marge
pipeline_plus_forte_marge = [
    {
        "$group": {
            "_id": "$nom_medicament",
            "marge_max": {"$max": "$marge_prix"},
            "categorie": {"$first": "$medicament_categorie"},
            "prix_unitaire": {"$first": "$prix_unitaire"},
            "prix_fournisseur": {"$first": "$prix_fournisseur"},
            "lot_id": {"$first": "$lot_id"}
        }
    },
    {"$sort": {"marge_max": -1}},
    {"$limit": 3},
    {"$project": {
        "_id": 0,
        "nom_medicament": "$_id",
        "marge_prix": "$marge_max",
        "medicament_categorie": "$categorie",
        "prix_unitaire": 1,
        "prix_fournisseur": 1,
        "lot_id": 1
    }}
]

# pipeline_plus_forte_marge = [
#     {"$sort": {"marge_prix": -1}},  # Tri décroissant
#     {"$limit": 3},                  # Garder le premier
#     {"$project": {
#         "_id": 0,
#         "nom_medicament": 1,
#         "medicament_categorie": 1,
#         "marge_prix": 1,
#         "prix_unitaire": 1,
#         "prix_fournisseur": 1,
#         "lot_id": 1
#     }}
# ]

# # 25. Evolution Total des pertes
# expired_medicines = df[(pd.to_datetime(df['date_expiration']) < pd.to_datetime('today')) & (df['quantite_restante'] > 0)].copy()
# expired_medicines['date_expiration'] = pd.to_datetime(expired_medicines['date_expiration'])
# expired_medicines.set_index('date_expiration', inplace=True)
# monthly_losses = expired_medicines.resample('M')['valeur_stock'].sum().reset_index()

# # plt.figure(figsize=(12, 3))
# # sns.lineplot(data=monthly_losses, x='date_expiration', y='valeur_stock', label='Monthly Losses')
# # plt.title('Monthly Losses from Expired Medicines Over Time')
# # plt.xlabel('Date')
# # plt.ylabel('Loss Value')
# # plt.legend()
# # plt.show()

# # 26. Taux de livraison en retard des fournisseurs
# late_deliveries = df[df['retard_jour'] > 0]
# late_deliveries_by_supplier = late_deliveries.groupby('fournisseur').size()
# total_deliveries_by_supplier = df.groupby('fournisseur').size()
# late_delivery_rate = (late_deliveries_by_supplier / total_deliveries_by_supplier) * 100

# # 27. Temps moyen de livraison
# average_delivery_time = df.groupby('fournisseur')['retard_jour'].mean()

# # 28. Nombre de médicaments en stock + Valeur financière du stock
# three_months_ago = TODAY - timedelta(days=30)
# last_3_months_data = df[pd.to_datetime(df['date_de_vente']) >= three_months_ago]
# stock_summary = last_3_months_data.groupby('nom_medicament').agg({
#     'quantite_restante': 'last',
#     'valeur_stock': 'last'
# }).reset_index()

# 27.Medicaments les plus cher
pipeline_medicaments_plus_cher = [
  {
    "$sort": { "prix_unitaire": -1 }
  },
  {
    "$limit": 3
  },
  {
    "$project": {
      "_id": 0,
      "nom_medicament": 1,
      "lot_id": 1,
      "prix_unitaire": 1,
      "fournisseur": 1
    }
  }
]

# 28.Medicaments les moins cher
pipeline_medicaments_moins_cher = [
  {
    "$sort": { "prix_unitaire": 1 }
  },
  {
    "$limit": 3
  },
  {
    "$project": {
      "_id": 0,
      "nom_medicament": 1,
      "lot_id": 1,
      "prix_unitaire": 1,
      "fournisseur": 1
    }
  }
]

# 29. Panier moyen par vente
pipeline_panier_moyen_vente = [
  {
    "$group": {
      "_id": "$id_vente",
      "valeur_vente": {
        "$sum": { "$multiply": ["$quantite", "$prix_unitaire"] }
      }
    }
  },
  {
    "$group": {
      "_id": None,
      "total_valeur": { "$sum": "$valeur_vente" },
      "nombre_ventes": { "$sum": 1 }
    }
  },
  {
    "$project": {
      "_id": 0,
      "panier_moyen": { "$divide": ["$total_valeur", "$nombre_ventes"] }
    }
  }
]

# 30. Top vendeur
pipeline_top_vendeur = [
  {
    "$group": {
      "_id": {
        "nom": "$nom_employe",
      },
      "total_ventes": { "$sum": "$quantite" },
      "chiffre_affaire": { "$sum": { "$multiply": ["$quantite", "$prix_unitaire"] } }
    }
  },
  {
    "$sort": { "total_ventes": -1 }
  },
  {
    "$limit": 3
  }
]

# 31. Vendeur non habilité
pipeline_vendeur_non_habilite = [
  {
    "$group": {
      "_id": {
        "nom": "$nom_employe",
      },
      "total_ventes": { "$sum": "$quantite" },
      "chiffre_affaire": { "$sum": { "$multiply": ["$quantite", "$prix_unitaire"] } }
    }
  },
  {
    "$sort": { "total_ventes": 1 }
  },
  {
    "$limit": 3
  }
]

# 32. Mois avec le plus d’approvisionnements
pipeline_mois_plus_approvisionnement = [
  {
    "$addFields": {
      "month_year": { "$dateToString": { "format": "%Y-%m", "date": "$arrival_date" } }
    }
  },
  {
    "$group": {
      "_id": "$month_year",
      "total_approvisionnement": { "$sum": "$quantity_arrival" }
    }
  },
  {
    "$sort": { "total_approvisionnement": -1 }
  },
  {
    "$limit": 3
  }
]

# 33. Temps moyen de livraison par fournisseur
pipeline_temps_moyen_livraison_fournisseur = [
  {
    "$group": {
      "_id": "$fournisseur",
      "temps_moyen_livraison": { "$avg": "$retard_jour" },
      "nombre_commandes": { "$sum": 1 }
    }
  },
  {
    "$sort": {
      "temps_moyen_livraison": -1
    }
  }
]



