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
                /* Style du tableau */
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }

                thead tr {
                    background-color: #28a745; /* Vert pharmacie */
                    color: white;
                    font-weight: bold;
                }

                tbody tr {
                    background-color: #f9f9f9;
                    color: black;
                }

                td, th {
                    padding: 10px;
                    text-align: left;
                }

                tbody tr:hover {
                    background-color: #e0f0e0;
                }
            </style>
        """, unsafe_allow_html=True)
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
                    <div class="metric-label">🔢 Nombre total de ventes</div>
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










# client 


from datetime import datetime, timedelta


st.markdown("<h2 style='color: green;'> clients</h2>", unsafe_allow_html=True)

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

# Vérification des données disponibles
if df is not None and "client" in df and "vente" in df:
    clients = df["client"]
    ventes = df["vente"]

    # Connexion à DuckDB pour effectuer des calculs
    con = duckdb.connect(database=":memory:")
    con.register("clients_data", clients)
    con.register("ventes_data", ventes)

    try:
        # Vérifier que les DataFrames clients et ventes contiennent des données valides
        if clients is not None and ventes is not None:
            # Nombre total de clients enregistrés
            nb_total_clients_result = con.execute("SELECT COUNT(DISTINCT ID_Client) FROM clients_data").fetchone()
            nb_total_clients = nb_total_clients_result[0] if nb_total_clients_result is not None else 0

            # Nombre de clients fidèles (> 10 achats)
            nb_clients_fideles_result = con.execute("""
                SELECT COUNT(DISTINCT ID_Client) 
                FROM ventes_data 
                GROUP BY ID_Client
                HAVING COUNT(ID_Vente) > 10
            """).fetchone()
            nb_clients_fideles = nb_clients_fideles_result[0] if nb_clients_fideles_result is not None else 0

            # Nombre de nouveaux clients (dernier mois)
            one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            nb_nouveaux_clients_result = con.execute(f"""
                SELECT COUNT(DISTINCT ID_Client)
                FROM ventes_data
                WHERE Date_Vente >= '{one_month_ago}'
            """).fetchone()
            nb_nouveaux_clients = nb_nouveaux_clients_result[0] if nb_nouveaux_clients_result is not None else 0

            # Nombre moyen d'achats par client
            nb_moyen_achats_client_result = con.execute("""
                SELECT AVG(nb_achats) 
                FROM (
                    SELECT COUNT(ID_Vente) AS nb_achats
                    FROM ventes_data
                    GROUP BY ID_Client
                ) AS achats
            """).fetchone()
            nb_moyen_achats_client = nb_moyen_achats_client_result[0] if nb_moyen_achats_client_result is not None else 0

            # Client avec le plus d'achats
            client_plus_achats = con.execute("""
                SELECT ID_Client, COUNT(ID_Vente) AS total_achats
                FROM ventes_data
                GROUP BY ID_Client
                ORDER BY total_achats DESC
                LIMIT 1
            """).fetchdf()

            # Vérifier si client_plus_achats a des données valides
            if not client_plus_achats.empty:
                client_max = client_plus_achats['ID_Client'][0]
                achats_max = client_plus_achats['total_achats'][0]
            else:
                client_max = "Inconnu"
                achats_max = 0

            # AFFICHAGE DESIGN
            with st.container():
                st.markdown("### 👥 Statistiques des clients")

                # Disposition en colonnes pour un affichage structuré
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-label">🔢 Nombre total de clients</div>
                        <div class="metric-value">{nb_total_clients}</div>
                    </div>
                """, unsafe_allow_html=True)

                col2.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-label">🤝 Clients fidèles (> 10 achats)</div>
                        <div class="metric-value">{nb_clients_fideles}</div>
                    </div>
                """, unsafe_allow_html=True)

                col3.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-label">🆕 Nouveaux clients (dernier mois)</div>
                        <div class="metric-value">{nb_nouveaux_clients}</div>
                    </div>
                """, unsafe_allow_html=True)

                col4, col5 = st.columns([2, 1])
                col4.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-label">💡 Nombre moyen d'achats par client</div>
                        <div class="metric-value">{nb_moyen_achats_client}</div>
                    </div>
                """, unsafe_allow_html=True)

                col5.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-label">🏆 Client avec le plus d'achats</div>
                        <div class="metric-value">{client_max} ({achats_max} achats)</div>
                    </div>
                """, unsafe_allow_html=True)

        else:
            st.error("❌ Les données clients ou ventes sont invalides ou manquantes.")
        st.markdown("---")
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des statistiques des clients : {e}")
else:
    st.error("❌ Les données 'client' ou 'vente' ne sont pas présentes dans le DataFrame.")






# fourniseurs


st.markdown("<h2 style='color: green;'>fournisseurs</h2>", unsafe_allow_html=True)

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

# Vérification des données disponibles
if df is not None and "fournisseur" in df and "commande" in df:
    fournisseurs = df["fournisseur"]
    commandes = df["commande"]

    # Convertir les dates dans le DataFrame commandes
    commandes["DateCommande"] = pd.to_datetime(commandes["DateCommande"], errors="coerce")
    commandes["DateLivraisonPrevue"] = pd.to_datetime(commandes["DateLivraisonPrevue"], errors="coerce")

    # Connexion à DuckDB pour effectuer des calculs
    con = duckdb.connect(database=":memory:")
    con.register("fournisseurs_data", fournisseurs)
    con.register("commandes_data", commandes)

    try:
        # Nombre total de fournisseurs
        nb_total_fournisseurs_result = con.execute("""
            SELECT COUNT(DISTINCT ID_Fournisseur) FROM fournisseurs_data
        """).fetchone()
        nb_total_fournisseurs = nb_total_fournisseurs_result[0] if nb_total_fournisseurs_result else 0

        # Fournisseur le plus utilisé
        fournisseur_le_plus_utilise_result = con.execute("""
            SELECT f.ID_Fournisseur, f.Nom, f.Prenom, COUNT(c.ID_Commande) AS total_commandes
            FROM commandes_data c
            JOIN fournisseurs_data f ON c.ID_Fournisseur = f.ID_Fournisseur
            GROUP BY f.ID_Fournisseur, f.Nom, f.Prenom
            ORDER BY total_commandes DESC
            LIMIT 1
        """).fetchdf()

        if not fournisseur_le_plus_utilise_result.empty:
            fournisseur_utilise = f"{fournisseur_le_plus_utilise_result['Nom'][0]} {fournisseur_le_plus_utilise_result['Prenom'][0]}"
            commandes_utilise = fournisseur_le_plus_utilise_result['total_commandes'][0]
        else:
            fournisseur_utilise = "Inconnu"
            commandes_utilise = 0

        # Fournisseur avec le plus grand retard
        fournisseur_retard_max_result = con.execute("""
            SELECT f.ID_Fournisseur, f.Nom, f.Prenom, 
                   MAX(DATEDIFF('day', CAST(c.DateCommande AS DATE), CAST(c.DateLivraisonPrevue AS DATE))) AS max_retard
            FROM commandes_data c
            JOIN fournisseurs_data f ON c.ID_Fournisseur = f.ID_Fournisseur
            WHERE c.DateLivraisonPrevue IS NOT NULL AND c.DateCommande IS NOT NULL
            GROUP BY f.ID_Fournisseur, f.Nom, f.Prenom
            ORDER BY max_retard DESC
            LIMIT 1
        """).fetchdf()

        if not fournisseur_retard_max_result.empty:
            fournisseur_retard = f"{fournisseur_retard_max_result['Nom'][0]} {fournisseur_retard_max_result['Prenom'][0]}"
            retard_max = fournisseur_retard_max_result['max_retard'][0]
        else:
            fournisseur_retard = "Inconnu"
            retard_max = 0

        # Moyenne de commandes par fournisseur
        nb_moyen_commandes_fournisseur_result = con.execute("""
            SELECT AVG(nb_commandes) 
            FROM (
                SELECT COUNT(ID_Commande) AS nb_commandes
                FROM commandes_data
                GROUP BY ID_Fournisseur
            ) AS commandes
        """).fetchone()
        nb_moyen_commandes_fournisseur = round(nb_moyen_commandes_fournisseur_result[0], 2) if nb_moyen_commandes_fournisseur_result else 0

        # Affichage des métriques
        with st.container():
            st.markdown("### 📦 Statistiques des fournisseurs")

            col1, col2, col3 = st.columns(3)
            col1.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🔢 Nombre total de fournisseurs</div>
                    <div class="metric-value">{nb_total_fournisseurs}</div>
                </div>
            """, unsafe_allow_html=True)

            col2.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🔥 Fournisseur le plus utilisé</div>
                    <div class="metric-value">{fournisseur_utilise} ({commandes_utilise} commandes)</div>
                </div>
            """, unsafe_allow_html=True)

            col3.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">⏳ Fournisseur avec le plus grand retard</div>
                    <div class="metric-value">{fournisseur_retard} ({retard_max} jours de retard)</div>
                </div>
            """, unsafe_allow_html=True)

            col4, col5 = st.columns([2, 1])
            col4.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💡 Nombre moyen de commandes par fournisseur</div>
                    <div class="metric-value">{nb_moyen_commandes_fournisseur}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des statistiques des fournisseurs : {e}")

else:
    st.error("❌ Les données 'fournisseur' ou 'commande' ne sont pas présentes dans le DataFrame.")
















# transaction


st.markdown("<h2 style='color: green;'>Transactions</h2>", unsafe_allow_html=True)

st.markdown("""
    <style>
        .metric-box {
            border-left: 5px solid #4CAF50;
            padding: 10px 15px;
            margin-bottom: 15px;
            border-radius: 6px;
            box-shadow: 1px 1px 4px rgba(0,0,0,0.05);
            background-color: rgb(38, 39, 48);
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

# Vérification des données disponibles
if df is not None and "transaction" in df:
    transactions = df["transaction"]

    # Convertir les dates dans le DataFrame transactions
    transactions["Date_Transaction"] = pd.to_datetime(transactions["Date_Transaction"], errors="coerce")

    # Connexion à DuckDB pour effectuer des calculs
    con = duckdb.connect(database=":memory:")
    con.register("transactions_data", transactions)

    try:
        # Nombre total de transactions
        nb_total_transactions_result = con.execute("""
            SELECT COUNT(*) FROM transactions_data
        """).fetchone()
        nb_total_transactions = nb_total_transactions_result[0] if nb_total_transactions_result else 0

        # Transactions par mode de paiement (Espèces, CB, Virement)
        nb_transactions_espèces_result = con.execute("""
            SELECT COUNT(*) FROM transactions_data WHERE Mode_Paiement = 'Espèces'
        """).fetchone()
        nb_transactions_espèces = nb_transactions_espèces_result[0] if nb_transactions_espèces_result else 0

        nb_transactions_CB_result = con.execute("""
            SELECT COUNT(*) FROM transactions_data WHERE Mode_Paiement = 'CB'
        """).fetchone()
        nb_transactions_CB = nb_transactions_CB_result[0] if nb_transactions_CB_result else 0

        nb_transactions_virement_result = con.execute("""
            SELECT COUNT(*) FROM transactions_data WHERE Mode_Paiement = 'Virement'
        """).fetchone()
        nb_transactions_virement = nb_transactions_virement_result[0] if nb_transactions_virement_result else 0

        # Transactions par type de transaction (Entrée, Sortie)
        nb_transactions_entrée_result = con.execute("""
            SELECT COUNT(*) FROM transactions_data WHERE Type_Transaction = 'Entrée'
        """).fetchone()
        nb_transactions_entrée = nb_transactions_entrée_result[0] if nb_transactions_entrée_result else 0

        nb_transactions_sortie_result = con.execute("""
            SELECT COUNT(*) FROM transactions_data WHERE Type_Transaction = 'Sortie'
        """).fetchone()
        nb_transactions_sortie = nb_transactions_sortie_result[0] if nb_transactions_sortie_result else 0

        # Affichage des métriques
        with st.container():
            st.markdown("### 💳 Statistiques des Transactions")

            # Disposition en colonnes pour un affichage structuré
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📊 Nombre total de transactions</div>
                    <div class="metric-value">{nb_total_transactions}</div>
                </div>
            """, unsafe_allow_html=True)

            col2.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💶 Transactions en Espèces</div>
                    <div class="metric-value">{nb_transactions_espèces}</div>
                </div>
            """, unsafe_allow_html=True)

            col3.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💳 Transactions par Carte Bancaire (CB)</div>
                    <div class="metric-value">{nb_transactions_CB}</div>
                </div>
            """, unsafe_allow_html=True)

            col4, col5, col6 = st.columns(3)
            col4.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💳 Transactions par Virement</div>
                    <div class="metric-value">{nb_transactions_virement}</div>
                </div>
            """, unsafe_allow_html=True)

            col5.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📥 Transactions Entrantes</div>
                    <div class="metric-value">{nb_transactions_entrée}</div>
                </div>
            """, unsafe_allow_html=True)

            col6.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📤 Transactions Sortantes</div>
                    <div class="metric-value">{nb_transactions_sortie}</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des statistiques des transactions : {e}")
else:
    st.error("❌ Les données 'transaction' ne sont pas présentes dans le DataFrame.")









# ordonnances

if df is not None and "ordonnance" in df and "vente" in df:
    ordonnances = df["ordonnance"]
    ventes = df["vente"]  # Enregistrer la table 'vente'

    # Connexion à DuckDB pour effectuer des calculs
    con = duckdb.connect(database=":memory:")
    con.register("ordonnances_data", ordonnances)
    con.register("ventes_data", ventes)  # Enregistrer aussi la table 'vente'

    try:
        # Nombre total d'ordonnances délivrées
        nb_total_ordonnances_result = con.execute("""
            SELECT COUNT(DISTINCT ID_Ordonnance) FROM ordonnances_data
        """).fetchone()
        nb_total_ordonnances = nb_total_ordonnances_result[0] if nb_total_ordonnances_result else 0

        # Ordonnances non associées à une vente
        nb_ordonnances_sans_vente_result = con.execute("""
            SELECT COUNT(DISTINCT ID_Ordonnance) FROM ordonnances_data
            WHERE ID_Ordonnance NOT IN (SELECT DISTINCT ID_Ordonnance FROM ventes_data)
        """).fetchone()
        nb_ordonnances_sans_vente = nb_ordonnances_sans_vente_result[0] if nb_ordonnances_sans_vente_result else 0

        # Nombre moyen de médicaments par ordonnance
        nb_medicaments_par_ordonnance_result = con.execute("""
            SELECT AVG(count) FROM (
                SELECT COUNT(DISTINCT ID_Medicament) AS count
                FROM ordonnances_data
                GROUP BY ID_Ordonnance
            ) AS subquery
        """).fetchone()
        nb_medicaments_par_ordonnance = nb_medicaments_par_ordonnance_result[0] if nb_medicaments_par_ordonnance_result else 0

        # Ordonnance avec le plus de médicaments
        ordonnance_plus_medicaments_result = con.execute("""
            SELECT ID_Ordonnance, COUNT(DISTINCT ID_Medicament) AS medicaments_count
            FROM ordonnances_data
            GROUP BY ID_Ordonnance
            ORDER BY medicaments_count DESC
            LIMIT 1
        """).fetchone()
        ordonnance_plus_medicaments = ordonnance_plus_medicaments_result[0] if ordonnance_plus_medicaments_result else None
        nb_medicaments_ordre_plus = ordonnance_plus_medicaments_result[1] if ordonnance_plus_medicaments_result else 0

        # Médecin ayant prescrit le plus d'ordonnances
        medic_prescrit_le_plus_result = con.execute("""
            SELECT Nom_Medecin, COUNT(DISTINCT ID_Ordonnance) AS ordonnances_count
            FROM ordonnances_data
            GROUP BY Nom_Medecin
            ORDER BY ordonnances_count DESC
            LIMIT 1
        """).fetchone()
        medic_prescrit_le_plus = medic_prescrit_le_plus_result[0] if medic_prescrit_le_plus_result else None
        nb_ordonnances_medecin = medic_prescrit_le_plus_result[1] if medic_prescrit_le_plus_result else 0

        # Affichage des métriques
        st.markdown("<h2 style='color: green;'>Ordonnances</h2>", unsafe_allow_html=True)

        st.markdown(""" 
            <style>
                .metric-box {
                    border-left: 5px solid #4CAF50;
                    padding: 10px 15px;
                    margin-bottom: 15px;
                    border-radius: 6px;
                    box-shadow: 1px 1px 4px rgba(0,0,0,0.05);
                    background-color: rgb(38, 39, 48);
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

        with st.container():
            st.markdown("### 📑 Statistiques des Ordonnances")

            col1, col2, col3 = st.columns(3)
            col1.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📊 Nombre total d'ordonnances délivrées</div>
                    <div class="metric-value">{nb_total_ordonnances}</div>
                </div>
            """, unsafe_allow_html=True)

            col2.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">❌ Ordonnances non associées à une vente</div>
                    <div class="metric-value">{nb_ordonnances_sans_vente}</div>
                </div>
            """, unsafe_allow_html=True)

            col3.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💊 Nombre moyen de médicaments par ordonnance</div>
                    <div class="metric-value">{nb_medicaments_par_ordonnance:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

            col4, col5 = st.columns(2)
            col4.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📑 Ordonnance avec le plus de médicaments</div>
                    <div class="metric-value">Ordonnance {ordonnance_plus_medicaments} avec {nb_medicaments_ordre_plus} médicaments</div>
                </div>
            """, unsafe_allow_html=True)

            col5.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🩺 Médecin ayant prescrit le plus d'ordonnances</div>
                    <div class="metric-value">{medic_prescrit_le_plus} avec {nb_ordonnances_medecin} ordonnances</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des statistiques des ordonnances : {e}")
else:
    st.error("❌ Les données 'ordonnances' ou 'vente' ne sont pas présentes dans le DataFrame.")







# employes

if df is not None and "employe" in df and "vente" in df:
    employes = df["employe"]
    ventes = df["vente"]

    # Connexion à DuckDB
    con = duckdb.connect(database=":memory:")
    con.register("employes_data", employes)
    con.register("ventes_data", ventes)

    try:
        # Statistiques simples
        nb_total_employes = con.execute("SELECT COUNT(DISTINCT ID_Employe) FROM employes_data").fetchone()[0]
        nb_pharmaciens = con.execute("SELECT COUNT(DISTINCT ID_Employe) FROM employes_data WHERE LOWER(Role) = 'pharmacien'").fetchone()[0]
        nb_caissiers = con.execute("SELECT COUNT(DISTINCT ID_Employe) FROM employes_data WHERE LOWER(Role) = 'caissier'").fetchone()[0]
        nb_preparateurs = con.execute("SELECT COUNT(DISTINCT ID_Employe) FROM employes_data WHERE LOWER(Role) = 'préparateur en pharmacie'").fetchone()[0]
        salaire_moyen = con.execute("SELECT ROUND(AVG(Salaire), 2) FROM employes_data").fetchone()[0]

        # Employé avec le plus de ventes
        employe_plus_ventes_result = con.execute("""
            SELECT e.Nom, e.Prenom, COUNT(v.ID_Vente) AS ventes_count
            FROM employes_data e
            LEFT JOIN ventes_data v ON e.ID_Employe = v.ID_Employe
            GROUP BY e.ID_Employe, e.Nom, e.Prenom
            ORDER BY ventes_count DESC
            LIMIT 1
        """).fetchone()

        employe_plus_ventes = f"{employe_plus_ventes_result[0]} {employe_plus_ventes_result[1]}" if employe_plus_ventes_result else "Aucun"
        nb_ventes_employe = employe_plus_ventes_result[2] if employe_plus_ventes_result else 0

        # Style et affichage
        st.markdown("<h2 style='color: green;'>Employés</h2>", unsafe_allow_html=True)

        st.markdown("""
            <style>
                .metric-box {
                    border-left: 5px solid #4CAF50;
                    padding: 10px 15px;
                    margin-bottom: 15px;
                    border-radius: 6px;
                    box-shadow: 1px 1px 4px rgba(0,0,0,0.05);
                    background-color: rgb(38, 39, 48);
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

        with st.container():
            st.markdown("### 📑 Statistiques des Employés")
            col1, col2, col3 = st.columns(3)

            col1.markdown(f"""<div class="metric-box"><div class="metric-label">📊 Nombre total d'employés</div><div class="metric-value">{nb_total_employes}</div></div>""", unsafe_allow_html=True)
            col2.markdown(f"""<div class="metric-box"><div class="metric-label">💊 Nombre de pharmaciens</div><div class="metric-value">{nb_pharmaciens}</div></div>""", unsafe_allow_html=True)
            col3.markdown(f"""<div class="metric-box"><div class="metric-label">💼 Nombre de caissiers</div><div class="metric-value">{nb_caissiers}</div></div>""", unsafe_allow_html=True)

            col4, col5 = st.columns(2)
            col4.markdown(f"""<div class="metric-box"><div class="metric-label">🔬 Nombre de préparateurs en pharmacie</div><div class="metric-value">{nb_preparateurs}</div></div>""", unsafe_allow_html=True)
            col5.markdown(f"""<div class="metric-box"><div class="metric-label">💵 Salaire moyen des employés</div><div class="metric-value">{salaire_moyen:.2f} AR</div></div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown(f"""<div class="metric-box"><div class="metric-label">💼 Employé avec le plus de ventes enregistrées</div><div class="metric-value">{employe_plus_ventes} avec {nb_ventes_employe} ventes</div></div>""", unsafe_allow_html=True)

            st.markdown("---")
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des statistiques des employés : {e}")
else:
    st.error("❌ Les données 'employe' ou 'vente' ne sont pas présentes dans le DataFrame.")








# approvisionnement

if df is not None and "approvisionnement" in df and "medicament" in df:
    approv = df["approvisionnement"]
    medicament_df = df["medicament"]

    # Fusionner approvisionnement avec medicament uniquement
    approv = pd.merge(approv, medicament_df, on="ID_Medicament", how="left")

    con.register("approvisionnement_data", approv)

    try:
        # Convertir la date
        approv["Date_Commande"] = pd.to_datetime(approv["Date_Commande"], errors="coerce", dayfirst=False)

        # Mettre à jour l'enregistrement SQL
        con.unregister("approvisionnement_data")
        con.register("approvisionnement_data", approv)

        # Statistiques générales
        total_approv = con.execute("SELECT COUNT(*) FROM approvisionnement_data").fetchone()[0]
        total_quantite = con.execute("SELECT SUM(Quantite_Commande) FROM approvisionnement_data").fetchone()[0]

        # Mois avec le plus d'approvisionnements
        mois_plus_approv = con.execute("""
            SELECT strftime('%Y-%m', Date_Commande) AS mois, COUNT(*) AS nb_approv
            FROM approvisionnement_data
            GROUP BY mois
            ORDER BY nb_approv DESC
            LIMIT 1
        """).fetchone()
        mois_max = mois_plus_approv[0] if mois_plus_approv else "N/A"
        nb_max = mois_plus_approv[1] if mois_plus_approv else 0

        # Mois avec le moins d'approvisionnements
        mois_moins_approv = con.execute("""
            SELECT strftime('%Y-%m', Date_Commande) AS mois, COUNT(*) AS nb_approv
            FROM approvisionnement_data
            GROUP BY mois
            ORDER BY nb_approv ASC
            LIMIT 1
        """).fetchone()
        mois_min = mois_moins_approv[0] if mois_moins_approv else "N/A"
        nb_min = mois_moins_approv[1] if mois_moins_approv else 0

        # Top médicaments approvisionnés
        top_medicaments = con.execute("""
            SELECT Nom_Commercial, SUM(Quantite_Commande) AS total_qte
            FROM approvisionnement_data
            GROUP BY Nom_Commercial
            ORDER BY total_qte DESC
            LIMIT 5
        """).fetchdf()

        # Affichage des statistiques
        st.markdown("<h2 style='color: green;'> Approvisionnements</h2>", unsafe_allow_html=True)

        st.markdown("""
            <style>
                .metric-box {
                    border-left: 5px solid #00BFFF;
                    padding: 10px 15px;
                    margin-bottom: 15px;
                    border-radius: 6px;
                    box-shadow: 1px 1px 4px rgba(0,0,0,0.05);
                    background-color: rgb(38, 39, 48);
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

        col1, col2 = st.columns(2)
        col1.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">🔢 Nombre total d’approvisionnements</div>
                <div class="metric-value">{total_approv}</div>
            </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">📦 Quantité totale de médicaments approvisionnés</div>
                <div class="metric-value">{int(total_quantite)}</div>
            </div>
        """, unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        col3.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">📈 Mois avec le plus d’approvisionnements</div>
                <div class="metric-value">{mois_max} ({nb_max})</div>
            </div>
        """, unsafe_allow_html=True)

        col4.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">📉 Mois avec le moins d’approvisionnements</div>
                <div class="metric-value">{mois_min} ({nb_min})</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 💊 Top 5 Médicaments Approvisionnés")
        
        # Première ligne avec les 3 premiers médicaments
        col1, col2 = st.columns(2)
        for idx, row in top_medicaments.head(3).iterrows():
            col1.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💊 {row['Nom_Commercial']}</div>
                    <div class="metric-value">{int(row['total_qte'])} unités</div>
                </div>
            """, unsafe_allow_html=True)

        # Deuxième ligne avec les 2 derniers médicaments
        for idx, row in top_medicaments.tail(2).iterrows():
            col2.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💊 {row['Nom_Commercial']}</div>
                    <div class="metric-value">{int(row['total_qte'])} unités</div>
                </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des statistiques des approvisionnements : {e}")
else:
    st.warning("Les données d’approvisionnement ou de médicaments ne sont pas disponibles.")




