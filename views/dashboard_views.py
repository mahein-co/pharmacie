import pandas as pd
from data.mongodb_client import MongoDBClient
from st_aggrid import AgGrid

from pipelines import pipeline_overview
# from views import employe_views

from style import icons

# Initialisation a MongoDB
vente_collection = MongoDBClient(collection_name="vente")
overview_collection = pipeline_overview.overview_collection
medicament_collection = MongoDBClient(collection_name="medicament")
employe_collection = MongoDBClient(collection_name="employe")

pipeline_get_employes = [
  {
    "$group": {
      "_id": "$nom_employe", 
      "date_embauche": { "$last": "$date_embauche" }, 
      "salaire": { "$last": "$salaire" } 
    }
  },
  {
    "$project": {
      "_id": 0,
      "nom_employe": "$_id",
      "date_embauche": 1,
      "salaire": 1
    }
  }
] 

all_employes = employe_collection.find_all_documents()
nombre_total_employes = employe_collection.count_distinct_agg(field_name="id_employe")

vente_docs = vente_collection.find_all_documents()
overview_docs = overview_collection.find_all_documents()
medicament_docs = medicament_collection.find_all_documents()

# I- D A S H B O A R D
# 1.2. valeur totale du stock
# 1.3. nombre total de vente
nombre_total_vente_str = f"{pipeline_overview.total_sales:,}".replace(",", " ")

# 1.4. Nombre total de médicaments
nb_total_medicaments = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_nb_medicaments,title="recuperation nb medoc par date de vente")
df_nb_medoc = pd.DataFrame(nb_total_medicaments)
nb_medoc = df_nb_medoc["nb_medicaments"].sum()

# 1.5. Total des pertes dues aux médicaments invendus
pertes_medicaments = overview_collection.make_specific_pipeline(
  pipeline=pipeline_overview.pipeline_pertes_expiration, 
  title="Calcul des pertes dues aux médicaments invendus"
)

# 1.6. Dataframe des ventes
# overview_docs = overview_collection.find_all_documents()
df_ventes = pd.DataFrame(overview_docs)
df_ventes = df_ventes.drop_duplicates(subset=["id_vente"])
first_date_vente = df_ventes["date_de_vente"].min() if not df_ventes.empty else None


# Execute the pipeline
chiffre_affaire_total = overview_collection.make_specific_pipeline(pipeline=pipeline_overview.pipeline_chiffre_affaire_total, title="CHIFFRE D'AFFAIRE TOTAL")

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

#valeur de stock 

valeur_stock_result = overview_collection.make_specific_pipeline(
pipeline=pipeline_overview.pipeline_valeur_totale_stock, 
title="Calcul de la valeur totale du stock"
)

# HTML ----------------------------------------------
def format_number_to_str(value):
    """Format a number with spaces as thousands separator."""
    return f"{int(value):,}".replace(",", " ")

def first_container_kpis_html(chiffre_affaire, valeur_totale_stock, total_pertes_medicaments):
    chiffre_affaire = format_number_to_str(chiffre_affaire)
    valeur_totale_stock = format_number_to_str(valeur_totale_stock)
    total_pertes_medicaments = format_number_to_str(total_pertes_medicaments)

    three_first_kpis_html = f"""
        <div class="kpi-container">
            <div class="kpi-card">
            <div style="text-align: left; position:absolute;">
            {icons.finance_icon_html}
            </div>
                <p class="kpi-title" style="font-size:1rem;">Chiffre d'affaires (MGA)</p>
                <p class="kpi-value" style="font-size:1.5rem;">{chiffre_affaire}</p>
            </div>
            <div class="kpi-card">
            <div style="text-align: left; position:absolute;">
            {icons.stock_icon_html}
            </div>
                <p class="kpi-title" style="font-size:1rem;">Valeur des stocks (MGA)</p>
                <p class="kpi-value" style="font-size:1.5rem;">{valeur_totale_stock}</p>
            </div>
            <div class="kpi-card">
            <div style="text-align: left; position:absolute;">
            {icons.perte_icon_html}
            </div>
            <p class="kpi-title" style="font-size:1rem; color:#48494B;">
                Pertes (MGA)
            </p>
            <p class="kpi-value" style="font-size:1.5rem;">{total_pertes_medicaments}</p>
            </div>

        </div>
    """
    return three_first_kpis_html

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

# # all employes
# total_all_employes_html = f"""
#   <div class="kpi-card" style="margin-bottom:1.5rem;">
#     <div style="text-align: left; position:absolute;">
#       {icons.employees_icon_html}
#     </div>
#     <p class="kpi-title" color:#48494B;">Total Employés</p>
#     <p class="kpi-value" style="font-size:1.5rem;">{nombre_total_employes}</p>
#   </div>
#   <div class="kpi-card" style="margin-bottom:1.5rem;">
#     <div style="text-align: left; position:absolute;">
#       {icons.salaire_icon_html}
#     </div>
#     <p class="kpi-title" color:#48494B;">Salaire Moyen (MGA)</p>
#     <p class="kpi-value" style="font-size:1.5rem;">{employe_views.salaire_moyen}</p>
#   </div>
#   <div class="kpi-card" style="margin-bottom:1.5rem;">
#     <div style="text-align: left; position:absolute;">
#       {icons.age_icon_html}
#     </div>
#     <p class="kpi-title" color:#48494B;">Âge Moyen</p>
#     <p class="kpi-value" style="font-size:1.5rem;">{round(employe_views.age_moyen)} ans</p>
#   </div>
# """


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


