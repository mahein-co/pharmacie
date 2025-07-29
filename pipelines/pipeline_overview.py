import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime, timedelta

from data.mongodb_client import MongoDBClient

# CONSTANTS
TODAY = datetime.today()
dans_30_jours = TODAY + timedelta(days=30)

# COLLECTION
overview_collection = MongoDBClient(collection_name="overview")

# Récupération de tous les documents de la collection overview
overview_docs = overview_collection.find_all_documents()

# Création d'un DataFrame à partir des documents
overview_df = pd.DataFrame(list(overview_docs))

overview_df["arrival_date"] = pd.to_datetime(overview_df["arrival_date"])
overview_df["date_de_vente"] = pd.to_datetime(overview_df["date_de_vente"])

# KPIs 
# 1. Chiffre d'affaires total
chiffe_affaire_total = (overview_df['quantite'] * overview_df['prix_unitaire']).sum()

# 2. Valeur total des stocks 
pipeline_valeur_totale_stock = [
    {
        "$match": {
            "date_expiration": { "$gt": TODAY }
        }
    },
    {
        "$group": {
            "_id": None,
            "valeur_stock_totale": {
                "$sum": {
                    "$multiply": ["$quantite_restante", "$prix_vente"]
                }
            }
        }
    }
]
# valid_stock = overview_df[pd.to_datetime(overview_df['date_expiration']) > TODAY]
# total_stock_value = valid_stock['valeur_stock'].sum()

# 3. Medicaments déjà expirés
pipeline_expired = [
    {
        "$match": {
            "date_expiration": { "$lt": TODAY }
        }
    },
    {
        "$project": {
            "_id": 0,
            "nom_medicament": 1,
            "lot_id": 1,
            "date_expiration": 1,
            "quantite_restante": 1
        }
    }
]
# df_expired_medcines = overview_df.groupby('nom_medicament')[['quantite_restante', 'prix_unitaire', 'date_expiration']].first()
# df_expired_medcines["valeur_stock"] = df_expired_medcines["quantite_restante"] * df_expired_medcines["prix_unitaire"]
# df_expired_medcines = df_expired_medcines.sort_values(by="valeur_stock", ascending=False)

# 4. Medicament bientôt expirés (dans 3 mois)
three_months_later = TODAY + timedelta(days=120)
pipeline_bientot_expire = [
    {
        "$match": {
            "date_expiration": {
                "$gte": TODAY,
                "$lte": three_months_later
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "nom_medicament": 1,
            "lot_id": 1,
            "date_expiration": 1,
            "quantite_restante": 1
        }
    }
]

# upcoming_expiry = overview_df[(pd.to_datetime(overview_df['date_expiration']) > TODAY) & (pd.to_datetime(overview_df['date_expiration']) <= three_months_later)]
# upcoming_expiry_grouped = upcoming_expiry.groupby('nom_medicament').agg({
#     'date_expiration': 'first',
#     'prix_unitaire': 'first',
#     'quantite_restante': 'sum',
#     'valeur_stock': 'sum'
# }).reset_index()
# upcoming_expiry_grouped['jour_restant'] = (pd.to_datetime(upcoming_expiry_grouped['date_expiration']) - datetime.today()).dt.days
# upcoming_expiry_grouped = upcoming_expiry_grouped.sort_values(by="jour_restant", ascending=True)

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
            "total_pertes": { "$sum": "$perte" }
        }
    }
]
# expired_medicines = overview_df[pd.to_datetime(overview_df['date_expiration']) < TODAY]

# 6. Nombre total d'employés
total_employees = overview_df['nom_employe'].nunique()

# 7. Nombre total d'approvisionnements
total_approvisionnements = overview_df['lot_id'].nunique()

# 8. Quantité totale de médicaments approvisionnés
quantity_by_medicine = overview_df.groupby('nom_medicament')['quantity_arrival'].sum().reset_index()

# 9. Nombre total de ventes
total_sales = len(overview_df)

# 10. Nombre total de fournisseurs
total_suppliers = overview_df['fournisseur'].nunique()

# 11. Médicaments en surplus (>500 unités)
surplus_stock = overview_df[(overview_df['quantite_restante'] > 500) & (pd.to_datetime(overview_df['date_expiration']) > pd.to_datetime('today'))]
surplus_stock_grouped = surplus_stock.groupby('nom_medicament').agg({
    'prix_unitaire': 'first',
    'quantite_restante': 'first',
    'valeur_stock': 'first'
}).reset_index()


# 12. Medicaments critical en stock
critical_stock = overview_df[(overview_df['quantite_restante'] < 70) & (pd.to_datetime(overview_df['date_expiration']) > pd.to_datetime('today'))]
critical_stock = critical_stock.sort_values(by="quantite_restante", ascending=False)
critical_stock_grouped = critical_stock.groupby('nom_medicament').agg({
    'prix_unitaire': 'first',
    'quantite_restante': 'first',
    'valeur_stock': 'sum'
}).reset_index()

# 13. Repture de stock sur les 3 derniers mois
three_months_ago = TODAY - timedelta(days=90)
last_month_sales = overview_df[pd.to_datetime(overview_df['date_de_vente']) >= three_months_ago]
stock_outs = last_month_sales[last_month_sales['quantite_restante'] == 0]
stock_outs_by_medicine = stock_outs.groupby('nom_medicament').size().reset_index(name='stock_out_count')

# 14. Médicament avec la plus forte rotation
high_rotation_medicine = overview_df.groupby('nom_medicament')['quantite'].sum().sort_values(ascending=False).head(1)

# 15. Médicament avec la plus faible rotation
low_rotation_medicine = overview_df.groupby('nom_medicament')['quantite'].sum().sort_values(ascending=True).head(1)

# 16. Médicaments les plus vendus (Top 3)
top_3_best_selling_medicines = overview_df.groupby('nom_medicament')['quantite'].sum().nlargest(3)

# 17. Médicaments les moins vendus (Bottom 3)
bottom_3_least_selling_medicines = overview_df.groupby('nom_medicament')['quantite'].sum().nsmallest(3)

# 18. Chiffre d’affaires par jour/semaine/mois
overview_df['chiffre_affaires'] = overview_df['quantite'] * overview_df['prix_unitaire']

daily_revenue = overview_df.resample('D', on='date_de_vente')['chiffre_affaires'].sum()
weekly_revenue = overview_df.resample('W', on='date_de_vente')['chiffre_affaires'].sum()
monthly_revenue = overview_df.resample('M', on='date_de_vente')['chiffre_affaires'].sum()

# plt.figure(figsize=(12, 6))
# plt.plot(daily_revenue, label='Daily Revenue')
# plt.title('Daily Revenue Over Time')
# plt.xlabel('Date')
# plt.ylabel('Revenue')
# plt.legend()
# plt.show()

# plt.figure(figsize=(12, 6))
# plt.plot(weekly_revenue, label='Weekly Revenue')
# plt.title('Weekly Revenue Over Time')
# plt.xlabel('Date')
# plt.ylabel('Revenue')
# plt.legend()
# plt.show()

# plt.figure(figsize=(12, 6))
# plt.plot(monthly_revenue, label='Monthly Revenue')
# plt.title('Monthly Revenue Over Time')
# plt.xlabel('Date')
# plt.ylabel('Revenue')
# plt.legend()
# plt.show()



# 19. Marge bénéficiaire moyenne
total_profit = (overview_df['quantite'] * overview_df['marge_prix']).sum()
total_revenue = (overview_df['quantite'] * overview_df['prix_unitaire']).sum()

if total_revenue > 0:
    average_profit_margin = (total_profit / total_revenue) * 100
else:
    average_profit_margin = 0

# 20. Médicament qui rapporte le plus
overview_df['profit'] = overview_df['quantite'] * overview_df['marge_prix']
most_profitable_medicine = overview_df.groupby('nom_medicament')['profit'].sum().idxmax()
total_profit = overview_df.groupby('nom_medicament')['profit'].sum().max()


# 21. Medicament qui rapporte le moins
least_profitable_medicine = overview_df.groupby('nom_medicament')['profit'].sum().idxmin()
total_profit = overview_df.groupby('nom_medicament')['profit'].sum().min()

# 22. Médicament avec la plus faible marge
lowest_margin_medicine = overview_df.groupby('nom_medicament')['marge_prix'].mean().idxmin()
lowest_margin_value = overview_df.groupby('nom_medicament')['marge_prix'].mean().min()
average_selling_price = overview_df[overview_df['nom_medicament'] == lowest_margin_medicine]['prix_unitaire'].mean()
margin_percentage = (lowest_margin_value / average_selling_price) * 100

# 23. Médicament avec la plus forte marge
highest_margin_medicine = overview_df.groupby('nom_medicament')['marge_prix'].mean().idxmax()
highest_margin_value = overview_df.groupby('nom_medicament')['marge_prix'].mean().max()
average_selling_price = overview_df[overview_df['nom_medicament'] == highest_margin_medicine]['prix_unitaire'].mean()
margin_percentage = (highest_margin_value / average_selling_price) * 100

# 24. Evolution Total des pertes
expired_medicines = overview_df[(pd.to_datetime(overview_df['date_expiration']) < pd.to_datetime('today')) & (overview_df['quantite_restante'] > 0)].copy()
expired_medicines['date_expiration'] = pd.to_datetime(expired_medicines['date_expiration'])
expired_medicines.set_index('date_expiration', inplace=True)
monthly_losses = expired_medicines.resample('M')['valeur_stock'].sum().reset_index()

# plt.figure(figsize=(12, 3))
# sns.lineplot(data=monthly_losses, x='date_expiration', y='valeur_stock', label='Monthly Losses')
# plt.title('Monthly Losses from Expired Medicines Over Time')
# plt.xlabel('Date')
# plt.ylabel('Loss Value')
# plt.legend()
# plt.show()

# 25. Taux de livraison en retard des fournisseurs
late_deliveries = overview_df[overview_df['retard_jour'] > 0]
late_deliveries_by_supplier = late_deliveries.groupby('fournisseur').size()
total_deliveries_by_supplier = overview_df.groupby('fournisseur').size()
late_delivery_rate = (late_deliveries_by_supplier / total_deliveries_by_supplier) * 100

# 26. Temps moyen de livraison
average_delivery_time = overview_df.groupby('fournisseur')['retard_jour'].mean()

# 27. Nombre de médicaments en stock + Valeur financière du stock
three_months_ago = TODAY - timedelta(days=30)
last_3_months_data = overview_df[pd.to_datetime(overview_df['date_de_vente']) >= three_months_ago]
stock_summary = last_3_months_data.groupby('nom_medicament').agg({
    'quantite_restante': 'last',
    'valeur_stock': 'last'
}).reset_index()


# 28. Panier moyen par vente
total_revenue = (overview_df['quantite'] * overview_df['prix_unitaire']).sum()
total_sales = len(overview_df['id_vente'].unique())
average_basket_value = total_revenue / total_sales

# 29. Top vendeur
top_3_employees = overview_df.groupby('nom_employe').apply(lambda x: (x['quantite'] * x['prix_unitaire']).sum()).nlargest(3)
employee_revenue = overview_df.groupby('nom_employe').apply(lambda x: (x['quantite'] * x['prix_unitaire']).sum()).reset_index(name='total_revenue')
employee_info = overview_df[['nom_employe', 'fonction']].drop_duplicates()
top_employees = pd.merge(employee_revenue, employee_info, on='nom_employe').nlargest(3, 'total_revenue')
# top_employees.groupby('nom_employe').size().plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
# plt.gca().spines[['top', 'right',]].set_visible(False)

# 30. Vendeur non habilité
employee_revenue = overview_df.groupby('nom_employe').apply(lambda x: (x['quantite'] * x['prix_unitaire']).sum()).reset_index(name='total_revenue')
employee_info = overview_df[['nom_employe', 'fonction']].drop_duplicates()
bottom_employees = pd.merge(employee_revenue, employee_info, on='nom_employe').nsmallest(3, 'total_revenue')
# bottom_employees.groupby('nom_employe').size().plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
# plt.gca().spines[['top', 'right',]].set_visible(False)

# 31. Mois avec le plus d’approvisionnements
monthly_arrivals = overview_df.resample('M', on='arrival_date')['quantity_arrival'].sum()
top_3_months = monthly_arrivals.sort_values(ascending=False).head(3)

# 
