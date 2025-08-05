import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
# Data = medicament_views.medoc_surplus_result
# surplus = pd.DataFrame(list(Data))
# surplus["lots"]= surplus["lots"][0][0]["lot_id"]
# surplus.rename(columns={"_id": "Médicament", "total_quantite": "Total quantite"}, inplace=True)

# st.title("💊 Tableau des Médicaments sur plus")
# # 🎯 Filtres
# with st.sidebar:
#     st.header("🔍 Filtres")
#     medicament_list = surplus["Médicament"].unique()
#     selected_medicaments = st.multiselect(
#         "Nom du médicament",
#         options=medicament_list,
#         default=medicament_list
#     )

# # 🎯 Application des filtres
# filtered_df = surplus[surplus["Médicament"].isin(selected_medicaments)]

# # 💅 CSS personnalisé
# st.markdown("""
#     <style>
#     .ag-root-wrapper {
#         border-radius: 20px;
#         font-family: Arial, sans-serif;
#         overflow: hidden;
#         box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
#     }
#     .ag-header, .ag-cell {
#         font-family: Arial, sans-serif;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # 🎨 Affichage du tableau avec AgGrid
# st.subheader("📋 Médicaments filtrés")
# gb = GridOptionsBuilder.from_dataframe(filtered_df)
# gb.configure_default_column(filter=True, sortable=True, resizable=True, editable=False)
# gb.configure_grid_options(domLayout='normal')
# grid_options = gb.build()

# AgGrid(
#     filtered_df,
#     gridOptions=grid_options,
#     theme='material',  # autres options : 'streamlit', 'alpine', 'balham'
#     fit_columns_on_grid_load=True,
#     height=300,
#     width='100%'
# )
# 🎯 Filtres



# ✅ Données 
Data = medicament_views.medoc_critique_result
critique = pd.DataFrame(list(Data))
critique["lots"]= critique["lots"][0][0]["lot_id"]
critique.rename(columns={"_id": "Médicament", "total_quantite": "Total quantite"}, inplace=True)

st.markdown("""
    <style>
        .custom-card {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        .custom-card h4 {
            text-align: center;
            margin-top: 0;
            margin-bottom: 20px;
        }
        .table-wrapper {
            overflow-x: auto;
        }
        .custom-table {
            width: 100%;
            border-collapse: collapse;
        }
        .custom-table th, .custom-table td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        .custom-table th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        .custom-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
""", unsafe_allow_html=True)

# 👉 2. Fonction pour afficher une carte avec titre centré + tableau
def render_table(critique, titre="📋 Tableau des données"):
    table_html = f"""
    <div class='custom-card'>
        <h4>{titre}</h4>
        <div class='table-wrapper'>
            <table class='custom-table'>
                <tr>
                    {''.join([f"<th>{col}</th>" for col in critique.columns])}
                </tr>
                {''.join([
                    "<tr>" + ''.join([f"<td>{row[col]}</td>" for col in critique.columns]) + "</tr>"
                    for _, row in critique.iterrows()
                ])}
            </table>
        </div>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

# 👉 3. Appel
render_table(critique, titre="📊 Medicaments en critique")


# # 🎯 Filtres
# with st.sidebar:
#     st.header("🔍 Filtres")
#     medicament_list = critique["Médicament"].unique()
#     selected_medicaments = st.multiselect(
#         "Nom du médicament",
#         options=medicament_list,
#         default=medicament_list
#     )

# # # 🎯 Application des filtres
# # filtered_df = critique[critique["Médicament"].isin(selected_medicaments)]

# # 💅 CSS personnalisé
# st.markdown("""
#     <style>
#     .ag-root-wrapper {
#         border-radius: 20px;
#         font-family: Arial, sans-serif;
#         overflow: hidden;
#         box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
#     }
#     .ag-header, .ag-cell {
#         font-family: Arial, sans-serif;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # 🎨 Affichage du tableau avec AgGrid
# st.subheader("📋 Médicaments filtrés")
# gb = GridOptionsBuilder.from_dataframe(filtered_df)
# gb.configure_default_column(filter=True, sortable=True, resizable=True, editable=False)
# gb.configure_grid_options(domLayout='normal')
# grid_options = gb.build()

# AgGrid(
#     filtered_df,
#     gridOptions=grid_options,
#     theme='material',  # autres options : 'streamlit', 'alpine', 'balham'
#     fit_columns_on_grid_load=True,
#     height=300,
#     width='100%'
# )


data = medicament_views.medoc_surplus_result
df_surplus = pd.DataFrame(data)
df_surplus["lots"]= df_surplus["lots"][0][0]["lot_id"]
df_surplus.rename(columns={"_id":"Médicaments","total_quantite":"Total Quantite"},inplace=True)

# 👉 1. CSS global (UNE SEULE FOIS)
st.markdown("""
    <style>
        .custom-card {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        .custom-card h4 {
            text-align: center;
            margin-top: 0;
            margin-bottom: 20px;
        }
        .table-wrapper {
            overflow-x: auto;
        }
        .custom-table {
            width: 100%;
            border-collapse: collapse;
        }
        .custom-table th, .custom-table td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        .custom-table th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        .custom-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
""", unsafe_allow_html=True)

# 👉 2. Fonction pour afficher une carte avec titre centré + tableau
def render_table(df_surplus, titre="📋 Tableau des données"):
    table_html = f"""
    <div class='custom-card'>
        <h4>{titre}</h4>
        <div class='table-wrapper'>
            <table class='custom-table'>
                <tr>
                    {''.join([f"<th>{col}</th>" for col in df_surplus.columns])}
                </tr>
                {''.join([
                    "<tr>" + ''.join([f"<td>{row[col]}</td>" for col in df_surplus.columns]) + "</tr>"
                    for _, row in df_surplus.iterrows()
                ])}
            </table>
        </div>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

# 👉 3. Appel
render_table(df_surplus, titre="📊 Medicaments en sur plus")



# data = medicament_views.rupture_stock
# df_rupture = pd.DataFrame(data)
# # df_rupture["lots"]= df_rupture["lots"][0][0]["lot_id"]
# print("resultat : ",df_rupture)
# # 👉 1. CSS global (UNE SEULE FOIS)
# st.markdown("""
#     <style>
#         .custom-card {
#             background-color: #f9f9f9;
#             padding: 20px;
#             border-radius: 15px;
#             box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
#             margin-bottom: 30px;
#         }
#         .custom-card h4 {
#             text-align: center;
#             margin-top: 0;
#             margin-bottom: 20px;
#         }
#         .table-wrapper {
#             overflow-x: auto;
#         }
#         .custom-table {
#             width: 100%;
#             border-collapse: collapse;
#         }
#         .custom-table th, .custom-table td {
#             padding: 10px;
#             border: 1px solid #ddd;
#             text-align: left;
#         }
#         .custom-table th {
#             background-color: #f0f0f0;
#             font-weight: bold;
#         }
#         .custom-table tr:nth-child(even) {
#             background-color: #f9f9f9;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # 👉 2. Fonction pour afficher une carte avec titre centré + tableau
# def render_table(df_rupture, titre="📋 Tableau des données"):
#     table_html = f"""
#     <div class='custom-card'>
#         <h4>{titre}</h4>
#         <div class='table-wrapper'>
#             <table class='custom-table'>
#                 <tr>
#                     {''.join([f"<th>{col}</th>" for col in df_rupture.columns])}
#                 </tr>
#                 {''.join([
#                     "<tr>" + ''.join([f"<td>{row[col]}</td>" for col in df_rupture.columns]) + "</tr>"
#                     for _, row in df_rupture.iterrows()
#                 ])}
#             </table>
#         </div>
#     </div>
#     """
#     st.markdown(table_html, unsafe_allow_html=True)

# # 👉 3. Appel
# render_table(df_rupture, titre="📊 Rupture du stock sur derniers mois")

with st.container():

    col1, col2 = st.columns(2)

    with col1:
        data = medicament_views.medoc_forte_rotation
        df_forte_rotation = pd.DataFrame(data)

        # ✅ Renommage correct des colonnes
        df_forte_rotation.rename(columns={"_id": "Médicaments", "quantite_totale_vendue": "Quantite Totale Vendue"}, inplace=True)

        df_forte_rotation = df_forte_rotation.sort_values(by="Quantite Totale Vendue", ascending=False).head(3)

        # CSS pour la carte
        st.markdown("""
            <style>
            .card {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            </style>
            """, unsafe_allow_html=True)

        # Graphique
        fig = px.bar(
            df_forte_rotation,
            x="Quantite Totale Vendue",
            y="Médicaments",
            orientation='h',
            text="Quantite Totale Vendue",
            color="Quantite Totale Vendue",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Médicaments à forte rotation"
        )

        fig.update_layout(
            title=dict(
                text="Médicaments à forte rotation",
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            xaxis_title="Quantité vendue",
            yaxis_title="Médicaments",
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=50, b=10)
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        data = medicament_views.medoc_faible_rotation
        df_faible_rotation = pd.DataFrame(data)

        # ✅ Renommage correct des colonnes
        df_faible_rotation.rename(columns={"_id": "Médicaments", "quantite_totale_vendue": "Quantite Totale Vendue"}, inplace=True)

        df_faible_rotation = df_faible_rotation.sort_values(by="Quantite Totale Vendue", ascending=False).head(3)

        # CSS pour la carte
        st.markdown("""
            <style>
            .card {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            </style>
            """, unsafe_allow_html=True)

        # Graphique
        fig = px.bar(
            df_faible_rotation,
            x="Quantite Totale Vendue",
            y="Médicaments",
            orientation='h',
            text="Quantite Totale Vendue",
            color="Quantite Totale Vendue",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Médicaments à faible rotation"
        )

        fig.update_layout(
            title=dict(
                text="Médicaments à faible rotation",
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            xaxis_title="Quantité vendue",
            yaxis_title="Médicaments",
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=50, b=10)
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)








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


