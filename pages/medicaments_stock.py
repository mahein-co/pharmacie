import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import load_data
from db import init_duckdb
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np


# Initialisation
st.set_page_config(page_title="Dashboard Pharmacie", layout="wide")
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">', unsafe_allow_html=True)

# Chargement CSS
# with open("style/pharmacie.css", "r") as css_file:
#     st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
# Dis à Python d'aller voir dans le dossier parent


# Chargement des données
df = load_data()

# Sidebar
with st.sidebar:
    if st.button("Recharger les données", key="reload", help="Cliquez pour recharger les données", use_container_width=True):
        st.cache_data.clear()
    st.sidebar.image("images/logoMahein.png", caption="", use_container_width=True)





# MEDICAMENT

st.markdown("<h3 style='color: green;'>Vue en details des Médicaments</h3>", unsafe_allow_html=True)

# Appliquer des styles CSS personnalisés pour les métriques
st.markdown("""
    <style>
        .metric-box {
            border-left: 5px solid #4CAF50;
            padding: 10px 15px;
            margin-bottom: 15px;
            border-radius: 6px;
            box-shadow: 1px 1px 4px rgba(0,0,0,0.05);
            background-color:  rgb(38, 39, 48);
        }
        .metric-label {
            font-size: 16px;
            color: white;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

if df is not None and "medicament" in df and "stock" in df and "detailVente" in df:
    medicament = df["medicament"]
    stock = df["stock"]
    vente_detail = df["detailVente"]

    merged_df = pd.merge(stock, medicament, on="ID_Medicament", how="left")

    con = duckdb.connect(database=":memory:")
    con.register("medicaments", merged_df)
    con.register("ventes", vente_detail)

    try:
        # Statistiques générales
        nb_total_medicaments = con.execute("SELECT COUNT(DISTINCT ID_Medicament) FROM medicaments").fetchone()[0]

        stats_stock = con.execute("""
            SELECT 
                ROUND(AVG(quantite_disponible), 2) AS stock_moyen,
                MIN(quantite_disponible) AS stock_min,
                MAX(quantite_disponible) AS stock_max
            FROM medicaments
        """).fetchdf()

        med_plus_vendu = con.execute("""
            SELECT m.Nom_Commercial AS nom, SUM(v.Quantité) AS total
            FROM ventes v
            JOIN stock s ON s.id_lot = v.id_lot
            JOIN medicament m ON m.ID_Medicament = s.ID_Medicament
            GROUP BY m.Nom_Commercial
            ORDER BY total DESC
            LIMIT 1
        """).fetchdf()

        # Top 5 pour graphe
        top5_vendus = con.execute("""
            SELECT m.Nom_Commercial AS nom, SUM(v.Quantité) AS total
            FROM ventes v
            JOIN stock s ON s.id_lot = v.id_lot
            JOIN medicament m ON m.ID_Medicament = s.ID_Medicament
            GROUP BY m.Nom_Commercial
            ORDER BY total DESC
            LIMIT 5
        """).fetchdf()

        med_stock_bas = con.execute("""
            SELECT Nom_Commercial, quantite_disponible 
            FROM medicaments 
            ORDER BY quantite_disponible ASC 
            LIMIT 1
        """).fetchdf()

        nb_categories = con.execute("SELECT COUNT(DISTINCT Categorie) FROM medicaments").fetchone()[0]

        med_cher = con.execute("""
            SELECT Nom_Commercial, Prix_Vente 
            FROM medicaments 
            ORDER BY Prix_Vente DESC 
            LIMIT 1
        """).fetchdf()

        med_moins_cher = con.execute("""
            SELECT Nom_Commercial, Prix_Vente 
            FROM medicaments 
            ORDER BY Prix_Vente ASC 
            LIMIT 1
        """).fetchdf()

        # AFFICHAGE DESIGN
        with st.container():
            st.markdown("### 📦 Stock des médicaments")

            col1, col2, col3 = st.columns(3)
            col1.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🔢 Total Médicaments</div>
                    <div class="metric-value">{nb_total_medicaments}</div>
                </div>
            """, unsafe_allow_html=True)

            col2.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📉Médicaments critiques en stock</div>
                    <div class="metric-value">{stats_stock["stock_min"][0]}</div>
                </div>
            """, unsafe_allow_html=True)

            col3.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📈Nombre total d’approvisionnements</div>
                    <div class="metric-value">{stats_stock["stock_max"][0]}</div>
                </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Erreur lors de l'affichage : {e}")
else:
    st.warning("Les données 'vente', 'detailVente' et 'client' ne sont pas disponibles.")


# Médicaments critiques en stock (<10 unités)

with st.container():

    st.markdown("<h3>Médicaments critiques en stock </h3>", unsafe_allow_html=True)

    # CSS personnalisé
    st.markdown("""
        <style>
            /* Fond noir général */
            body, .stApp {
                background-color: #0e0e0e;
                color: white;
            }

            /* Style du tableau */
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background-color: #0e0e0e;
                color: white;
            }

            thead tr {
                background-color: #28a745; /* Vert pharmacie */
                color: white;
                font-weight: bold;
            }

            tbody tr {
                background-color: #0e0e0e;
                color: white;
            }

            td, th {
                padding: 10px;
                text-align: left;
            }

            tbody tr:hover {
                background-color: #e0f0e0;
                color: #0e0e0e;
            }
        </style>
    """, unsafe_allow_html=True)

    # Contenu HTML du tableau
    html_table = """
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Name</th>
                    <th>Points</th>
                    <th>Team</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Domenic</td>
                    <td>88,110</td>
                    <td>dcode</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Sally</td>
                    <td>72,400</td>
                    <td>Students</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Nick</td>
                    <td>52,300</td>
                    <td>dcode</td>
                </tr>
            </tbody>
        </table>
    """

    # Affichage HTML du tableau
    st.markdown(html_table, unsafe_allow_html=True)



#Médicaments en surplus (>500 unités)
with st.container():
    
    st.markdown("<h3>Médicaments en surplus </h3>", unsafe_allow_html=True)

    # CSS personnalisé
    st.markdown("""
        <style>
            /* Fond noir général */
            body, .stApp {
                background-color: #0e0e0e;
                color: white;
            }

            /* Style du tableau */
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background-color: #0e0e0e;
                color: white;
            }

            thead tr {
                background-color: #28a745; /* Vert pharmacie */
                color: white;
                font-weight: bold;
            }

            tbody tr {
                background-color: #0e0e0e;
                color: white;
            }

            td, th {
                padding: 10px;
                text-align: left;
            }

            tbody tr:hover {
                background-color: #e0f0e0;
                color: #0e0e0e;
            }
        </style>
    """, unsafe_allow_html=True)

    # Contenu HTML du tableau
    html_table = """
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Name</th>
                    <th>Points</th>
                    <th>Team</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Domenic</td>
                    <td>88,110</td>
                    <td>dcode</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Sally</td>
                    <td>72,400</td>
                    <td>Students</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Nick</td>
                    <td>52,300</td>
                    <td>dcode</td>
                </tr>
            </tbody>
        </table>
    """

    # Affichage HTML du tableau
    st.markdown(html_table, unsafe_allow_html=True)


with st.container():
    
    st.markdown("<h3>Ruptures de stock sur le dernier mois</h3>", unsafe_allow_html=True)

    # CSS personnalisé
    st.markdown("""
        <style>
            /* Fond noir général */
            body, .stApp {
                background-color: #0e0e0e;
                color: white;
            }

            /* Style du tableau */
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background-color: #0e0e0e;
                color: white;
            }

            thead tr {
                background-color: #28a745; /* Vert pharmacie */
                color: white;
                font-weight: bold;
            }

            tbody tr {
                background-color: #0e0e0e;
                color: white;
            }

            td, th {
                padding: 10px;
                text-align: left;
            }

            tbody tr:hover {
                background-color: #e0f0e0;
                color: #0e0e0e;
            }
        </style>
    """, unsafe_allow_html=True)

    # Contenu HTML du tableau
    html_table = """
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Name</th>
                    <th>Points</th>
                    <th>Team</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Domenic</td>
                    <td>88,110</td>
                    <td>dcode</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Sally</td>
                    <td>72,400</td>
                    <td>Students</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Nick</td>
                    <td>52,300</td>
                    <td>dcode</td>
                </tr>
            </tbody>
        </table>
    """

    # Affichage HTML du tableau
    st.markdown(html_table, unsafe_allow_html=True)

with st.container():

    col1, col2 = st.columns(2)

    # Données exemples
    data = pd.DataFrame({
        'Médicament': ['Paracétamol', 'Ibuprofène', 'Amoxicilline', 'Aspirine'],
        'Rotation': [120, 85, 60, 150]
    })

    # 🔥 Colonne 1 : Médicament avec la plus forte rotation
    with col1:
        st.markdown("<h3>Médicament avec la plus forte rotation</h3>", unsafe_allow_html=True)

        data_high = data.sort_values('Rotation', ascending=False).reset_index(drop=True)

        max_rot = data_high['Rotation'].max()

        def add_fire(row, max_rotation):
            return f"{row['Rotation']} 🔥" if row['Rotation'] == max_rotation else str(row['Rotation'])

        data_high['label'] = data_high.apply(lambda row: add_fire(row, max_rot), axis=1)

        fig_high = px.bar(
            data_high,
            x='Rotation',
            y='Médicament',
            orientation='h',
            text='label',
            color='Rotation',
            color_continuous_scale=['#a8d5a2', '#28a745'],
        )

        fig_high.update_traces(textposition='inside', textfont_color='white')
        fig_high.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(autorange='reversed'),
            coloraxis_showscale=False
        )

        st.plotly_chart(fig_high)

    # ❄️ Colonne 2 : Médicament avec la plus faible rotation
    with col2:
        st.markdown("<h3>Médicament avec la plus faible rotation</h3>", unsafe_allow_html=True)

        data_low = data.sort_values('Rotation', ascending=True).reset_index(drop=True)

        min_rot = data_low['Rotation'].min()

        def add_snow(row, min_rotation):
            return f"{row['Rotation']} ❄️" if row['Rotation'] == min_rotation else str(row['Rotation'])

        data_low['label'] = data_low.apply(lambda row: add_snow(row, min_rot), axis=1)

        fig_low = px.bar(
            data_low,
            x='Rotation',
            y='Médicament',
            orientation='h',
            text='label',
            color='Rotation',
            color_continuous_scale=['#a8d5a2', '#28a745'],
        )

        fig_low.update_traces(textposition='inside', textfont_color='white')
        fig_low.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(autorange='reversed'),
            coloraxis_showscale=False
        )

        st.plotly_chart(fig_low)



# ------------------- Données d'exemple ------------------- #
    data_stock = pd.DataFrame({
        'Médicament': ['Paracétamol', 'Ibuprofène', 'Amoxicilline', 'Aspirine', 'Doliprane'],
        'Prix unitaire': [1500, 2000, 2500, 1000, 3000],
        'Quantité en stock': [50, 30, 20, 40, 10]
    })

    # ------------------- Calculs ------------------- #
    nb_total_medicaments = data_stock['Quantité en stock'].sum()
    valeur_stock = (data_stock['Prix unitaire'] * data_stock['Quantité en stock']).sum()

    plus_cher = data_stock.loc[data_stock['Prix unitaire'].idxmax()]
    moins_cher = data_stock.loc[data_stock['Prix unitaire'].idxmin()]

    # ------------------- CSS pour tableau ------------------- #
    st.markdown("""
        <style>
            .custom-table td {
                padding: 8px;
                border: 1px solid #ddd;
                text-align: left;
            }
            .custom-table th {
                background-color: #2d6a4f;
                color: white;
                padding: 10px;
                text-align: left;
            }
            .custom-table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 10px;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
        </style>
    """, unsafe_allow_html=True)


    # ------------------- Tableau HTML stylisé ------------------- #
    st.markdown("<h3>📋 Détails du stock</h3>", unsafe_allow_html=True)

    table_html = data_stock.to_html(classes="custom-table", index=False)
    st.markdown(table_html, unsafe_allow_html=True)
















