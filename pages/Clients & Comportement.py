from datetime import timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from utils import load_data
from db import init_duckdb
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
import json

# Initialisation
st.set_page_config(page_title="Dashboard Pharmacie", layout="wide")
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">', unsafe_allow_html=True)

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




# client 


from datetime import datetime, timedelta


st.markdown("<h2 style='color: green;'> Clients & Comportement</h2>", unsafe_allow_html=True)

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


    
    
    

# Nombre moyen de médicaments achetés par client  

if df is not None and "vente" in df and "detailVente" in df and "client" in df:
    # Récupération des DataFrames
    vente = df["vente"]
    detail_vente = df["detailVente"]
    client = df["client"]

    # Fusion des ventes avec les détails et les clients
    merged_vente = pd.merge(vente, detail_vente, on="ID_Vente", how="inner")
    merged_vente = pd.merge(merged_vente, client, on="ID_Client", how="left")

    # Connexion à DuckDB en mémoire
    con = duckdb.connect(database=":memory:")
    con.register("vente_client", merged_vente)

    st.markdown("### 👥 Nombre moyen de médicaments achetés par client")

    custom_colors = [
        "#0d0887", "#5c01a6", "#9c179e",
        "#6a41b4", "#4f76c4", "#3a93c6",
        "#22b2aa", "#70cf57", "#fbd524", "#f8961e"
    ]

    try:
        # 🧮 Moyenne globale
        query_avg = """
            SELECT 
                ROUND(SUM(Quantité) * 1.0 / COUNT(DISTINCT ID_Client), 2) AS Moyenne_Medicaments_Par_Client
            FROM vente_client
        """
        moyenne = con.execute(query_avg).fetchone()[0]
        moyenne = moyenne if moyenne is not None else 0
        st.success(f"💊 **Moyenne : {moyenne} médicaments par client**")

        # 📊 Top 10 clients par total acheté
        query_top_clients = """
            SELECT 
                CONCAT(Nom, ' ', Prenom) AS Nom_Client,
                SUM(Quantité) AS Total_Achete
            FROM vente_client
            GROUP BY Nom_Client
            ORDER BY Total_Achete DESC
            LIMIT 10
        """
        top_clients_df = con.execute(query_top_clients).fetchdf()

        st.markdown("---")
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul ou de l'affichage du graphique : {e}")

else:
    st.error("❌ Les données 'vente', 'detailVente' et 'client' ne sont pas présentes dans le DataFrame.")






#Nombre moyen de médicaments achetés par client et Clients achetant en grande quantité (>10 unités)


if df is not None and "vente" in df and "detailVente" in df and "client" in df:
    # Chargement des DataFrames
    vente = df["vente"]
    detail_vente = df["detailVente"]
    client = df["client"]

    # Fusion des tables
    merged_vente = pd.merge(vente, detail_vente, on="ID_Vente", how="inner")
    merged_vente = pd.merge(merged_vente, client, on="ID_Client", how="left")

    # Connexion à DuckDB
    con = duckdb.connect(database=":memory:")
    con.register("vente_client", merged_vente)

    st.markdown("### 🧍‍♂️ Clients achetant en grande quantité (>10 unités)")

    # Palette plasma personnalisée (sans jaune)
    plasma_custom = [
        "#0d0887", "#2e0594", "#4c02a1", "#6a00a8",
        "#8f0da4", "#a9349a", "#c5548c", "#d9777e",
        "#e79374", "#f2af6d"
    ]

    try:
        # Requête SQL pour clients >10 unités
        query_clients_grands = """
            SELECT 
                CONCAT(Nom, ' ', Prenom) AS Nom_Client,
                SUM(Quantité) AS Total_Quantite
            FROM vente_client
            GROUP BY Nom_Client
            HAVING SUM(Quantité) > 10
            ORDER BY Total_Quantite DESC
            limit 10
        """
        grands_acheteurs_df = con.execute(query_clients_grands).fetchdf()
        

        if not grands_acheteurs_df.empty:
            
            
            
            # Convertir les données en dictionnaire
            grands_acheteurs = grands_acheteurs_df.to_dict(orient="records")

            # Chemin du fichier JSON
            json_path = "json/grands_acheteurs.json"

            # Enregistrer / écraser le fichier JSON
            with open(json_path, "w", encoding='utf-8') as f:
                json.dump(grands_acheteurs, f, ensure_ascii=False, indent=4)


            # Calcul du total global pour le pourcentage
            total_global = grands_acheteurs_df["Total_Quantite"].sum()

            # Calcul du pourcentage pour chaque client
            grands_acheteurs_df["Pourcentage"] = (grands_acheteurs_df["Total_Quantite"] / total_global) * 100
            grands_acheteurs_df["Pourcentage"] = grands_acheteurs_df["Pourcentage"].round(2)

            # Ne garder que les colonnes utiles
            top_clients_pourcent = grands_acheteurs_df[["Nom_Client", "Pourcentage"]]

            # Convertir en dictionnaire
            grands_acheteurs = top_clients_pourcent.to_dict(orient="records")

            # Chemin du fichier JSON
            json_path = "json/grands_acheteurs_Top10.json"

            # Enregistrer / écraser le fichier JSON
            with open(json_path, "w", encoding='utf-8') as f:
                json.dump(grands_acheteurs, f, ensure_ascii=False, indent=4)
            
            
            

            # Limiter à 10 premiers clients
            top10_df = grands_acheteurs_df.head(10)

            # Layout en deux colonnes
            col1, col2 = st.columns(2)

            # Bar chart horizontal
            with col1:
                fig_bar = px.bar(
                    grands_acheteurs_df,
                    x="Total_Quantite",
                    y="Nom_Client",
                    orientation="h",
                    title="📊 Quantité achetée par client",
                    text="Total_Quantite",
                    color="Nom_Client",
                    color_discrete_sequence=plasma_custom
                )
                fig_bar.update_layout(
                    yaxis=dict(categoryorder="total ascending"),
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # Camembert limité à 10
            with col2:
                fig_pie = px.pie(
                    top10_df,
                    values="Total_Quantite",
                    names="Nom_Client",
                    title="🥧 Top 10 des clients par quantité achetée",
                    color_discrete_sequence=plasma_custom
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)

        else:
            st.info("Aucun client n'a acheté plus de 10 unités.")
            st.markdown("---")
    except Exception as e:
        st.error(f"❌ Erreur lors de la génération des graphiques : {e}")

else:
    st.error("❌ Les données 'vente', 'detailVente' et 'client' ne sont pas présentes dans le DataFrame.")









#Clients réguliers (>5 achats en 6 mois)

from datetime import datetime, timedelta

if df is not None and "vente" in df and "client" in df:
    vente = df["vente"]
    client = df["client"]

    # 🔁 Fusion des tables "vente" et "client" sur ID_Client
    merged_df = pd.merge(vente, client, on="ID_Client", how="left")

    # 🧼 Nettoyage de la colonne Date_Vente (au cas où il y a des textes parasites comme "modifié")
    merged_df['Date_Vente_x'] = merged_df['Date_Vente_x'].astype(str).str.extract(r'(\d{1,2}/\d{1,2}/\d{4})')
    merged_df['Date_Vente_x'] = pd.to_datetime(merged_df['Date_Vente_x'], format="%m/%d/%Y", errors='coerce')

    # 🕒 Calcul de la date limite : 6 mois en arrière
    date_limite = datetime.now() - timedelta(days=180)

    # 📉 Filtrage des ventes récentes
    recent_sales_df = merged_df[merged_df['Date_Vente_x'] > date_limite]

    # 📦 Connexion DuckDB en mémoire + enregistrement du DataFrame
    con = duckdb.connect(database=':memory:')
    con.register('pharmacie', merged_df)

    st.markdown("### 📊 Clients réguliers (>5 achats dans les 6 derniers mois)")

    try:
        # 💾 Requête SQL pour identifier les clients avec plus de 5 achats récents
        query = """
            SELECT 
                v.ID_Client, 
                v.Nom, 
                v.Prenom, 
                COUNT(v.ID_Vente) AS Nombre_Achats
            FROM pharmacie v
            WHERE Date_Vente_x > CURRENT_DATE - INTERVAL 6 MONTH
            GROUP BY v.ID_Client, v.Nom, v.Prenom
            HAVING COUNT(v.ID_Vente) > 5
            ORDER BY Nombre_Achats DESC
     """


        clients_reguliers_df = con.execute(query).fetchdf()

        if not clients_reguliers_df.empty:
            # 📊 Génération du graphique Plotly
            fig = px.bar(
                clients_reguliers_df,
                x="Nombre_Achats",
                y="Nom",
                orientation="h",
                title="📊 Clients réguliers (>5 achats dans les 6 derniers mois)",
                labels={"Nombre_Achats": "Nombre d'achats", "Nom": "Client"},
                text="Nombre_Achats",
                color="Nom",
                color_discrete_sequence=px.colors.sequential.Plasma_r
            )
            fig.update_layout(
                yaxis=dict(categoryorder="total ascending"),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun client n'a effectué plus de 5 achats dans les 6 derniers mois.")

    except Exception as e:
        st.error(f"❌ Erreur lors de la génération du graphique : {e}")

else:
    st.error("❌ Les données 'vente' et 'client' ne sont pas présentes dans le DataFrame.")





# Répartition des paiements
with st.expander("💳 Répartition des paiements"):
    if df is not None and "vente" in df:
        vente = df["vente"]

        # Connexion DuckDB en mémoire
        con = duckdb.connect(database=":memory:")
        con.register("vente", vente)

        st.markdown("### 💳 Répartition des paiements")

        try:
            # Requête : somme totale payée par mode de paiement
            query = """
                SELECT Mode_Paiement, SUM(Total_Payer) AS Montant_Total
                FROM vente
                GROUP BY Mode_Paiement
                ORDER BY Montant_Total DESC
            """
            paiement_df = con.execute(query).fetchdf()

            if not paiement_df.empty:
                
                
               # Calcul des pourcentages
                paiement_df["Pourcentage"] = (paiement_df["Montant_Total"] / paiement_df["Montant_Total"].sum()) * 100

                # Arrondir les pourcentages à 2 chiffres après la virgule (optionnel)
                paiement_df["Pourcentage"] = paiement_df["Pourcentage"].round(2)

                # Conserver uniquement Mode_Paiement et Pourcentage pour le JSON
                pourcentages_df = paiement_df[["Mode_Paiement", "Pourcentage"]]

                # Sauvegarde en JSON (chemin à adapter selon ton projet)
                chemin_fichier = "json/repartition_paiements.json"
                with open(chemin_fichier, "w", encoding="utf-8") as f:
                    json.dump(pourcentages_df.to_dict(orient="records"), f, ensure_ascii=False, indent=4)

                    
                    
                    
                    
                fig = px.pie(
                    paiement_df,
                    values="Montant_Total",
                    names="Mode_Paiement",
                    title="Répartition des paiements par mode",
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée de paiement trouvée.")
        
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération du graphique : {e}")
                   

    else:
        st.error("❌ La table 'vente' est absente du DataFrame.")
