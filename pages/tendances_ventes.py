import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from utils import load_data
from db import init_duckdb
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

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





# ventes

st.markdown("<h2 style='color: green;'>Tendances des ventes</h2>", unsafe_allow_html=True)

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


# Connexion à MongoDB pour récupérer les données des clients
ventes_collection = MongoDBClient(collection_name="vente")

if ventes_collection:
    # Recuperer toutes les ventes
    ventes = ventes_collection.find_all_documents()

    # Nombre totale de ventes
    nb_total_ventes = ventes_collection.count_distinct_agg("id_vente")

    # con = duckdb.connect(database=":memory:")
    # con.register("ventes", ventes)
    # con.register("detailVente", detail_ventes)

    try:
        # Statistiques des ventes
        # nb_total_ventes = con.execute("SELECT COUNT(ID_Vente) FROM ventes").fetchone()[0]

        # ca_total = con.execute("SELECT SUM(Total_Payer) FROM ventes").fetchone()[0]

        # ca_moyen = con.execute("SELECT AVG(Total_Payer) FROM ventes").fetchone()[0]

        # vente_max = con.execute("SELECT MAX(Total_Payer) FROM ventes").fetchone()[0]

        # vente_min = con.execute("SELECT MIN(Total_Payer) FROM ventes").fetchone()[0]

        # nb_ventes_annulees = con.execute("SELECT COUNT(ID_Vente) FROM ventes WHERE Mode_Paiement = 'Annulé'").fetchone()[0]

        # nb_ventes_en_attente = con.execute("SELECT COUNT(ID_Vente) FROM ventes WHERE Mode_Paiement = 'En attente'").fetchone()[0]

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

        #     col2.markdown(f"""
        #         <div class="metric-box">
        #             <div class="metric-label">💰 Chiffre d'affaires total</div>
        #             <div class="metric-value">{ca_total:.2f} €</div>
        #         </div>
        #     """, unsafe_allow_html=True)

        #     col3.markdown(f"""
        #         <div class="metric-box">
        #             <div class="metric-label">💸 Montant moyen par vente</div>
        #             <div class="metric-value">{ca_moyen:.2f} €</div>
        #         </div>
        #     """, unsafe_allow_html=True)

        #     col4, col5 = st.columns([2, 1])
        #     col4.markdown(f"""
        #         <div class="metric-box">
        #             <div class="metric-label">💵 Vente la plus élevée</div>
        #             <div class="metric-value">{vente_max:.2f} €</div>
        #         </div>
        #     """, unsafe_allow_html=True)

        #     col5.markdown(f"""
        #         <div class="metric-box">
        #             <div class="metric-label">💲 Vente la plus basse</div>
        #             <div class="metric-value">{vente_min:.2f} €</div>
        #         </div>
        #     """, unsafe_allow_html=True)

        # st.markdown("---")

        # with st.container():
        #     st.markdown("### 🛑 Statistiques des ventes en attente ou annulées")
        #     col6, col7 = st.columns(2)
        #     col6.markdown(f"""
        #         <div class="metric-box">
        #             <div class="metric-label">❌ Nombre de ventes annulées</div>
        #             <div class="metric-value">{nb_ventes_annulees}</div>
        #         </div>
        #     """, unsafe_allow_html=True)

        #     col7.markdown(f"""
        #         <div class="metric-box">
        #             <div class="metric-label">⏳ Nombre de ventes en attente de paiement</div>
        #             <div class="metric-value">{nb_ventes_en_attente}</div>
        #         </div>
        #     """, unsafe_allow_html=True)

        st.markdown("---")

     

    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des statistiques des ventes : {e}")
else:
    st.error("❌ Les données 'ventes' et 'detailVente' ne sont pas présentes dans le DataFrame.")










# Médicaments les plus vendus (Top 3)


custom_plasma = [
    "#0d0887", "#5c01a6", "#9c179e", "#6a41b4", "#4f76c4", "#3a93c6"
]

if df is not None and all(key in df for key in ["medicament", "vente", "stock"]):
    medicament = df["medicament"]
    vente = df["vente"]
    stock = df["stock"]

    # Extraction de l'année depuis Date_Vente
    vente["Date_Vente"] = pd.to_datetime(vente["Date_Vente"], errors='coerce')
    vente["Annee_Vente"] = vente["Date_Vente"].dt.year

    # Liste unique des années disponibles
    annees_disponibles = sorted(vente["Annee_Vente"].dropna().unique())

    st.sidebar.markdown("### 📅 Filtrer par année")

    # Option simple : une seule année
    annee_unique = st.sidebar.selectbox("Sélectionner une année", options=annees_disponibles)

    # Option avancée : plage d'années
    st.sidebar.markdown("### 📆 Filtrer entre deux années")
    annee_min, annee_max = st.sidebar.select_slider(
        "Sélectionner une plage d'années",
        options=annees_disponibles,
        value=(min(annees_disponibles), max(annees_disponibles))
    )

    # Filtrage par plage d’années
    vente_filtre = vente[
        (vente["Annee_Vente"] >= annee_min) & (vente["Annee_Vente"] <= annee_max)
    ]

    # Fusion des données
    vente_avec_nom = pd.merge(vente_filtre, medicament[["ID_Medicament", "Nom_Commercial"]], on="ID_Medicament", how="left")
    vente_stock = pd.merge(vente_avec_nom, stock[["ID_Medicament", "quantite_disponible"]], on="ID_Medicament", how="left")

    # Analyse avec DuckDB
    con = duckdb.connect(database=':memory:')
    con.register("vente_stock", vente_stock)

    try:
        query = """
            SELECT 
                Nom_Commercial,
                SUM(Quantite) AS Total_Vendu,
                MAX(quantite_disponible) AS Stock_Disponible
            FROM vente_stock
            GROUP BY Nom_Commercial
            ORDER BY Total_Vendu DESC
            LIMIT 3
        """
        top_ventes_stock = con.execute(query).fetchdf()

        total_ventes = top_ventes_stock["Total_Vendu"].sum()
        top_ventes_stock["Pourcentage"] = round(100 * top_ventes_stock["Total_Vendu"] / total_ventes, 2)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### 🥇 Médicaments les plus vendus ({annee_min} - {annee_max})")
            fig_pie = px.pie(
                top_ventes_stock,
                names="Nom_Commercial",
                values="Pourcentage",
                hole=0.4,
                title=f"🥇 Médicaments les Plus Vendus ({annee_min} - {annee_max})",
                color_discrete_sequence=custom_plasma
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.markdown(f"### 💊 Médicaments avec Stock ({annee_min} - {annee_max})")
            fig_bar = px.bar(
                top_ventes_stock,
                y="Nom_Commercial",
                x="Total_Vendu",
                color="Nom_Commercial",
                text="Pourcentage",
                title=f"💊 Top 3 Médicaments avec Stock ({annee_min} - {annee_max})",
                labels={"Total_Vendu": "Vendus", "Stock_Disponible": "Stock Disponible"},
                color_discrete_sequence=custom_plasma,
                orientation='h'
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        for _, row in top_ventes_stock.iterrows():
            st.write(f"🔹 **{row['Nom_Commercial']}** : {row['Pourcentage']}% des ventes – Stock : {row['Stock_Disponible']}")

    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse des ventes et du stock : {e}")

else:
    st.error("❌ Données manquantes : 'medicament', 'vente' ou 'stock'")






## Analyse des Ventes par Saison


if df is not None and "vente" in df and "medicament" in df:
    st.markdown("## 🕒 Analyse des Ventes par Saison et Catégorie")

    # Sélection de l'année pour filtrage dans la barre latérale
    annee_selectionnee = st.sidebar.selectbox("Sélectionnez l'année par Saison et Catégorie", options=df["vente"]["Date_Vente"].dt.year.unique())

    medicament = df["medicament"]
    vente = df["vente"]

    try:
        # Conversion des dates et ajout des colonnes pour le mois et la saison
        vente["Date_Vente"] = pd.to_datetime(vente["Date_Vente"], errors='coerce')
        vente["Mois"] = vente["Date_Vente"].dt.month
        vente["Année"] = vente["Date_Vente"].dt.year

        # Fonction pour identifier la saison
        def get_saison(mois):
            if mois in [12, 1, 2]:
                return "Hiver"
            elif mois in [3, 4, 5]:
                return "Printemps"
            elif mois in [6, 7, 8]:
                return "Été"
            elif mois in [9, 10, 11]:
                return "Automne"
            return "Inconnu"

        vente["Saison"] = vente["Mois"].apply(get_saison)

        # Filtrer les données par l'année sélectionnée dans la sidebar
        vente = vente[vente["Année"] == annee_selectionnee]

        # Joindre les données de vente avec les informations sur les médicaments (Nom_Commercial et Catégorie)
        vente_saison_categorie = pd.merge(vente, medicament[["ID_Medicament", "Nom_Commercial", "Categorie"]], on="ID_Medicament", how="left")

        # Groupement par saison et catégorie
        vente_par_saison_categorie = vente_saison_categorie.groupby(["Saison", "Categorie"])["Quantite"].sum().reset_index()

        # Création des colonnes pour afficher les graphiques côte à côte
        col1, col2 = st.columns(2)

        # Graphique en sunburst dans la première colonne
        with col1:
            fig_saison_categorie = px.sunburst(
                vente_par_saison_categorie,
                path=["Saison", "Categorie"],
                values="Quantite",
                title=f"📊 Quantité Vendue par Saison et Catégorie pour l'année {annee_selectionnee}",
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            st.plotly_chart(fig_saison_categorie, use_container_width=True)

        # Graphique en barres dans la deuxième colonne
        with col2:
            fig_bar = px.bar(
                vente_par_saison_categorie,
                x="Saison",
                y="Quantite",
                color="Categorie",
                title=f"📊 Quantité Vendue par Saison et Catégorie pour l'année {annee_selectionnee}",
                labels={"Quantite": "Quantité Vendue", "Saison": "Saison"},
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Affichage de la période avec le plus de ventes
        saison_max_categorie = vente_par_saison_categorie.loc[vente_par_saison_categorie["Quantite"].idxmax()]
        st.success(f"🌟 **Période avec le plus de ventes** : **{saison_max_categorie['Saison']}** - **{saison_max_categorie['Categorie']}** avec **{saison_max_categorie['Quantite']}** médicaments vendus.")

    except Exception as e:
        st.error(f"❌ Erreur dans l’analyse des saisons et catégories : {e}")
else:
    st.warning("⚠️ Les données nécessaires pour l'analyse des saisons et catégories ne sont pas disponibles.")









# Jour de la semaine avec le plus de ventes
with st.expander("Jour de la semaine avec le plus de ventes"):
    if df is not None and "vente" in df and "medicament" in df:
        medicament = df["medicament"]
        vente = df["vente"]
        
        # Conversion de la colonne Date_Vente en datetime et extraction du jour de la semaine
        vente["Date_Vente"] = pd.to_datetime(vente["Date_Vente"], errors='coerce')
        vente["Jour_Semaine"] = vente["Date_Vente"].dt.dayofweek  # 0=Dimanche, 1=Lundi, ..., 6=Samedi

        # Groupement des ventes par jour de la semaine
        vente_par_jour = vente.groupby("Jour_Semaine")["Quantite"].sum().reset_index()

        # Renommer les jours de la semaine pour une lecture plus facile
        vente_par_jour["Jour_Semaine_Label"] = vente_par_jour["Jour_Semaine"].map({
            0: "Dimanche", 1: "Lundi", 2: "Mardi", 3: "Mercredi", 4: "Jeudi", 5: "Vendredi", 6: "Samedi"
        })

        # Trouver le jour de la semaine avec le plus de ventes
        jour_max_ventes = vente_par_jour.loc[vente_par_jour["Quantite"].idxmax()]

        # Connexion à DuckDB pour effectuer des analyses SQL
        con = duckdb.connect(database=':memory:')
        con.register("vente", vente)

        try:
            # Requête SQL pour obtenir le jour de la semaine avec le plus de ventes
            query = """
                SELECT 
                    Jour_Semaine,
                    SUM(Quantite) AS Total_Ventes
                FROM vente
                GROUP BY Jour_Semaine
                ORDER BY Total_Ventes DESC
                LIMIT 1
            """
            jour_max_ventes_sql = con.execute(query).fetchdf()

            # Renommer les jours de la semaine pour une lecture plus facile
            jour_max_ventes_sql["Jour_Semaine_Label"] = jour_max_ventes_sql["Jour_Semaine"].map({
                0: "Dimanche", 1: "Lundi", 2: "Mardi", 3: "Mercredi", 4: "Jeudi", 5: "Vendredi", 6: "Samedi"
            })

            # Affichage du jour avec le plus de ventes
            st.markdown(f"### Jour de la semaine avec le plus de ventes")
            st.write(f"🔹 **Jour : {jour_max_ventes_sql['Jour_Semaine_Label'][0]}**")
            st.write(f"🔹 **Total des ventes : {jour_max_ventes_sql['Total_Ventes'][0]} ventes**")

            # Nouveau graphique : Évolution des ventes par jour de la semaine sous forme de courbe
            fig_line = px.line(
                vente_par_jour,
                x="Jour_Semaine_Label",
                y="Quantite",
                title="Évolution des Ventes par Jour de la Semaine",
                labels={"Quantite": "Quantité Vendue", "Jour_Semaine_Label": "Jour de la Semaine"},
                markers=True
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # Optionnel : Graphique des ventes par médicament
            vente_par_medicament = vente.groupby("ID_Medicament")["Quantite"].sum().reset_index()
            vente_par_medicament = pd.merge(vente_par_medicament, medicament[["ID_Medicament", "Nom_Commercial"]], on="ID_Medicament", how="left")

            fig_medicament = px.bar(
                vente_par_medicament,
                x="Nom_Commercial",
                y="Quantite",
                title="Ventes par Médicament",
                labels={"Quantite": "Quantité Vendue", "Nom_Commercial": "Médicament"},
                color="Nom_Commercial",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_medicament, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Erreur lors de l'analyse des ventes : {e}")

    else:
        st.error("❌ Données manquantes : 'medicament' ou 'vente'")
