import streamlit as st
from data.mongodb_client import MongoDBClient
from views import dashboard_views
from pipelines import pipeline_overview

from style import icons






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


# ========== KPI Cards ===============
kpis_html = f"""
<div class="kpi-container">
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
        {icons.medicament_icon_html}
      </div>
      <p class="kpi-title">Nombre de médicaments</p>
      <p class="kpi-value" style="font-size:1.5rem;">{dashboard_views.nb_total_medicaments}</p>
    </div>
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
        {icons.medicament_critique_icon_html}
      </div>
      <p class="kpi-title">Médicaments -70 unités</p>
      <p class="kpi-value" style="font-size:1.5rem;">{len(medoc_critique_result)}</p>
    </div>
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
        {icons.medicament_surplus_icon_html}
      </div>
      <p class="kpi-title">Médicaments +700 unités</p>
      <p class="kpi-value" style="font-size:1.5rem;">{len(medoc_surplus_result)}</p>
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


