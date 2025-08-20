import streamlit as st
from data.mongodb_client import MongoDBClient
from pipelines import pipelines_ventes, pipeline_overview
from views import dashboard_views

from style import icons





#initiation a mongoDB 
# vente_collection = MongoDBClient(collection_name="vente")
# employe_collection = MongoDBClient(collection_name="employe")
# medicament_collection = MongoDBClient(collection_name="medicament")
overview_collection = MongoDBClient(collection_name="overview")

#3--nombres de ventes
# nombre_ventes = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_nb_ventes,title="recuperation nb ventes")
# # nombre_ventes_str = f"{nombre_ventes:,}".replace(",", " ")


#3.top vendeur

top_vendeur = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_top_vendeur,title="recuperaction top 3")

#4.top medicaments

top_medicaments = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_medicaments_plus_vendus,title="recuperation top medicaments")

#5.Médicaments les moins vendus
Medoc_moins_vendus = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_medicaments_moins_vendus,title="recuperation moins venus")

#6.Non habilité vendeur
vendeur_non_habilite = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_vendeur_non_habilite,title="recuperation vendeur non habilite")

#hitmap
saisonalite = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_quantite_jour,title="recuperation hitmap")

#evolution
Medoc_evolution = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_quantite_mois,title="recuperation evolution")

# ========== KPI Cards ===============
def get_kpis(chiffre_affaire, nombre_ventes) : 
  panier_moyen =  round(chiffre_affaire/ nombre_ventes)
  chiffre_affaire_str = f"{int(chiffre_affaire):,}".replace(",", " ") 
  nombre_ventes_str = f"{nombre_ventes:,}".replace(",", " ")
  panier_moyen_str = f"{panier_moyen:,}".replace(",", " ")
  kpis_html = f"""
    <div class="kpi-container">
    <div class="kpi-card">
      <div style="text-align: left; position:absolute;">
      {icons.finance_icon_html}
      </div>
        <p class="kpi-title"> Chiffre d'affaires (MGA)</p>
        <p class="kpi-value" style="font-size: 1.5rem;">{chiffre_affaire_str}</p>
    </div>
    <div class="kpi-card">
    <div style="text-align: left; position:absolute;">
      {icons.panier_icon_html}
      </div>
        <p class="kpi-title">Panier moyen (MGA)</p>
        <p class="kpi-value" style="font-size: 1.5rem;">{panier_moyen_str}</p>
    </div>
    <div class="kpi-card">
    <div style="text-align: left; position:absolute;">
      {icons.ventes_icon_html}
      </div>
        <p class="kpi-title">Nombre de ventes</p>
        <p class="kpi-value" style="font-size: 1.5rem;">{22}</p>
    </div>
    </div>
    """
  return kpis_html

