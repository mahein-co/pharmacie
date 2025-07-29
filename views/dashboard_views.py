import streamlit as st
from data.mongodb_client import MongoDBClient
from data import mongodb_pipelines

from pipelines import pipeline_overview

# Initialisation a MongoDB
vente_collection = MongoDBClient(collection_name="vente")
overview_collection = MongoDBClient(collection_name="overview")
medicament_collection = MongoDBClient(collection_name="medicament")
employe_collection = MongoDBClient(collection_name="employe")

# 1. chiffre d'affaire total
chiffre_affaire = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_chiffre_affaire_total, title="Calcul du chiffre d'affaire")

try:
  total_chiffre_affaire = chiffre_affaire[0]["chiffre_affaire_total"] if chiffre_affaire else 0
  total_chiffre_affaire_str = f"{int(total_chiffre_affaire):,}".replace(",", " ")
except Exception as e:
    total_chiffre_affaire_str = 0

# # 2. valeur totale du stock
valeur_stock = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_valeur_totale_stock, 
  title="Calcul de la valeur totale du stock"
)
try:
    valeur_totale_stock = valeur_stock[0]["valeur_stock_totale"] if valeur_stock else 0
except Exception as e:
    valeur_totale_stock = 0
    
# # 3. nombre total de vente
nombre_total_vente_str = f"{pipeline_overview.total_sales:,}".replace(",", " ")

# # 4. nombre total d'alimentation
# # nombre_alimentation = medicament_collection.make_specific_pipeline(pipeline=mongodb_pipelines.pipeline_nombre_alimentations, title="Recuperation de nombre total d'alimentation")
# # try:
# #     nombre_total_alimentation = nombre_alimentation[0]["nombre_total_alimentations"] if nombre_alimentation else 0
# # except Exception as e :
# #     nombre_total_alimentation = 0

# II- SECOND LINE OF SCORECARD
# 2.1. Nombre total de médicaments
nb_total_medicaments = medicament_collection.count_distinct_agg(field_name="id_medicament")
    
# 2.2. Total des pertes dues aux médicaments invendus
pertes_medicaments = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_pertes_expiration, 
  title="Calcul des pertes dues aux médicaments invendus"
)
try:
  total_pertes_medicaments = pertes_medicaments[0]["total_pertes"] if pertes_medicaments else 0
except Exception as e:
  total_pertes_medicaments = 0

# # 2.4. Nombre total de fournisseur
# nb_total_fournisseurs = medicament_collection.count_distinct_agg(field_name="fournisseur")

    
# # 2.5. Médicaments expirés ou bientôt expirés
# medicaments_expires = medicament_collection.make_specific_pipeline(pipeline=mongodb_pipelines.pipeline_expirations, title="Récupération des médicaments expirés ou bientôt expirés")


# STYLES
custom_css = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");

body {
  font-family: "Quicksand", sans-serif;
  justify-content: center;
  align-items: center;
  background-color: #ffffff !important;
}

.main {
  width: 50%;
  padding: 20px;
}

/* METRICS */
.stMetric {
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
  padding: 20px;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.stMetric:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
}

/* BOUTONS */
.stButton > button {
  background-color: #007bff;
  color: white;
  border-radius: 10px;
  padding: 10px 20px;
  border: none;
  font-weight: 600;
  transition: background-color 0.3s ease;
}
.stButton > button:hover {
  background-color: #0056b3;
}

/* TITRE */
.stTitle {
  color: #333;
  font-size: 28px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 20px;
}

/* CHARTS */
.stPlotlyChart {
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 15px;
  margin-top: 30px;
}

/* TABLES */
.stTable th, .stTable td {
  padding: 10px;
  text-align: left;
  border: 1px solid #ddd;
}
.stTable th {
  background-color: #f2f2f2;
  font-weight: bold;
}
.stTable td {
  background-color: #ffffff;
}

/* BOUTON FLOTTANT */
.floating-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  border-radius: 30px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease, transform 0.3s ease;
}
.floating-button:hover {
  background-color: #0056b3;
  transform: scale(1.05);
}
.floating-button i {
  margin-right: 8px;
}

/* RELOAD */
.reload-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  border-radius: 30px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease, transform 0.3s ease;
}
.reload-button:hover {
  background-color: #0056b3;
  transform: scale(1.05);
}
.reload-button i {
  margin-right: 8px;
}

/* CARDS */
.container {
  display: flex;
  gap: 20px;
  justify-content: space-between;
  flex-wrap: wrap;
  margin-bottom: 30px;
}   
.card {
  flex: 1;
  min-width: 200px;
  padding: 20px;
  border-radius: 15px;
  color: white;
  font-family: "Segoe UI", sans-serif;
  position: relative;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.card h1 {
  margin: 0;
  font-size: 1.5rem;
}
.card p {
  margin-top: 7px;
  font-size: 1rem;
  opacity: 0.9;
}
.card.pink { background-color: #f28ca3; }
.card.blue { background-color: #3f3d9b; }
.card.orange { background-color: #f6b352; }
.card.purple { background-color: #b8a4e4; color: #1f1f1f; }
</style>
"""

# talbe style
table_css = """
<style>
.table-container {
    font-family: Arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
    border-radius: 8px;
    overflow: hidden;
}

.table-container table {
    width: 100%;
    border-collapse: collapse;
}

.table-container th, .table-container td {
    padding: 12px 15px;
    text-align: center;
}

.table-container thead {
    background-color: #f8f9fa;
    font-weight: bold;
}

.table-container tr:nth-child(even) {
    background-color: #f4f4f4;
}

.badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    color: white;
    font-weight: bold;
    font-size: 0.85em;
}

.badge.green { background-color: #1abc9c; }     /* + positive */
.badge.red { background-color: #e74c3c; }       /* - negative */
.badge.grey { background-color: #95a5a6; }      /* 0% change */
</style>
"""

kpis_style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Roboto:ital,wght@0,100..900;1,100..900&family=Satisfy&display=swap');
* {
  font-family: "Quicksand", sans-serif;
}

.title {
  font-family: "Dancing Script", cursive;
  top: 0px;
}


.kpi-container {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
  font-family:"Roboto", cursive;

}

.kpi-card {
  background: #ffffff;
  border-radius: 15px;
  padding: 20px;
  flex: 1;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  text-align: center;
}
.kpi-title {
  color: #888;
  margin: 0;
  font-size: 3rem;
}
.kpi-value {
  font-size: 3rem;
  color: #000;
  font-weight: bold;
  margin: 5px 0;
}
.kpi-change {
  font-size: 14px;
}
.kpi-change.positive {
  color: #28a745;
}
.kpi-change.negative {
  color: #dc3545;
}

.section-card {
  background: #fff;
  padding: 20px;
  color: #888;
  border-radius: 15px;
  margin-bottom: 20px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.section-header h4 {
  margin: 0;
}
.view-report-btn {
  background: #f5f5f5;
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.visitors-count {
  font-size: 22px;
  margin-top: 15px;
}
.visitor-details {
  font-size: 14px;
  color: #666;
}
.positive {
  color: #28a745;
}
.negative {
  color: #dc3545;
}

.promo-card {
  background: linear-gradient(120deg, #4a6cf7, #6741f7);
  color: white;
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 20px;
  text-align: center;
}
.promo-title {
  font-size: 18px;
  font-weight: bold;
}
.promo-subtext {
  font-size: 14px;
  margin-bottom: 10px;
}
.go-pro-btn {
  background-color: #2ecc71;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.go-pro-btn:hover {
  background-color: #27ae60;
}

.conversion-footer {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
}

</style>
"""

# ========== KPI Cards ===============
three_first_kpis_html = f"""
<div class="kpi-container">
    <div class="kpi-card">
        <p class="kpi-title" style="font-size:1.2rem;">Total Finance</p>
        <p class="kpi-value" style="font-size:2rem;">{total_chiffre_affaire_str} <span class="badge grey">MGA</span></p>
    </div>
    <div class="kpi-card">
        <p class="kpi-title" style="font-size:1.2rem;">Total Ventes (Unités)</p>
        <p class="kpi-value" style="font-size:2rem;">{nombre_total_vente_str}</p>
    </div>
    <div class="kpi-card">
        <p class="kpi-title" style="font-size:1.2rem;">Total Approvisionnement</p>
        <p class="kpi-value" style="font-size:2rem;">{pipeline_overview.total_approvisionnements}</p>
    </div>
</div>
"""

three_second_kpis_html = f"""
<div class="kpi-container">
    <div class="kpi-card">
      <div class="kpi-title" style="font-size:1.2rem;">
          Total Pertes
          <span style="font-size:0.9rem;">(Médicaments invendus)</span>
      </div>
      <div class="kpi-value" style="font-size:2rem;">{f"{int(total_pertes_medicaments/4):,}".replace(",", " ")}&nbsp;MGA</div>
    </div>
    <div class="kpi-card">
        <p class="kpi-title" style="font-size:1.2rem;">Valeur Stock</p>
        <p class="kpi-value" style="font-size:2rem;">{f"{int(valeur_totale_stock/5):,}".replace(",", " ")}&nbsp;MGA</p>
    </div>
    <div class="kpi-card">
        <p class="kpi-title" style="font-size:1.2rem;">Total Médicaments</p>
        <p class="kpi-value" style="font-size:2rem;">{nb_total_medicaments}</p>
    </div>
</div>
"""


table_html = """
<div class="table-container">
<table>
    <thead>
        <tr>
            <th></th>
            <th>08/07/23 - 14/07/23</th>
            <th>01/07/23 - 07/07/23</th>
            <th>∆</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Impressions</td>
            <td>12</td>
            <td>12</td>
            <td><span class="badge grey">↔ 0%</span></td>
        </tr>
        <tr>
            <td>Clics</td>
            <td>572</td>
            <td>487</td>
            <td><span class="badge green">+18%</span></td>
        </tr>
        <tr>
            <td>Visiteurs uniques</td>
            <td>362</td>
            <td>348</td>
            <td><span class="badge green">+4%</span></td>
        </tr>
        <tr>
            <td>Leads</td>
            <td>0</td>
            <td>0</td>
            <td><span class="badge grey">↔ 0%</span></td>
        </tr>
        <tr>
            <td>Ventes</td>
            <td>3</td>
            <td>0</td>
            <td><span class="badge green">+∞%</span></td>
        </tr>
        <tr>
            <td>Valeur de la commande</td>
            <td>0€</td>
            <td>213,12€</td>
            <td><span class="badge red">-100%</span></td>
        </tr>
        <tr>
            <td>Commissions</td>
            <td>2,13€</td>
            <td>0€</td>
            <td><span class="badge green">+100%</span></td>
        </tr>
    </tbody>
</table>
</div>
"""


# # Exemples d'utilisation
# st.markdown(f"""
# <div class="container">
#     <div class="card pink">
#         <h1>{dashboard_views.total_chiffre_affaire}&nbsp;MGA</h1>
#         <p>Chiffre d'affaire total</p>
#     </div>
#     <div class="card blue">
#         <h1>118.7 k</h1>
#         <p>Total ventes</p>
#     </div>
#     <div class="card orange">
#         <h1>56.3 k</h1>
#         <p>Total alimentations</p>
#     </div>
#     <div class="card purple">
#         <h1>2 114</h1>
#         <p>Total médicaments</p>
#     </div>
# </div>
# """, unsafe_allow_html=True)


