from datetime import timedelta
import streamlit as st
from streamlit.components.v1 import html

import pandas as pd
import plotly.express as px
import duckdb
from utils import load_data
from db import init_duckdb
import streamlit as st


from data.mongodb_ip_manager import MongoDBIPManager
from data import mongodb_pipelines
from streamlit.components.v1 import html

# views
from views import dashboard_views


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
with open("style/pharmacie.css", "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


# Chargement des données
df = load_data()

# Sidebar
with st.sidebar:
    if st.button("Recharger les données", key="reload", help="Cliquez pour recharger les données", use_container_width=True):
        st.cache_data.clear()
    st.sidebar.image("images/logoMahein.png", caption="", use_container_width=True)

# -----------------------------------------------------------------
# TITLE
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
<div class="box">Dashboard</div>
""")

# importation de style CSS
# st.markdown(dashboard_views.custom_css, unsafe_allow_html=True)
st.markdown(dashboard_views.kpis_style, unsafe_allow_html=True)


# I- FIRST LINE OF SCORECARD
if dashboard_views.vente_collection and dashboard_views.medicament_collection:

    # Extraction des DataFrames
    medicament_df = df["medicament"]
    stock_df = df["stock"]
    
    # Fusion des données
    merged_df = pd.merge(stock_df, medicament_df, on="ID_Medicament", how="left")

    # Connexion à DuckDB
    con = duckdb.connect(database=':memory:')
    con.register('pharmacie', merged_df)


    # 🔎 Indicateurs SQL
    metrics_queries = {
        # "📦 Valeur totale du stock": f"{valeur_totale_stock:,}".replace(",", " ") + " MGA",
        # "⚠️Nombre total d’alimentation": "SELECT COUNT(*) FROM pharmacie WHERE Stock_Disponible < 10"
        # "📦 Valeur totale du stock": "SELECT SUM(Stock_Disponible) FROM pharmacie",
    }   

    st.markdown(dashboard_views.kpis_html, unsafe_allow_html=True)

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
if dashboard_views.medicament_collection and dashboard_views.employe_collection:
    # 2.1. Nombre total de médicaments
    nb_total_medicaments = dashboard_views.medicament_collection.count_distinct_agg(field_name="id_medicament")
    
    # 2.2. Total des pertes dues aux médicaments invendus
    pertes_medicaments = dashboard_views.medicament_collection.make_specific_pipeline(pipeline=mongodb_pipelines.pipeline_valeur_perte, title="Calcul des pertes dues aux médicaments invendus")
    try:
        total_pertes_medicaments = pertes_medicaments[0]["perte_totale"] if pertes_medicaments else 0
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des pertes dues aux médicaments invendus : {e}")
        total_pertes_medicaments = 0

    # 2.4. Nombre total de fournisseur
    nb_total_fournisseurs = dashboard_views.medicament_collection.count_distinct_agg(field_name="fournisseur")

    
    # 2.5. Médicaments expirés ou bientôt expirés
    medicaments_expires = dashboard_views.medicament_collection.make_specific_pipeline(pipeline=mongodb_pipelines.pipeline_expirations, title="Récupération des médicaments expirés ou bientôt expirés")


    
    rows_html = ""
    for row_medicament in medicaments_expires[:7]:
        rows_html += f"""
        <tr>
            <td>{row_medicament['nom']}</td>
            <td>{row_medicament['arrival_date'].strftime('%d-%m-%Y')}</td>
            <td style="color:red;">{row_medicament['date_expiration'].strftime('%d-%m-%Y')}</td>
            <td>{row_medicament['prix_unitaire']} Ar</td>
            <td>{row_medicament['Quantity_arrival']}</td>
        </tr>
        """

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
        html_table = f"""
            <table>
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Date d'arrivée</th>
                        <th>Date d'expiration</th>
                        <th>Prix unitaire</th>
                        <th>Quantité restante</th>
                    </tr>
                </thead>
                <tbody>
                {rows_html}
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






