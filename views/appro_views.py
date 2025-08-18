import streamlit as st
from data.mongodb_client import MongoDBClient
from pipelines import pipeline_overview

from style import icons

# initiation a mongoDB 
overview_collection = MongoDBClient(collection_name="overview")

Commande_moyen = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_commande_moyen_global,title="recuperation")

try:
    commande_moyen = Commande_moyen[0]["moyenne_commandes_par_fournisseur"] if Commande_moyen else 0
except Exception as e :
    commande_moyen = 0

Commande_moyen_par_fournisseur = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_commande_moyen_par_fournisseurs,title="recuperation par commande fornisseurs")


#Temps moyen de livraison par fournisseur
Temps_moyen_fournisseur = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_temps_moyen_livraison_fournisseur,title="recuperation temps moyen fournisseurs")

#Nombre de livraisons en retard par fournisseur
taux_retard_livraison = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_taux_retard_livraison,title="recuperation taux livraison")

#Mois plus Aprovisionnements
Mois_plus_Appro = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_mois_plus_approvisionnement,title="recuperation mois plus approvisionnements")


# ========== KPI Cards ===============
kpis_html = f"""
<div class="kpi-container">
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
      {icons.fournisseur_icon_html}
      </div>
      <p class="kpi-title">Grossistes - Fournisseurs (nombre)</p>
      <p class="kpi-value" style="font-size:1.5rem;">{pipeline_overview.nb_fournisseur}</p>
    </div>
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
      {icons.commande_icon_html}
      </div>
      <p class="kpi-title">Commandes moyennes</p>
      <p class="kpi-value" style="font-size:1.5rem;">{int(commande_moyen)}</p>
    </div>
</div>
"""


