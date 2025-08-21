import streamlit as st
import numpy as np
import pandas as pd
from data.mongodb_client import MongoDBClient
from views import dashboard_views
from pipelines import pipelines_finance,pipeline_overview

from style import icons



#importation de baseDB via MongoDB
overview_collection = MongoDBClient(collection_name="overview")
vente_collection = MongoDBClient(collection_name="vente")
medicament_collection = MongoDBClient(collection_name="medicament")

# Overview docs
overveiw_docs = overview_collection.find_all_documents()



#Marge bénéficiaire moyenne
marge_benefice_moyen = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_marge_beneficiaire_moyenne,title="recuperation du marge beneficaire")

#Médicaments qui rapporte le plus
medoc_rapporte_plus = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_medicament_rapporte_plus,title="recuperation rapport plus")

#Médicaments qui rapporte moins
medoc_rapporte_moins = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_medicament_rapporte_moins,title="recuperation rapporte moins")

#Médicament avec la plus forte marge
medoc_forte_marge = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_plus_forte_marge,title="recuperation forte marge")

#Médicament avec la plus faible marge
medoc_faible_marge = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_plus_faible_marge,title="recuperation faible marge")

#Evolution Total des pertes dues aux médicaments invendus ou abîmés
Evolution_pertes = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_pertes_expiration_fig,title="recuperation pertes")


#chriffre d'affraire
CA_finance = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_chiffre_affaire_mensuel,title="recuperation CA jour")



kpis_html = f"""
  <div class="kpi-card">
    <div style="text-align: left; position:absolute;">
        {icons.finance_icon_html}
    </div>
    <p class="kpi-title">Total Finance (MGA)</p>
    <p class="kpi-value" style="font-size:1.5rem;">{dashboard_views.chiffre_affaire}</p>
  </div>
"""


