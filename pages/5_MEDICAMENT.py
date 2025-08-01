import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit.components.v1 import html
from views import medicament_views,dashboard_views
from data.mongodb_client import MongoDBClient
from pipelines import pipeline_overview




# Initialisation
st.set_page_config(page_title="MEDICAMENT", layout="wide")

html("""
<style>
    @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
    
  .box {
    color: #eee;
    padding: 20px;
    font-family: 'Dancing Script', cursive;
    border-radius: 10px;
    font-size: 74px;
  }
</style>
<div class="box">Médicament</div>
""")

st.markdown(medicament_views.custom_css,unsafe_allow_html=True)
st.markdown(medicament_views.kpis_style,unsafe_allow_html=True)
if medicament_views.overview_collection :
  st.markdown(medicament_views.kpis_html,unsafe_allow_html=True)
  # st.markdown(medicament_views.table_medicaments_critiques_html,unsafe_allow_html=True)
  # st.markdown(medicament_views.table_medicaments_surplus_html,unsafe_allow_html=True)

else:
    st.error("Il est impossible de charger les données depuis la database.")



# ✅ Données 
Data = medicament_views.medoc_surplus_result
surplus = pd.DataFrame(list(Data))
surplus["lots"]= surplus["lots"][0][0]["lot_id"]
surplus.rename(columns={"_id": "Médicament", "total_quantite": "Total quantite"}, inplace=True)

st.title("💊 Tableau des Médicaments sur plus")
# 🎯 Filtres
with st.sidebar:
    st.header("🔍 Filtres")
    medicament_list = surplus["Médicament"].unique()
    selected_medicaments = st.multiselect(
        "Nom du médicament",
        options=medicament_list,
        default=medicament_list
    )

# 🎯 Application des filtres
filtered_df = surplus[surplus["Médicament"].isin(selected_medicaments)]

# 💅 CSS personnalisé
st.markdown("""
    <style>
    .ag-root-wrapper {
        border-radius: 20px;
        font-family: Arial, sans-serif;
        overflow: hidden;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    .ag-header, .ag-cell {
        font-family: Arial, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# 🎨 Affichage du tableau avec AgGrid
st.subheader("📋 Médicaments filtrés")
gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_default_column(filter=True, sortable=True, resizable=True, editable=False)
gb.configure_grid_options(domLayout='normal')
grid_options = gb.build()

AgGrid(
    filtered_df,
    gridOptions=grid_options,
    theme='material',  # autres options : 'streamlit', 'alpine', 'balham'
    fit_columns_on_grid_load=True,
    height=300,
    width='100%'
)


# ✅ Données 
Data = medicament_views.medoc_critique_result
critique = pd.DataFrame(list(Data))
critique["lots"]= critique["lots"][0][0]["lot_id"]
critique.rename(columns={"_id": "Médicament", "total_quantite": "Total quantite"}, inplace=True)

st.title("💊 Tableau des Médicaments sur plus")
# 🎯 Filtres
with st.sidebar:
    st.header("🔍 Filtres")
    medicament_list = critique["Médicament"].unique()
    selected_medicaments = st.multiselect(
        "Nom du médicament",
        options=medicament_list,
        default=medicament_list
    )

# 🎯 Application des filtres
filtered_df = critique[critique["Médicament"].isin(selected_medicaments)]

# 💅 CSS personnalisé
st.markdown("""
    <style>
    .ag-root-wrapper {
        border-radius: 20px;
        font-family: Arial, sans-serif;
        overflow: hidden;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    .ag-header, .ag-cell {
        font-family: Arial, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# 🎨 Affichage du tableau avec AgGrid
st.subheader("📋 Médicaments filtrés")
gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_default_column(filter=True, sortable=True, resizable=True, editable=False)
gb.configure_grid_options(domLayout='normal')
grid_options = gb.build()

AgGrid(
    filtered_df,
    gridOptions=grid_options,
    theme='material',  # autres options : 'streamlit', 'alpine', 'balham'
    fit_columns_on_grid_load=True,
    height=300,
    width='100%'
)






# import streamlit as st
# import pandas as pd

# # 📊 Données de stock (exemple actuel et précédent)
# data = {
#     "Médicament": ["Paracétamol", "Ibuprofène", "Amoxicilline", "Aspirine"],
#     "Stock actuel": [50, 20, 35, 5],
#     "Stock précédent": [45, 30, 40, 10]
# }

# df = pd.DataFrame(data)

# # ➕ Calcul de variation %
# df["Évolution (%)"] = ((df["Stock actuel"] - df["Stock précédent"]) / df["Stock précédent"]) * 100
# df["Évolution (%)"] = df["Évolution (%)"].round(2)

# # 💡 Fonction pour style d'évolution (avec emoji et couleur)
# def format_variation(val):
#     if val > 0:
#         return f"🟢 +{val}%"
#     elif val < 0:
#         return f"🔴 {val}%"
#     else:
#         return f"⚪  0%"

# df["Évolution"] = df["Évolution (%)"].apply(format_variation)

# # 🧼 Suppression de la colonne brute
# df_affichage = df[["Médicament", "Stock actuel", "Stock précédent", "Évolution"]]

# # 🎨 CSS custom pour style carte
# st.markdown("""
# <style>
# .metric-table td {
#     padding: 0.5em 1em;
#     font-size: 1.1em;
# }
# .metric-table th {
#     background-color: #f0f2f6;
#     padding: 0.5em 1em;
#     font-size: 1.1em;
# }
# </style>
# """, unsafe_allow_html=True)

# # 📋 Affichage HTML simulé
# st.markdown("<h3>📦 Suivi des stocks par médicament</h3>", unsafe_allow_html=True)
# st.markdown(df_affichage.to_html(classes="metric-table", index=False, escape=False), unsafe_allow_html=True)


