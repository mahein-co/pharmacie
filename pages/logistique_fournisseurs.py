import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from utils import load_data
from db import init_duckdb
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

from pipelines import pipelines_fournisseurs
from data.mongodb_client import MongoDBClient

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




# fourniseurs
overview_collection = MongoDBClient(collection_name="overview")


#requete 
taux_retard = overview_collection.make_specific_pipeline(pipeline=pipelines_fournisseurs.pipeline_taux_retard,title="recuperation taux retard")
print("taux retard: ",taux_retard)

retard_moyen = overview_collection.make_specific_pipeline(pipeline=pipelines_fournisseurs.pipeline_retard_moyen,title="recuperation retard moyen")
print("retard_moyen: ",retard_moyen)

nb_commandes = overview_collection.make_specific_pipeline(pipeline=pipelines_fournisseurs.pipeline_nombre_commandes,title="recuperation nombre commandes")
print("nb_commandes: ",nb_commandes)


st.markdown("<h2 style='color: green;'>Logistique & Fournisseurs</h2>", unsafe_allow_html=True)

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














# Taux de retard= (Nb total de livraisons/Nb livraisons en retard) ×100    et Fournisseur le plus fiable



if df is not None and "stock" in df and "fournisseur" in df:
    stock = df["stock"]
    fournisseur = df["fournisseur"]

    # Convertir les dates au bon format
    stock["Date_Commande"] = pd.to_datetime(stock["Date_Commande"], errors="coerce")
    stock["Date_Reception"] = pd.to_datetime(stock["Date_Reception"], errors="coerce")

    # Ajouter une colonne booléenne : livraison en retard (> 3 jours)
    stock["Livraison_Retard"] = (stock["Date_Reception"] - stock["Date_Commande"]).dt.days > 3

    # Nom complet du fournisseur
    fournisseur["Nom_Fournisseur"] = fournisseur["Nom"] + " " + fournisseur["Prenom"]

    # Fusion
    merged_df = pd.merge(stock, fournisseur[["ID_Fournisseur", "Nom_Fournisseur"]], on="ID_Fournisseur", how="left")

    # Connexion à DuckDB
    con = duckdb.connect(database=":memory:")
    con.register("logistique", merged_df)

    # Couleur personnalisée pour le gradient
    custom_plasma = ["#0d0887", "#5c01a6", "#9c179e", "#6a41b4", "#4f76c4", "#3a93c6"]

    try:
        # 1. Taux de retard de tous les fournisseurs
        query_retards = """
            SELECT 
                Nom_Fournisseur,
                COUNT(*) AS Total_Livraisons,
                SUM(CASE WHEN Livraison_Retard THEN 1 ELSE 0 END) AS Livraisons_Retard,
                ROUND(100.0 * SUM(CASE WHEN Livraison_Retard THEN 1 ELSE 0 END) / COUNT(*), 2) AS Taux_Retard
            FROM logistique
            GROUP BY Nom_Fournisseur
            HAVING Total_Livraisons > 0
            ORDER BY Taux_Retard DESC
        """
        retard_df = con.execute(query_retards).fetchdf()

        if not retard_df.empty:
            # --- 1. GRAPHE : Tous les fournisseurs ---
            fig_all = px.bar(
                retard_df,
                x="Taux_Retard",
                y="Nom_Fournisseur",
                orientation="h",
                text="Taux_Retard",
                color="Taux_Retard",
                color_continuous_scale=custom_plasma,
                labels={"Taux_Retard": "% Retards", "Nom_Fournisseur": "Fournisseur"},
                title="Taux de livraison en retard des fournisseurs"
            )
            fig_all.update_layout(yaxis=dict(categoryorder="total ascending"))

            # --- 2. Fournisseur le plus fiable + GRAPHE Top 3 ---
            query_top3 = """
                SELECT 
                    Nom_Fournisseur,
                    COUNT(*) AS Total_Livraisons,
                    SUM(CASE WHEN Livraison_Retard THEN 1 ELSE 0 END) AS Retards,
                    ROUND(100.0 * SUM(CASE WHEN Livraison_Retard THEN 1 ELSE 0 END) / COUNT(*), 2) AS Taux_Retard
                FROM logistique
                GROUP BY Nom_Fournisseur
                HAVING Total_Livraisons >= 0
                ORDER BY Taux_Retard ASC
                LIMIT 3
            """
            top_fournisseurs = con.execute(query_top3).fetchdf()

            if not top_fournisseurs.empty:
                best = top_fournisseurs.iloc[0]
                st.markdown("### ✅ Fournisseur le plus fiable")
                st.success(f"📦 **{best['Nom_Fournisseur']}** avec un taux de retard de **{best['Taux_Retard']}%** sur {best['Total_Livraisons']} livraisons.")

                fig_top3 = px.pie(
                    top_fournisseurs,
                    names="Nom_Fournisseur",
                    values="Taux_Retard",
                    title="Top 3 des fournisseurs les plus fiables (Taux de retard les plus bas)",
                    labels={"Nom_Fournisseur": "Fournisseur", "Taux_Retard": "Taux de retard (%)"},
                    color="Nom_Fournisseur",
                    color_discrete_sequence=["#2ca02c", "#1f77b4", "#ff7f0e"]
                )
                fig_top3.update_traces(textinfo="percent+label", pull=[0.1, 0, 0])  # Pousse un peu le premier segment pour la visibilité
                fig_top3.update_layout(showlegend=True)


                # ✅ Afficher les deux graphiques côte à côte
                col1, col2 = st.columns(2)

                with col1:
                    st.plotly_chart(fig_all, use_container_width=True)

                with col2:
                    st.plotly_chart(fig_top3, use_container_width=True)
            else:
                st.info("Aucun fournisseur avec des livraisons enregistrées.")

        else:
            st.info("Aucune donnée de livraison trouvée.")
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul : {e}")
else:
    st.error("❌ Les données 'stock' et 'fournisseur' ne sont pas disponibles.")






# Fournisseur avec le plus de problèmes

if df is not None and "stock" in df and "fournisseur" in df:
    stock = df["stock"]
    fournisseur = df["fournisseur"]

    # Conversion des dates
    stock["Date_Commande"] = pd.to_datetime(stock["Date_Commande"], errors="coerce")
    stock["Date_Reception"] = pd.to_datetime(stock["Date_Reception"], errors="coerce")

    # Colonne de retard
    stock["Livraison_Retard"] = (stock["Date_Reception"] - stock["Date_Commande"]).dt.days > 3

    # Nom complet
    fournisseur["Nom_Fournisseur"] = fournisseur["Nom"] + " " + fournisseur["Prenom"]

    # Fusion
    merged_df = pd.merge(stock, fournisseur[["ID_Fournisseur", "Nom_Fournisseur"]], on="ID_Fournisseur", how="left")

    # Connexion DuckDB
    con = duckdb.connect(database=":memory:")
    con.register("logistique", merged_df)

    try:
        # Fournisseur le plus fiable (le moins de retards)
        query = """
            SELECT 
                Nom_Fournisseur,
                COUNT(*) AS Total_Livraisons,
                SUM(CASE WHEN Livraison_Retard THEN 1 ELSE 0 END) AS Retards,
                ROUND(100.0 * SUM(CASE WHEN Livraison_Retard THEN 1 ELSE 0 END) / COUNT(*), 2) AS Taux_Retard
            FROM logistique
            GROUP BY Nom_Fournisseur
            HAVING Retards > 0
            ORDER BY Taux_Retard ASC
            LIMIT 3
        """
        top_fournisseurs_problemes = con.execute(query).fetchdf()

        if not top_fournisseurs_problemes.empty:
           
            top_fournisseurs_problemes["Text"] = top_fournisseurs_problemes.apply(
                lambda row: f"{row['Retards']} retards sur {row['Total_Livraisons']} livraisons", axis=1)

            # Graphique pour visualiser les top 3 fournisseurs
            fig1 = px.pie(
                top_fournisseurs_problemes,
                names="Nom_Fournisseur",  
                values="Retards", 
                hover_data=["Text"],  
                color="Retards",  
                color_discrete_sequence=px.colors.sequential.Reds,  
                labels={"Retards": "Retards", "Nom_Fournisseur": "Fournisseur"},
                title="Top 3 des fournisseurs avec le plus de retards de livraison"
            )

            fig1.update_traces(textinfo='percent+label+value', hovertemplate='%{label}: %{value} retards')


            # fig1.update_traces(textposition='inside', texttemplate='%{text}')
            # fig1.update_layout(yaxis=dict(categoryorder="total descending"))

            # Utilisation de `st.columns` pour afficher les graphiques côte à côte
            col1, col2 = st.columns(2)

            with col1:
                # Afficher le graphique du fournisseur le plus fiable
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                # Fournisseur avec le plus de problèmes
                st.markdown("### ❗ Fournisseur avec le plus de retards de livraison")
                for index, row in top_fournisseurs_problemes.iterrows():
                    st.error(f"🚚 **{row['Nom_Fournisseur']}** avec **{row['Retards']} retards** sur **{row['Total_Livraisons']}** livraisons.")
                # Vous pouvez ajouter d'autres graphiques ou informations selon les besoins
        else:
            st.info("Aucun fournisseur avec des retards de livraison.")
    except Exception as e:
        st.error(f"❌ Erreur lors de l’analyse : {e}")
else:
    st.error("❌ Les données 'stock' et 'fournisseur' sont manquantes.")









if df is not None and "stock" in df and "fournisseur" in df:
    stock = df["stock"]
    fournisseur = df["fournisseur"]

    # Conversion des dates
    stock["Date_Commande"] = pd.to_datetime(stock["Date_Commande"], errors="coerce")
    stock["Date_Reception"] = pd.to_datetime(stock["Date_Reception"], errors="coerce")

    # Calcul du délai de livraison en jours
    stock["Delai_Livraison"] = (stock["Date_Reception"] - stock["Date_Commande"]).dt.days

    # Création du nom complet
    fournisseur["Nom_Fournisseur"] = fournisseur["Nom"] + " " + fournisseur["Prenom"]

    # Fusion
    merged_df = pd.merge(stock, fournisseur[["ID_Fournisseur", "Nom_Fournisseur"]], on="ID_Fournisseur", how="left")

    try:
        # Calcul du temps moyen de livraison par fournisseur
        delai_df = (
            merged_df.groupby("Nom_Fournisseur")["Delai_Livraison"]
            .mean()
            .reset_index()
            .rename(columns={"Delai_Livraison": "Delai_Moyen"})
            .sort_values("Delai_Moyen")
        )

        if not delai_df.empty:
            st.markdown("### ⏱️ Temps moyen de livraison par fournisseur (en jours)")

            fig = px.bar(
                delai_df,
                x="Delai_Moyen",
                y="Nom_Fournisseur",
                orientation="h",
                text=delai_df["Delai_Moyen"].round(1).astype(str) + " jours",
                labels={"Delai_Moyen": "Temps moyen (jours)", "Nom_Fournisseur": "Fournisseur"},
                color="Delai_Moyen",
                color_continuous_scale="Blues"
            )
            fig.update_traces(textposition="inside")
            fig.update_layout(yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée de livraison disponible pour le calcul.")
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul du délai moyen : {e}")
