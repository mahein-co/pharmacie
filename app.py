from datetime import timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from utils import load_data
from db import init_duckdb
# from sklearn.linear_model import LinearRegression
# from sklearn.model_selection import train_test_split
import numpy as np

from data.mongodb_ip_manager import MongoDBIPManager

# Initialisation
st.set_page_config(page_title="Dashboard Pharmacie", layout="wide")
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">', unsafe_allow_html=True)


def mongodb_ip_manager():   
    manager = MongoDBIPManager()

    current_ip = manager.get_current_ip()
    if current_ip:
        if not manager.ip_exists(current_ip):
            manager.add_ip(current_ip)


mongodb_ip_manager()

# Chargement CSS
# with open("style/pharmacie.css", "r") as css_file:
#     st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Chargement des données
df = load_data()

# Sidebar
with st.sidebar:
    if st.button("Recharger les données", key="reload", help="Cliquez pour recharger les données", use_container_width=True):
        st.cache_data.clear()
    st.sidebar.image("images/logoMahein.png", caption="", use_container_width=True)


if df is not None and "medicament" in df and "stock" in df:
    # Extraction des DataFrames
    medicament_df = df["medicament"]
    stock_df = df["stock"]

    # Fusion des données
    merged_df = pd.merge(stock_df, medicament_df, on="ID_Medicament", how="left")

    # Connexion à DuckDB
    con = duckdb.connect(database=':memory:')
    con.register('pharmacie', merged_df)

    # 💊 Titre principal
    st.markdown("""
        <h1 style='font-size: 32px; color: #4CAF50; margin-bottom: 0;'>PHARMACIE METROPOLE</h1>
        <p style='font-size: 16px; color: gray;'>Vue d'ensemble des indicateurs clés</p>
        <hr style='margin-top: 10px; margin-bottom: 20px;' />
    """, unsafe_allow_html=True)

    # 🔎 Indicateurs SQL
    metrics_queries = {
        "💰 Chiffre d'affaires total": "SELECT SUM(Prix_Vente * Stock_Disponible) FROM pharmacie",
        "📦 Valeur totale du stock": "SELECT SUM(Stock_Disponible) FROM pharmacie",
        "🔢 Nombre total de ventes": "SELECT COUNT(DISTINCT Nom_Commercial) FROM pharmacie",
        "⚠️Nombre total d’alimentation": "SELECT COUNT(*) FROM pharmacie WHERE Stock_Disponible < 10"
    }

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

    try:
        # Répartir les métriques en colonnes
        cols = st.columns(4)
        for i, (label, query) in enumerate(metrics_queries.items()):
            value = con.execute(query).fetchone()[0]
            value = "N/A" if value is None else f"{value:,.2f}"

            # Affichage HTML perfsonnalisé avec bordure gauche
            html_metric = f"""
                <div class="metric-box">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
            """
            cols[i].markdown(html_metric, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Une erreur est survenue lors du calcul des indicateurs : {e}")

else:
    st.error("❌ Les données 'medicament' et 'stock' sont manquantes ou invalides.")


st.markdown("<h2 style='color: green;'>Médicaments</h2>", unsafe_allow_html=True)

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
            st.markdown("### 📦 Vue Global de Médicaments")

            col1,col2,col3 = st.columns(3)
            col1.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🔢 Total Médicaments</div>
                    <div class="metric-value">{nb_total_medicaments}</div>
                </div>
            """, unsafe_allow_html=True)


            col2.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📈 Total des pertes dues aux médicaments invendus</div>
                    <div class="metric-value">{stats_stock["stock_max"][0]}</div>
                </div>
            """, unsafe_allow_html=True)

            col3.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📊 Quantité totale de médicaments approvisionnés</div>
                    <div class="metric-value">{stats_stock["stock_moyen"][0]}</div>
                </div>
            """, unsafe_allow_html=True)
        


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

        # Affichage HTML personnalisé
        st.markdown(html_table, unsafe_allow_html=True)



    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des statistiques : {e}")
else:
    st.error("❌ Les données 'medicament', 'stock' et 'detailVente' ne sont pas présentes dans le DataFrame.")

# ventes

st.markdown("<h2 style='color: green;'> ventes</h2>", unsafe_allow_html=True)

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

if df is not None and "vente" in df and "detailVente" in df:
    ventes = df["vente"]
    detail_ventes = df["detailVente"]

    con = duckdb.connect(database=":memory:")
    con.register("ventes", ventes)
    con.register("detailVente", detail_ventes)

    try:
        # Statistiques des ventes
        nb_total_ventes = con.execute("SELECT COUNT(ID_Vente) FROM ventes").fetchone()[0]

        ca_total = con.execute("SELECT SUM(Total_Payer) FROM ventes").fetchone()[0]

        ca_moyen = con.execute("SELECT AVG(Total_Payer) FROM ventes").fetchone()[0]

        vente_max = con.execute("SELECT MAX(Total_Payer) FROM ventes").fetchone()[0]

        vente_min = con.execute("SELECT MIN(Total_Payer) FROM ventes").fetchone()[0]

        nb_ventes_annulees = con.execute("SELECT COUNT(ID_Vente) FROM ventes WHERE Mode_Paiement = 'Annulé'").fetchone()[0]

        nb_ventes_en_attente = con.execute("SELECT COUNT(ID_Vente) FROM ventes WHERE Mode_Paiement = 'En attente'").fetchone()[0]

        # AFFICHAGE DESIGN
        with st.container():
            st.markdown("### 📦 Statistiques des ventes")

            col1, col2, col3 = st.columns(3)
            col1.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🔢 Nombre total de fournisseurs</div>
                    <div class="metric-value">{nb_total_ventes}</div>
                </div>
            """, unsafe_allow_html=True)

            col2.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💰 Chiffre d'affaires total</div>
                    <div class="metric-value">{ca_total:.2f} €</div>
                </div>
            """, unsafe_allow_html=True)

            col3.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💸 Montant moyen par vente</div>
                    <div class="metric-value">{ca_moyen:.2f} €</div>
                </div>
            """, unsafe_allow_html=True)

            col4, col5 = st.columns([2, 1])
            col4.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💵 Vente la plus élevée</div>
                    <div class="metric-value">{vente_max:.2f} €</div>
                </div>
            """, unsafe_allow_html=True)

            col5.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💲 Vente la plus basse</div>
                    <div class="metric-value">{vente_min:.2f} €</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        with st.container():
            st.markdown("### 🛑 Statistiques des ventes en attente ou annulées")
            col6, col7 = st.columns(2)
            col6.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">❌ Nombre de ventes annulées</div>
                    <div class="metric-value">{nb_ventes_annulees}</div>
                </div>
            """, unsafe_allow_html=True)

            col7.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">⏳ Nombre de ventes en attente de paiement</div>
                    <div class="metric-value">{nb_ventes_en_attente}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des statistiques des ventes : {e}")
else:
    st.error("❌ Les données 'ventes' et 'detailVente' ne sont pas présentes dans le DataFrame.")



