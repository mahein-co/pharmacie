import streamlit as st
from data.mongodb_client import MongoDBClient
from views import dashboard_views
from pipelines import pipeline_overview








#importation de data dans le MongoDB
overview_collection = MongoDBClient(collection_name="overview")

medoc_surplus_result = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_medicament_surplus,title="recuperation Medoc sur plus")
try:
    medoc_surplus = medoc_surplus_result[1]["total_quantite"] if medoc_surplus_result else 0
except Exception as e:
    medoc_surplus = 0 

medoc_critique_result = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_medicament_critique,title="recuperation en critique")
try:
    medoc_critique = medoc_critique_result[1]["total_quantite"] if medoc_critique_result else 0
except Exception as e:
    medoc_critique = 0

#rupurture du stock sur dernier mois
rupture_stock = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_rupture_stock,title="recuperation du rupture")

#medicaments plus fort rotation 
medoc_forte_rotation = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_medicament_forte_rotation,title="recuperation Medicaments forte rotation")

#medicaments faible rotation 
medoc_faible_rotation = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_medicament_faible_rotation,title="recuperation Medicaments faible rotation")

#medicaments moins cher 
medoc_moins_cher = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_medicaments_moins_cher,title="recuperation de moins cher")

#medicaments plus cher
medoc_plus_cher = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_medicaments_plus_cher,title="recuperation plus cher")









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
kpis_html = f"""
<div class="kpi-container">
    <div class="kpi-card">
        <p class="kpi-title" style="font-size:1.2rem;">Total Medicaments</p>
        <p class="kpi-value" style="font-size:2rem;">{dashboard_views.nb_total_medicaments}</p>
    </div>
    <div class="kpi-card">
        <p class="kpi-title" style="font-size:1.2rem;">Total medicaments en critiques en stock</p>
        <p class="kpi-value" style="font-size:2rem;">{medoc_critique}</p>
    </div>
    <div class="kpi-card">
        <p class="kpi-title" style="font-size:1.2rem;">Medicaments en surplus</p>
        <p class="kpi-value" style="font-size:2rem;">{medoc_surplus}</p>
    </div>
</div>
"""


table_medicaments_critiques_html = """
<div class="table-container kpi-card style="margin-bottom: 30px;">
<h2 class="subtitle">Médicaments en critiques</h2>
<table>
    <thead>
        <tr>
            <th>Médicament</th>
            <th>Quantité critiques</th>
            <th>Status d'expiration</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Leads</td>
            <td>0</td>
            <td><span class="badge grey">Dans 15 jours</span></td>
        </tr>
        <tr>
            <td>Valeur de la commande</td>
            <td>213,12€</td>
            <td><span class="badge red">Déjà expiré</span></td>
        </tr>
        <tr>
            <td>Commissions</td>
            <td>0€</td>
            <td><span class="badge green">Dans 30 jours</span></td>
        </tr>
    </tbody>
</table>
</div>
"""


