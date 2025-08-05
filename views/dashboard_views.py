import streamlit as st
import pandas as pd
from data.mongodb_client import MongoDBClient
from data import mongodb_pipelines
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

from pipelines import pipeline_overview
from views import employe_views

import base64

# Initialisation a MongoDB
vente_collection = MongoDBClient(collection_name="vente")
overview_collection = pipeline_overview.overview_collection
medicament_collection = MongoDBClient(collection_name="medicament")
employe_collection = MongoDBClient(collection_name="employe")

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# I- S C O R E C A R D
# 1.1. chiffre d'affaire total
chiffre_affaire = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_chiffre_affaire_total, title="Calcul du chiffre d'affaire")
try:
  total_chiffre_affaire = chiffre_affaire[0]["chiffre_affaire_total"] if chiffre_affaire else 0
  total_chiffre_affaire_str = f"{int(total_chiffre_affaire):,}".replace(",", " ")
except Exception as e:
    total_chiffre_affaire_str = 0

# 1.2. valeur totale du stock
valeur_stock = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_valeur_totale_stock, 
  title="Calcul de la valeur totale du stock"
)
try:
    valeur_totale_stock = valeur_stock[0]["valeur_stock_totale"] if valeur_stock else 0
except Exception as e:
    valeur_totale_stock = 0
    
# 1.3. nombre total de vente
nombre_total_vente_str = f"{pipeline_overview.total_sales:,}".replace(",", " ")

# 1.4. Nombre total de médicaments
nb_total_medicaments = medicament_collection.count_distinct_agg(field_name="id_medicament")
    
# 1.5. Total des pertes dues aux médicaments invendus
pertes_medicaments = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_pertes_expiration, 
  title="Calcul des pertes dues aux médicaments invendus"
)
try:
  total_pertes_medicaments = pertes_medicaments[0]["total_pertes"] if pertes_medicaments else 0
except Exception as e:
  total_pertes_medicaments = 0

    
# II. MEDICAMENTS
# 2.1. Médicaments expirés
medicaments_expires = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_medicament_expired, 
  title="Récupération des médicaments expirés ou bientôt expirés"
)

# 2.2. Medicament bientôt expirés
medicament_bientot_expires = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_medicament_bientot_expire,
  title="Récupération des médicaments bientôt expirés"
)
medicaments_expires = medicaments_expires + medicament_bientot_expires
medicaments_expires.sort(key=lambda x: x['date_expiration'])

# 2.3 Médicaments en rupture de stock au cours de 4 derniers mois
medicaments_rupture_stock = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_rupture_stock,
  title="Récupération des médicaments en rupture de stock"
) 

# 2.4. Médicaments avec le plus forte rotation
medicaments_forte_rotation = overview_collection.make_specific_pipeline(
  pipeline= pipeline_overview.pipeline_medicament_forte_rotation,
  title= "Récupération des médicaments avec la plus forte rotation"
)

# 2.5. Médicaments avec le plus faible rotation
medicaments_faible_rotation = overview_collection.make_specific_pipeline(
  pipeline= pipeline_overview.pipeline_medicament_faible_rotation,
  title= "Récupération des médicaments avec la plus baile rotation"
)

# 2.6. Médicaments les plus de vendus
medicaments_plus_vendus = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_medicaments_plus_vendus,
  title="Récupération des médicaments les plus vendus"
)

# 2.7. Médicaments les moins vendus
medicaments_moins_vendus = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_medicaments_moins_vendus,
  title="Récupération des médicaments les moins vendus"
)

# III. F I N A N C E
# 3.1. Chiffre d’affaires par jour
chiffre_affaires_par_jour = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_chiffre_affaire_daily,
  title="Récupération du chiffre d'affaires par jour"
)

# 3.2. Chiffre d’affaires par semaine
chiffre_affaires_par_semaine = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_chiffre_affaire_weekly,
  title="Récupération du chiffre d'affaires par semaine"
)

# 3.3. Chiffre d’affaires par mois
chiffre_affaires_par_mois = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_chiffre_affaire_monthly,
  title="Récupération du chiffre d'affaires par mois"
)

# 3.4. Chiffre d’affaires par annee
chiffre_affaires_par_annee = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_chiffre_affaire_yearly,
  title="Récupération du chiffre d'affaires par annee"
)

# 3.5. Marge bénéficiaire moyenne 
marge_beneficiaire_moyenne = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_marge_beneficiaire_moyenne,
  title="Récupération de la marge bénéficiaire moyenne"
)

# 3.6. Médicament qui rapporte plus
medicament_rapportant_plus = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_medicament_rapporte_plus,
  title="Récupération du médicament qui rapporte le plus"
)

# 3.6. Médicament qui rapporte moins
medicament_rapportant_moins = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_medicament_rapporte_moins,
  title="Récupération du médicament qui rapporte le moins"
)


# STYLES --------------------------------------
custom_css = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");

body {
  font-family: "Quicksand", sans-serif;
  justify-content: center;
  align-items: center;
  background-color: #ffffff !important;
}
.subtitle{
  font-family: "Quicksand", sans-serif;
  font-weight: bold;
  color: #fefefe;
  font-size: 1.8rem;
  margin-top: 2rem;
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
.card.green { background-color: #1abc9c; color: #1f1f1f; }
.card.purple { background-color: #b8a4e4; color: #1f1f1f; }
.card.red { background-color: #e74c3c; color: #1f1f1f; }
</style>
"""

# clustering employees style
clustering_employees_style = """
  <style>
  /* Supprimer le fond gris autour des widgets Streamlit */
  .stPlotlyChart {
      background-color: transparent;
      padding: 0;
      margin: 0;
  }
  div[data-testid="stVerticalBlock"] > div {
      background-color: transparent !important;
      box-shadow: none !important;
      padding: 0 !important;
  }
  </style>
"""

# talbe style
table_css = """
<style>
.table-container {
    font-family: Arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    color: #0aa;
    margin: 20px 0;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
    border-radius: 8px;
    overflow: hidden;
}
.table-container .subtitle{
  font-family: "Quicksand", sans-serif;
  font-weight: bold;
  color: #95a5a6;
  text-transform: uppercase;
  font-size: 1.5rem;
  margin-bottom: 0.3rem;
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

.row-table{
  background-color: #ffffff;
  padding: 50px 10px;
  margin: 5px 0;
  border-radius: 12px;
  color: #333;
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

# KPI STLYE
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
  gap: 12px;
  margin-bottom: 25px;
  font-family:"Roboto", cursive;

}

.kpi-card {
  background: #fff;
  border-radius: 15px;
  border: 1px solid #eee;
  padding: 20px;
  margin-bottom: 10px;
  flex: 1;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  text-align: center;
}
.card {
    background-color: #1e1e26;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    margin-bottom: 20px;
    color: white;
}
.kpi-title {
  color: #888;
  margin: 0;
  font-size: 1rem;
  font-weight: bold;
  text-align: right;
}
.kpi-value {
  font-size: 3rem;
  color: #000;
  font-weight: normal;
  text-align: right;
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


# IMAGES -------------------------------------------
# finance
finance_icon_b64 = get_base64_image("assets/icons/terminal.png")
finance_icon_html = f'<img src="data:image/png;base64,{finance_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# vente
ventes_icon_b64 = get_base64_image("assets/icons/vente.png")
ventes_icon_html = f'<img src="data:image/png;base64,{ventes_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# stock
stock_icon_b64 = get_base64_image("assets/icons/stock.png")
stock_icon_html = f'<img src="data:image/png;base64,{stock_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# perte
perte_icon_b64 = get_base64_image("assets/icons/perte.png")
perte_icon_html = f'<img src="data:image/png;base64,{perte_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# employees
employees_icon_b64 = get_base64_image("assets/icons/employees.png")
employees_icon_html = f'<img src="data:image/png;base64,{employees_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# salaire
salaire_icon_b64 = get_base64_image("assets/icons/salaire.png")
salaire_icon_html = f'<img src="data:image/png;base64,{salaire_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# age
age_icon_b64 = get_base64_image("assets/icons/age.png")
age_icon_html = f'<img src="data:image/png;base64,{age_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'




# HTML ----------------------------------------------
three_first_kpis_html = f"""
<div class="kpi-container" style="margin-top:-6rem;">
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
      {finance_icon_html}
      </div>
        <p class="kpi-title" style="font-size:1rem; color:#48494B;">Total Finance (MGA)</p>
        <p class="kpi-value" style="font-size:1.5rem;">{total_chiffre_affaire_str}</p>
    </div>
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
      {ventes_icon_html}
      </div>
        <p class="kpi-title" style="font-size:1rem; color:#48494B;">Total Ventes</p>
        <p class="kpi-value" style="font-size:1.6rem;">{nombre_total_vente_str}</p>
    </div>
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
      {stock_icon_html}
      </div>
        <p class="kpi-title" style="font-size:1rem; color:#48494B;">Valeur Stocks (MGA)</p>
        <p class="kpi-value" style="font-size:1.5rem;">{f"{int(valeur_totale_stock):,}".replace(",", " ")}</p>
    </div>
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
      {perte_icon_html}
      </div>
      <p class="kpi-title" style="font-size:1rem; color:#48494B;">
        Total Pertes (MGA)
      </p>
      <p class="kpi-value" style="font-size:1.5rem;">{f"{int(total_pertes_medicaments):,}".replace(",", " ")}</p>
    </div>

</div>
"""

# three_second_kpis_html = f"""
# <div class="kpi-container">
#     <div class="kpi-card">
#       <div class="kpi-title" style="font-size:1.2rem; color:#48494B;">
#           Total Pertes
#           <span style="font-size:0.9rem;">(Médicaments invendus)</span>
#       </div>
#       <div class="kpi-value" style="font-size:2rem;">{f"{int(total_pertes_medicaments):,}".replace(",", " ")}&nbsp;MGA</div>
#     </div>
#     <div class="kpi-card">
#         <p class="kpi-title" style="font-size:1.2rem; color:#48494B;">Valeur Stock</p>
#         <p class="kpi-value" style="font-size:2rem;">{f"{int(valeur_totale_stock):,}".replace(",", " ")}&nbsp;MGA</p>
#     </div>
#     <div class="kpi-card">
#         <p class="kpi-title" style="font-size:1.2rem; color:#48494B;">Total Médicaments</p>
#         <p class="kpi-value" style="font-size:2rem;">{nb_total_medicaments}</p>
#     </div>
# </div>
# """

def get_status(jours_restants):
    if jours_restants < 1:
        return '<span class="badge red">Déjà expiré</span>'
    elif jours_restants < 30:
        return f'<span class="badge grey">Dans {jours_restants} jours</span>'
    elif jours_restants >= 30:
        return f'<span class="badge green">Dans {jours_restants} jours</span>'
    else:
        return f'<span class="badge blue">Dans {jours_restants} jours</span>'

rows_table_html = """"""
for m in medicaments_expires[-5:]:
  rows_table_html += f"""
      <tr class="row-table">
          <td>{m['nom_medicament']}</td>
          <td>{m['date_expiration'].strftime('%d %B %Y')}</td>
          <td>{m['quantite_totale_restante']}</td>
          <td>{get_status(m['jours_restants'])}</td>
      </tr>
  """

table_head_medicaments_expired_html = f"""
<div class="table-container kpi-card">
<h2 class="subtitle">Médicaments expirés ou bientôt expirés</h2>
<table>
    <thead>
        <tr>
            <th>Médicament</th>
            <th>Date d'expiration</th>
            <th>Quantité restante</th>
            <th>Status d'expiration</th>
        </tr>
    </thead>
    <tbody>
    </tbody>
</table>
</div>
"""


# all employes
nombre_total_employes = employe_collection.count_distinct_agg(field_name="id_employe")

total_all_employes_html = f"""
  <div class="kpi-card" style="margin-bottom:1.5rem;">
    <div style="text-align: left; position:absolute;">
      {employees_icon_html}
    </div>
    <p class="kpi-title" color:#48494B;">Total Employés</p>
    <p class="kpi-value" style="font-size:1.5rem;">{nombre_total_employes}</p>
  </div>
  <div class="kpi-card" style="margin-bottom:1.5rem;">
    <div style="text-align: left; position:absolute;">
      {salaire_icon_html}
    </div>
    <p class="kpi-title" color:#48494B;">Salaire Moyen (MGA)</p>
    <p class="kpi-value" style="font-size:1.5rem;">{employe_views.salaire_moyen}</p>
  </div>
  <div class="kpi-card" style="margin-bottom:1.5rem;">
    <div style="text-align: left; position:absolute;">
      {age_icon_html}
    </div>
    <p class="kpi-title" color:#48494B;">Âge Moyen</p>
    <p class="kpi-value" style="font-size:1.5rem;">{round(employe_views.age_moyen)} ans</p>
  </div>
"""


# Exemples d'utilisation
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


