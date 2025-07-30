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
            "jours_restants": { "$first": "$jours_restants" }
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
            "quantite_restante": { "$gt": 500 }
        }
    },
    {
        "$group": {
            "_id": "$nom_medicament",
            "total_quantite": { "$sum": "$quantite_restante" },
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

# 13. Medicaments critical en stock
pipeline_medicament_critique = [
    {
        "$match": {
            "quantite_restante": { "$lt": 50 }
        }
    },
    {
        "$group": {
            "_id": "$nom_medicament",
            "total_quantite": { "$sum": "$quantite_restante" },
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
        "$gte": TODAY - timedelta(days=120)
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
# top_3_best_selling_medicines = df.groupby('nom_medicament')['quantite'].sum().nlargest(3)

# # 18. Médicaments les moins vendus (Bottom 3)
# bottom_3_least_selling_medicines = df.groupby('nom_medicament')['quantite'].sum().nsmallest(3)

# # 19. Chiffre d’affaires par jour/semaine/mois
# df['chiffre_affaires'] = df['quantite'] * df['prix_unitaire']

# daily_revenue = df.resample('D', on='date_de_vente')['chiffre_affaires'].sum()
# weekly_revenue = df.resample('W', on='date_de_vente')['chiffre_affaires'].sum()
# monthly_revenue = df.resample('M', on='date_de_vente')['chiffre_affaires'].sum()

# # plt.figure(figsize=(12, 6))
# # plt.plot(daily_revenue, label='Daily Revenue')
# # plt.title('Daily Revenue Over Time')
# # plt.xlabel('Date')
# # plt.ylabel('Revenue')
# # plt.legend()
# # plt.show()

# # plt.figure(figsize=(12, 6))
# # plt.plot(weekly_revenue, label='Weekly Revenue')
# # plt.title('Weekly Revenue Over Time')
# # plt.xlabel('Date')
# # plt.ylabel('Revenue')
# # plt.legend()
# # plt.show()

# # plt.figure(figsize=(12, 6))
# # plt.plot(monthly_revenue, label='Monthly Revenue')
# # plt.title('Monthly Revenue Over Time')
# # plt.xlabel('Date')
# # plt.ylabel('Revenue')
# # plt.legend()
# # plt.show()



# # 20. Marge bénéficiaire moyenne
# total_profit = (df['quantite'] * df['marge_prix']).sum()
# total_revenue = (df['quantite'] * df['prix_unitaire']).sum()

# if total_revenue > 0:
#     average_profit_margin = (total_profit / total_revenue) * 100
# else:
#     average_profit_margin = 0

# # 21. Médicament qui rapporte le plus
# df['profit'] = df['quantite'] * df['marge_prix']
# most_profitable_medicine = df.groupby('nom_medicament')['profit'].sum().idxmax()
# total_profit = df.groupby('nom_medicament')['profit'].sum().max()


# # 22. Medicament qui rapporte le moins
# least_profitable_medicine = df.groupby('nom_medicament')['profit'].sum().idxmin()
# total_profit = df.groupby('nom_medicament')['profit'].sum().min()

# # 23. Médicament avec la plus faible marge
# lowest_margin_medicine = df.groupby('nom_medicament')['marge_prix'].mean().idxmin()
# lowest_margin_value = df.groupby('nom_medicament')['marge_prix'].mean().min()
# average_selling_price = df[df['nom_medicament'] == lowest_margin_medicine]['prix_unitaire'].mean()
# margin_percentage = (lowest_margin_value / average_selling_price) * 100

# # 24. Médicament avec la plus forte marge
# highest_margin_medicine = df.groupby('nom_medicament')['marge_prix'].mean().idxmax()
# highest_margin_value = df.groupby('nom_medicament')['marge_prix'].mean().max()
# average_selling_price = df[df['nom_medicament'] == highest_margin_medicine]['prix_unitaire'].mean()
# margin_percentage = (highest_margin_value / average_selling_price) * 100

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


# # 29. Panier moyen par vente
# total_revenue = (df['quantite'] * df['prix_unitaire']).sum()
# total_sales = len(df['id_vente'].unique())
# average_basket_value = total_revenue / total_sales

# # 30. Top vendeur
# top_3_employees = df.groupby('nom_employe').apply(lambda x: (x['quantite'] * x['prix_unitaire']).sum()).nlargest(3)
# employee_revenue = df.groupby('nom_employe').apply(lambda x: (x['quantite'] * x['prix_unitaire']).sum()).reset_index(name='total_revenue')
# employee_info = df[['nom_employe', 'fonction']].drop_duplicates()
# top_employees = pd.merge(employee_revenue, employee_info, on='nom_employe').nlargest(3, 'total_revenue')
# # top_employees.groupby('nom_employe').size().plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
# # plt.gca().spines[['top', 'right',]].set_visible(False)

# # 31. Vendeur non habilité
# employee_revenue = df.groupby('nom_employe').apply(lambda x: (x['quantite'] * x['prix_unitaire']).sum()).reset_index(name='total_revenue')
# employee_info = df[['nom_employe', 'fonction']].drop_duplicates()
# bottom_employees = pd.merge(employee_revenue, employee_info, on='nom_employe').nsmallest(3, 'total_revenue')
# # bottom_employees.groupby('nom_employe').size().plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
# # plt.gca().spines[['top', 'right',]].set_visible(False)

# # 32. Mois avec le plus d’approvisionnements
# monthly_arrivals = df.resample('M', on='arrival_date')['quantity_arrival'].sum()
# top_3_months = monthly_arrivals.sort_values(ascending=False).head(3)

# 
