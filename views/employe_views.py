import streamlit as st 
from data.mongodb_client import MongoDBClient
from pipelines import pipeline_overview,pipelines_employe

from style import icons


#importation DATABASE via MongoDB
# employe_collection = MongoDBClient(collection_name="employe")
# employe_documents = employe_collection.find_all_documents()
overview_collection = MongoDBClient(collection_name="overview")

# REQUETES ------------------
#2--Salaire moyen 
salaire_moyen = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_salaire_moyen,title="salaire moyen")

try:
    salaire_moyen = salaire_moyen[0]["salaire_moyen"] if salaire_moyen else 0
    salaire_moyen = round(salaire_moyen)
    salaire_moyen = f"{salaire_moyen:,}".replace(",", " ")
except Exception as e:
    salaire_moyen = 0

# 1--Nombre total employers 
Nb_employers = overview_collection.count_distinct_agg(field_name="nom_employe")

#3-- Age moyen 

age_moyen = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_age_moyen,title="age moyen")

try:
    age_moyen = age_moyen[0]["age_moyen"] if age_moyen else 0
except Exception as e:
    age_moyen = 0


#effectif employer par categorie 
effectif_par_employe_categorie = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_eff_categorie,title="recuperation effectifs par categorie")

#effectif employer par fonction
effectif_par_employe_fonction = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_eff_fonction,title="recuperation effectifs par fonction")



kpis_html = f"""
<div class="kpi-container">
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
        {icons.employees_icon_html}
      </div>
        <p class="kpi-title">Nombre Total Employé</p>
        <p class="kpi-value" style="font-size:1.5rem;">{Nb_employers}</p>
    </div>
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
        {icons.salaire_icon_html}
      </div>
        <p class="kpi-title">Salaire Moyen (MGA)</p>
        <p class="kpi-value" style="font-size:1.5rem;">{salaire_moyen}</p>
    </div>
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
        {icons.age_icon_html}
      </div>
        <p class="kpi-title">Age moyen</p>
        <p class="kpi-value" style="font-size:1.5rem;">{round(age_moyen)} ans</p>
    </div>
</div>
"""