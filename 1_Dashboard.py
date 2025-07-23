from datetime import timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from utils import load_data
from db import init_duckdb
# import numpy as np
# import asyncio

from data.mongodb_ip_manager import MongoDBIPManager
from data.mongodb_client import MongoDBClient
from data import mongodb_pipelines


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



# Initialisation a MongoDB
vente_collection = MongoDBClient(collection_name="vente")
medicament_collection = MongoDBClient(collection_name="medicament")
employe_collection = MongoDBClient(collection_name="employe")

# I- FIRST LINE OF SCORECARD
if vente_collection and medicament_collection:
    # 1. chiffre d'affaire total
    chiffre_affaire = vente_collection.make_specific_pipeline(pipeline=mongodb_pipelines.pipeline_chiffre_affaire, title="Calcul du chiffre d'affaire")
    try:
        total_chiffre_affaire = chiffre_affaire[0]["montant_total"] if chiffre_affaire else 0
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul du chiffre d'affaire : {e}")
        total_chiffre_affaire = 0

    # # 2. valeur totale du stock
    # valeur_stock = vente_collection.make_specific_pipeline(pipeline=mongodb_pipelines.pipeline_somme_valeur_stock, title="Calcul de la valeur totale du stock")
    # try:
    #     valeur_totale_stock = valeur_stock[0]["valeur_totale_stock"] if valeur_stock else 0
    # except Exception as e:
    #     st.error(f"❌ Erreur lors du calcul de la valeur totale du stock : {e}")
    #     valeur_totale_stock = 0
        
    # 3. nombre total de vente
    nombre_total_vente = vente_collection.count_distinct_agg(field_name="id_vente")

    # 4. nombre total d'alimentation
    nombre_alimentation = medicament_collection.make_specific_pipeline(pipeline=mongodb_pipelines.pipeline_nombre_alimentations, title="Recuperation de nombre total d'alimentation")
    try:
        nombre_total_alimentation = nombre_alimentation[0]["nombre_total_alimentations"] if nombre_alimentation else 0
    except Exception as e :
        st.error(f"❌ Erreur lors du calcul du nombre total d'alimentation : {e}")
        nombre_total_alimentation = 0


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
        <h1 style='font-size: 32px; color: #4CAF50; margin-bottom: 0;'>PHARMACIE MÉTROPOLE</h1>
        <p style='font-size: 16px; color: gray;'>Vue d'ensemble des indicateurs clés</p>
        <hr style='margin-top: 10px; margin-bottom: 20px;' />
    """, unsafe_allow_html=True)

    # 🔎 Indicateurs SQL
    metrics_queries = {
        "Chiffre d'affaires total": f"{total_chiffre_affaire:,}".replace(",", " ") + "&nbsp; MGA",
        # "📦 Valeur totale du stock": f"{valeur_totale_stock:,}".replace(",", " ") + " MGA",
        "🔢 Nombre total de ventes": f"{nombre_total_vente:,}".replace(",", " "),
        "⚠️Nombre total d’alimentation": nombre_total_alimentation
        # "⚠️Nombre total d’alimentation": "SELECT COUNT(*) FROM pharmacie WHERE Stock_Disponible < 10"
        # "📦 Valeur totale du stock": "SELECT SUM(Stock_Disponible) FROM pharmacie",
    }   

    st.markdown("""
        <style>
            .metric-box {
                border-left: 5px solid #4CAF50;
                padding: 10px 7px;
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
        cols = st.columns(3)
        for i, (key, value) in enumerate(metrics_queries.items()):
            # value = con.execute(query).fetchone()[0]
            # value = "N/A" if value is None else f"{value:,.2f}"

            # Affichage HTML perfsonnalisé avec bordure gauche
            html_metric = f"""
                <div class="metric-box">
                    <div class="metric-label">{key}</div>
                    <div class="metric-value">{value}</div>
                </div>
            """
            cols[i].markdown(html_metric, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Une erreur est survenue lors du calcul des indicateurs : {e}")
else:
    st.error("Il est impossible de charger les données depuis la database.")


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

# II- SECOND LINE OF SCORECARD
if medicament_collection and employe_collection:
    # 2.1. Nombre total de médicaments
    nb_total_medicaments = medicament_collection.count_distinct_agg(field_name="id_medicament")
    
    # 2.2. Total des pertes dues aux médicaments invendus
    pertes_medicaments = medicament_collection.make_specific_pipeline(pipeline=mongodb_pipelines.pipeline_valeur_perte, title="Calcul des pertes dues aux médicaments invendus")
    try:
        total_pertes_medicaments = pertes_medicaments[0]["perte_totale"] if pertes_medicaments else 0
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des pertes dues aux médicaments invendus : {e}")
        total_pertes_medicaments = 0

    # 2.4. Nombre total de fournisseur
    nb_total_fournisseurs = medicament_collection.count_distinct_agg(field_name="fournisseur")

    
    # 2.5. Médicaments expirés ou bientôt expirés
    medicament_collection = medicament_collection.get_collection()
    # medicaments_expires = medicament_collection.make_specific_pipeline(pipeline=mongodb_pipelines.pipeline_medicaments_expirants, title="Récupération des médicaments expirés ou bientôt expirés")
    medicaments_expires = list(medicament_collection.aggregate(mongodb_pipelines.pipeline_expirations))


    medicament = df["medicament"]
    stock = df["stock"]
    vente_detail = df["detailVente"]

    merged_df = pd.merge(stock, medicament, on="ID_Medicament", how="left")

    con = duckdb.connect(database=":memory:")
    con.register("medicaments", merged_df)
    con.register("ventes", vente_detail)

    try:
        # Statistiques générales

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

            col1,col2,col4 = st.columns(3)
            col1.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🔢 Total Médicaments</div>
                    <div class="metric-value">{nb_total_medicaments}</div>
                </div>
            """, unsafe_allow_html=True)


            col2.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📈 Total des pertes dues aux médicaments invendus</div>
                    <div class="metric-value">{f"{total_pertes_medicaments:,}".replace(",", " ")} &nbsp;MGA</div>
                </div>
            """, unsafe_allow_html=True)

            # col3.markdown(f"""
            #     <div class="metric-box">
            #         <div class="metric-label">📊 Quantité totale de médicaments approvisionnés</div>
            #         <div class="metric-value">{stats_stock["stock_moyen"][0]}</div>
            #     </div>
            # """, unsafe_allow_html=True)

            col4.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📊 Nombre total de fournisseurs</div>
                    <div class="metric-value">{nb_total_fournisseurs}</div>
                </div>
            """, unsafe_allow_html=True)
        

        #Médicaments expirés ou bientôt expirés (alerte)
        # CSS personnalisé
        st.markdown("Médicaments expirés ou bientôt expirés")
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


st.markdown("Vendeur non habilité")
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

# try:

#     except Exception as e:
#         st.error(f"❌ Erreur lors du calcul des statistiques : {e}")
# else:
#     st.error("❌ Les données 'medicament', 'stock' et 'detailVente' ne sont pas présentes dans le DataFrame.")






