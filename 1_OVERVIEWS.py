import math
import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
from data.mongodb_ip_manager import MongoDBIPManager
from datetime import date
from style import style, icons
from views import dashboard_views, employe_views 
from pipelines import pipeline_overview

st.markdown("""
    <style>
        [data-testid="stToolbar"] [aria-label="Settings"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# Initialisation
st.set_page_config(page_title="Dashboard Pharmacie", layout="wide")
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">', unsafe_allow_html=True)

# importation de style CSS
st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.table_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)
st.markdown(style.button_style, unsafe_allow_html=True)


# PING IP
def mongodb_ip_manager():   
    manager = MongoDBIPManager()

    current_ip = manager.get_current_ip()
    if current_ip:
        if not manager.ip_exists(current_ip):
            manager.add_ip(current_ip)
mongodb_ip_manager()

# Chargement CSS
with open("style/pharmacie.css", "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.sidebar.image("assets/images/logoMahein.png", caption="", use_container_width=True)

# GLOBAL VARIABLES ------------------------------------------------
TODAY = date.today()
date_debut = dashboard_views.first_date_vente if dashboard_views.first_date_vente else TODAY
date_fin = TODAY

# -----------------------------------------------------------------
# # 1. Chiffre d'affaires
# chiffre_affaire = pipeline_overview.get_chiffre_affaire_total()
# # 2. Nombre de ventes
# nombre_ventes = pipeline_overview.get_nombre_de_ventes()
# # 3. Valeur de stock
# valeur_stock = pipeline_overview.get_valeur_totale_stock() 


#1. Chiffre d'affaires
df_CA = pd.DataFrame(dashboard_views.chiffre_affaire_total)
# DASHBOARD TITLE
col_title, col_empty, col_filter = st.columns([2, 2, 2])
with col_title:
    html("""
    <style>
        @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
        
        .box {
            color: #0A9548;
            font-family: 'Dancing Script', cursive;
            font-size: 74px;
            margin-top:-1rem;
            margin-bottom: 2rem;
        }
    </style>
    <div class="box">Overview</div>
    """)

# FILTRE DATE -------------------------------------------------
with col_filter:
    col1,col2 = st.columns([3,2])
    if "date_range" not in st.session_state:
        st.session_state.date_range = None

    with col1:
        st.session_state.date_range = st.date_input("CHOISISSEZ 02 DATES", value=(date_debut, TODAY))
    
    with col2:
        apply_button = st.button("Appliquer");

# 1. DAHSBOARD --------------------------------------------
# 1. chriffres d'affraire
# if apply_button:
#     if len(st.session_state.date_range) == 2:
#         date_debut, date_fin = st.session_state.date_range
#         if (date_debut <= date_fin):
            # # 1. Chiffre d'affaires
            # chiffre_affaire = pipeline_overview.get_chiffre_affaire_total(
            #     start_date=date_debut, 
            #     end_date=date_fin
            # )
            # # 2. Nombre de ventes
            # nombre_ventes = pipeline_overview.get_nombre_de_ventes(
            #     start_date=date_debut, 
            #     end_date=date_fin
            # )
            # # 3. Valeur de stock
            # valeur_stock = pipeline_overview.get_valeur_totale_stock(end_date=date_fin)

# SCORECARD KPIS -----------------------------------------
three_second_kpis_html = f"""
    <div class="kpi-container-secondary">
        <div class="kpi-card">
        <div style="text-align: left; position:absolute;">
        {icons.employees_icon_html}
        </div>
            <p class="kpi-title" style="font-size:1rem;">Nombre d'employés</p>
            <p class="kpi-value" style="font-size:1.5rem;">{employe_views.Nb_employers}</p>
        </div>
        <div class="kpi-card">
        <div style="text-align: left; position:absolute;">
        {icons.ventes_icon_html}
        </div>
            <p class="kpi-title" style="font-size:1rem;">Nombre de ventes</p>
            <p class="kpi-value" style="font-size:1.6rem;">{dashboard_views.format_number_to_str(nombre_ventes)}
        </div>
        <div class="kpi-card">
        <div style="text-align: left; position:absolute;">
        {icons.fournisseur_icon_html}
        </div>
            <p class="kpi-title" style="font-size:1rem;">Nombre de fournisseurs</p>
            <p class="kpi-value" style="font-size:1.5rem;">{pipeline_overview.nb_fournisseur}</p>
        </div>

    </div>
"""
st.markdown(dashboard_views.first_container_kpis_html(
    chiffre_affaire,
    valeur_stock
), unsafe_allow_html=True)
st.markdown(three_second_kpis_html, unsafe_allow_html=True)


# 3. MEDICAMENTS --------------------------------------------
# DATA-FRAME MEDICAMENTS --------------------------------------
data = dashboard_views.medicaments_expires
df = pd.DataFrame(data)
# Renommer les colonnes
df.rename(columns={
    "_id": "Lot",
    "nom_medicament": "Médicament",
    "date_expiration": "Date d'expiration",
    "quantite_totale_restante": "Quantité restante",
    "jours_restants": "Jours restants"
}, inplace=True)

# Fonction pour le statut
def get_status(jours):
    if jours < 1:
        color = "#f44336"
        text = "Déjà expiré"
    elif jours < 50:
        color = "#ff9800"
        text = f"Dans {jours} jours"
    else:
        color = "#4caf50"
        text = f"Dans {jours} jours"
    return f"""
    <div style="
        background-color: {color};
        color: white;
        text-decoration:uppercase;
        padding: 6px 12px;
        border-radius: 12px;
        font-weight: normal;
        display: inline-block;
        min-width: 100px;
        text-align: center;
    ">{text}</div>
    """

df["Status"] = df["Jours restants"].apply(get_status)

# 🔍 Barre de recherche en haut
st.markdown(style.placeholder_style, unsafe_allow_html=True)
# Champ texte avec placeholder
search = st.text_input("Recherche", placeholder="Rechercher un médicament déjà ou bientôt expiré", label_visibility="collapsed")

# Filtrage selon la recherche
if search:
    df = df[df.astype(str).apply(lambda row: row.str.contains(search, case=False), axis=1).any(axis=1)]

# 🎨 CSS tableau stylisé
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

# 🔢 Pagination : affichage tableau avec page
# Valeurs disponibles
rows_per_page_options = [5]
# Valeur par défaut
rows_per_page = st.session_state.get("rows_per_page", 5)

# Nombre total de pages
total_rows = len(df)
total_pages = math.ceil(total_rows / rows_per_page)

# Index de page courant
current_page = st.session_state.get("current_page", 1)
start = (current_page - 1) * rows_per_page
end = start + rows_per_page
df_page = df.iloc[start:end]

# 🧾 Affichage tableau
def render_table(df_part):
    table_html = "<div class='table-wrapper'><table class='custom-table'>"
    table_html += "<tr>" + "".join([f"<th>{col}</th>" for col in df_part.columns]) + "</tr>"
    for _, row in df_part.iterrows():
        table_html += "<tr>"
        for col in df_part.columns:
            table_html += f"<td>{row[col]}</td>"
        table_html += "</tr>"
    table_html += "</table></div>"
    st.markdown(table_html, unsafe_allow_html=True)

if df.empty:
    st.markdown("""
    <div class='custom-card'>
        <h4>Médicaments expiré</h4>
        <p style='text-align:center; color: #888;'>Aucune Data</p>
    </div>
""", unsafe_allow_html=True)
else:
    # Affiche le tableau filtré et paginé
    render_table(df_page)

# Bas de tableau : choix nombre de lignes et navigation
col1, col2 = st.columns(2)

with col1:
    rows_per_page = st.selectbox("Afficher par page :", rows_per_page_options, index=rows_per_page_options.index(rows_per_page))
    st.session_state["rows_per_page"] = rows_per_page
    total_pages = math.ceil(len(df) / rows_per_page)  # Recalcul après changement

with col2:
    current_page = st.number_input(f"Page (1-{total_pages})", min_value=1, max_value=total_pages, value=current_page, step=1)
    st.session_state["current_page"] = current_page



