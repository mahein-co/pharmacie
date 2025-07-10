import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
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

# Chargement des données
df = load_data()

# Sidebar
with st.sidebar:
    if st.button("Recharger les données", key="reload", help="Cliquez pour recharger les données", use_container_width=True):
        st.cache_data.clear()
    st.sidebar.image("images/logoMahein.png", caption="", use_container_width=True)





# MEDICAMENT



st.markdown("<h2 style='color: green;'>Médicaments & Stock</h2>", unsafe_allow_html=True)

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
                    <div class="metric-label">📉 Stock Minimum</div>
                    <div class="metric-value">{stats_stock["stock_min"][0]}</div>
                </div>
            """, unsafe_allow_html=True)

            col3.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📈 Stock Maximum</div>
                    <div class="metric-value">{stats_stock["stock_max"][0]}</div>
                </div>
            """, unsafe_allow_html=True)

            col4, col5 = st.columns([2, 1])
            col4.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">📊 Stock Moyen</div>
                    <div class="metric-value">{stats_stock["stock_moyen"][0]}</div>
                </div>
            """, unsafe_allow_html=True)

            col5.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🧪 Catégories</div>
                    <div class="metric-value">{nb_categories}</div>
                </div>
            """, unsafe_allow_html=True)

     
        
        with st.expander("### 🏆 Top Médicaments"):
         with st.container():
            st.markdown("### 🏆 Top Médicaments")
            col6, col7, col8 = st.columns(3)
            col6.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🔥 Le plus vendu</div>
                    <div class="metric-value">{med_plus_vendu['nom'][0]}</div>
                </div>
            """, unsafe_allow_html=True)

            col7.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">❗ Stock le plus bas</div>
                    <div class="metric-value">{med_stock_bas['Nom_Commercial'][0]}</div>
                </div>
            """, unsafe_allow_html=True)

            col8.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">💰 Plus cher</div>
                    <div class="metric-value">{med_cher['Nom_Commercial'][0]}</div>
                </div>
            """, unsafe_allow_html=True)

            col9, _ = st.columns([1, 2])
            col9.markdown(f"""
                <div class="metric-box">
                    <div class="metric-label">🪙 Moins cher</div>
                    <div class="metric-value">{med_moins_cher['Nom_Commercial'][0]}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        

    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des statistiques : {e}")
else:
    st.error("❌ Les données 'medicament', 'stock' et 'detailVente' ne sont pas présentes dans le DataFrame.")









# Médicaments critiques en stock (<10 unités)
try:
    if "medicament" in df and "stock" in df:
        medicament = df["medicament"]
        stock = df["stock"]

        # Fusion des données
        merged_df = pd.merge(stock, medicament, on="ID_Medicament", how="left")

        # Créer des colonnes pour les éléments en ligne
        col1, col2 = st.columns([1, 1])

        # Sélection de la date dans la première colonne
        with col1:
            date_column = st.selectbox(
                "🗓️ Sélectionnez la date à utiliser pour l'analyse :",
                ["date_entree", "Date_Peremption"]
            )

        # Nettoyage des dates
        merged_df[date_column] = merged_df[date_column].astype(str).str.extract(r'(\d{1,2}/\d{1,2}/\d{4})')
        merged_df["Année"] = pd.to_datetime(merged_df[date_column], dayfirst=True, errors='coerce').dt.year
        merged_df = merged_df.dropna(subset=["Année"])

        # Filtrage des médicaments critiques
        stock_critique = (
            merged_df[merged_df["Stock_Disponible"] < 10]
            .groupby(["Année", "Nom_Commercial"])
            .size()
            .reset_index(name="Nombre_Médicaments_Critiques")
        )

        # Sélection de l’année dans la deuxième colonne
        with col2:
            selected_year = st.selectbox(
                "📅 Sélectionnez une année :",
                sorted(stock_critique["Année"].unique())
            )

        # Graphique 1 : Évolution (dans la première colonne)
        fig_area = px.area(
            stock_critique,
            x="Année",
            y="Nombre_Médicaments_Critiques",
            color="Nom_Commercial",
            title="📊 Évolution des Médicaments Critiques en Stock (<10 unités)",
            labels={"Nombre_Médicaments_Critiques": "Nombre de Médicaments Critiques"},
            color_discrete_sequence=px.colors.sequential.Plasma
        )

        # Graphique 2 : Camembert (dans la première colonne)
        filtered_data = stock_critique[stock_critique["Année"] == selected_year]
        fig = px.pie(
            filtered_data,
            names="Nom_Commercial",
            values="Nombre_Médicaments_Critiques",
            title=f"<b>Répartition des Médicaments Critiques en Stock en {selected_year}</b>",
            color_discrete_sequence=px.colors.sequential.Plasma,
            hole=0.4
        )

        # Affichage des graphiques l'un à côté de l'autre
        with col1:
            st.plotly_chart(fig_area, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("❌ Les feuilles 'medicament' et 'stock' ne sont pas disponibles dans le fichier Excel.")

except Exception as e:
    st.error(f"❌ Erreur lors du calcul des statistiques : {e}")








#Médicaments en surplus (>500 unités)

if df is not None and "medicament" in df and "stock" in df:
    # Récupération des deux DataFrames
    medicament = df["medicament"]
    stock = df["stock"]

    # Fusionner stock et medicament
    merged_df = pd.merge(stock, medicament, on="ID_Medicament", how="left")

    # Connexion à DuckDB en mémoire et insertion des données
    con = duckdb.connect(database=':memory:')
    con.register('pharmacie', merged_df)

    st.markdown("### 📈 Médicaments en surplus")
    custom_plasma = [
        "#0d0887",  # Bleu profond
        "#5c01a6",  # Violet foncé
        "#9c179e",  # Violet
        "#6a41b4",  # Violet clair
        "#4f76c4",  # Bleu plus clair
        "#3a93c6",
    ]



    try:
        # Requête SQL : obtenir tous les noms et leurs stocks
        query = """
            SELECT Nom_Commercial, count(Stock_Disponible) AS Total_Stock
            FROM pharmacie
            WHERE Stock_Disponible > 20
            GROUP BY Nom_Commercial
            ORDER BY Total_Stock DESC
        """
        surplus_df = con.execute(query).fetchdf()

        if not surplus_df.empty:
    # Création du bar chart horizontal
            fig = px.bar(
                surplus_df,
                x="Total_Stock",
                y="Nom_Commercial",
                orientation="h",
                title="📦 Médicaments en surplus (>500 unités)",
                labels={"Total_Stock": "Stock disponible", "Nom_Commercial": "Médicament"},
                text="Total_Stock",
                color="Nom_Commercial",  # Obligatoire pour appliquer color_discrete_sequence
                color_discrete_sequence=custom_plasma
            )
            fig.update_layout(
                yaxis=dict(categoryorder="total ascending"),
                showlegend=False  # Facultatif si tu veux éviter une légende répétitive
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun médicament en surplus (>500 unités) trouvé.")


    except Exception as e:
        st.error(f"❌ Erreur lors de la génération du graphique : {e}")

else:
    st.error("❌ Les données 'medicament' et 'stock' ne sont pas présentes dans le DataFrame.")




with st.expander("### ❌ Ruptures de stock sur le dernier mois"):

    if df is not None and "medicament" in df and "stock" in df:
        # Récupération des deux DataFrames
        medicament = df["medicament"]
        stock = df["stock"]

        # ✅ Conversion correcte du format Date_Reception
        stock["Date_Reception"] = pd.to_datetime(stock["Date_Reception"], format="%m/%d/%Y", errors="coerce")

        # Fusionner stock et medicament
        merged_df = pd.merge(stock, medicament, on="ID_Medicament", how="left")

        # Connexion à DuckDB en mémoire et insertion des données
        con = duckdb.connect(database=':memory:')
        con.register('pharmacie', merged_df)

        # Requête pour les ruptures de stock sur le dernier mois
        try:
            query = """
            SELECT 
                Nom_Commercial, 
                COUNT(ID_Stock) AS Nombre_de_ruptures
            FROM 
                pharmacie
            WHERE 
                quantite_disponible <= 0 
                AND Date_Reception >= CURRENT_DATE - INTERVAL '1 month'
            GROUP BY 
                Nom_Commercial
            ORDER BY 
                Nombre_de_ruptures DESC;
            """
            ruptures_df = con.execute(query).fetchdf()

            st.markdown("### ❌ Ruptures de stock sur le dernier mois")

            # Utilisation de st.columns pour afficher le tableau et le graphique côte à côte
            col1, col2 = st.columns([1, 2])  # Ajuste les proportions si nécessaire

            # Colonne 1: Tableau
            with col1:
                st.markdown("<br><br>", unsafe_allow_html=True) 
                st.dataframe(ruptures_df)

            # Colonne 2: Graphique Plotly
            with col2:
                # ✅ Graphique Plotly (barres verticales)
                if not ruptures_df.empty:
                    fig = px.bar(
                        ruptures_df,
                        x="Nom_Commercial",
                        y="Nombre_de_ruptures",
                        color="Nom_Commercial",  # Nécessaire pour appliquer color_discrete_sequence
                        title="📉 Médicaments en rupture de stock (dernier mois)",
                        labels={"Nom_Commercial": "Médicament", "Nombre_de_ruptures": "Nombre de ruptures"},
                        text="Nombre_de_ruptures",
                        color_discrete_sequence=px.colors.sequential.Plasma
                    )
                    fig.update_traces(textposition="outside")
                    fig.update_layout(
                        xaxis_tickangle=-45,
                        showlegend=False  # Cacher la légende si chaque barre correspond à un médicament unique
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Aucune rupture de stock détectée ce mois-ci.")

        except Exception as e:
            st.error(f"❌ Erreur lors de l'exécution de la requête : {e}")
    else:
        st.error("❌ Les données 'medicament' et 'stock' ne sont pas présentes dans le DataFrame.")






# Médicaments avec la plus forte et la plus faible rotation
if df is not None and "vente" in df and "detailVente" in df and "client" in df:
    vente = df["vente"]
    detail_vente = df["detailVente"]
    client = df["client"]

    merged = pd.merge(vente, detail_vente, on="ID_Vente", how="inner")

    # Fusion avec les noms de médicament si présents
    if "medicament" in df:
        medicament_df = df["medicament"]
        merged = pd.merge(merged, medicament_df[["ID_Medicament", "Nom_Commercial"]], on="ID_Medicament", how="left")
    else:
        merged["Nom_Commercial"] = merged["ID_Medicament"]

    # Connexion DuckDB
    con = duckdb.connect(database=":memory:")
    con.register("vente_detail", merged)

    with st.expander("🔄 Médicaments avec la plus forte et la plus faible rotation"):
        st.markdown("## ⚖️ Comparaison des rotations des médicaments")

        try:
            # Médicament le plus vendu
            top_medicament = con.execute("""
                SELECT Nom_Commercial, SUM(Quantité) AS Total_Vendu
                FROM vente_detail
                GROUP BY Nom_Commercial
                ORDER BY Total_Vendu DESC
                LIMIT 1
            """).fetchdf()

            top5_df = con.execute("""
                SELECT Nom_Commercial, SUM(Quantité) AS Total_Vendu
                FROM vente_detail
                GROUP BY Nom_Commercial
                ORDER BY Total_Vendu DESC
                LIMIT 5
            """).fetchdf()

            # Médicament le moins vendu
            least_medicament = con.execute("""
                SELECT Nom_Commercial, SUM(Quantité) AS Total_Vendu
                FROM vente_detail
                GROUP BY Nom_Commercial
                HAVING SUM(Quantité) > 0
                ORDER BY Total_Vendu ASC
                LIMIT 1
            """).fetchdf()

            bottom5_df = con.execute("""
                SELECT Nom_Commercial, SUM(Quantité) AS Total_Vendu
                FROM vente_detail
                GROUP BY Nom_Commercial
                HAVING SUM(Quantité) > 0
                ORDER BY Total_Vendu ASC
                LIMIT 5
            """).fetchdf()

            col2, col1 = st.columns(2)

            with col1:
                st.markdown("### 🔁 Plus forte rotation")
                if not top_medicament.empty:
                    nom_top = top_medicament.iloc[0]["Nom_Commercial"]
                    qte_top = int(top_medicament.iloc[0]["Total_Vendu"])
                    st.success(f"🏅 Médicament : **{nom_top}**\n\n💊 Quantité vendue : **{qte_top}**")
                else:
                    st.warning("Aucune donnée pour la forte rotation.")
                fig_top = px.bar(
                    top5_df,
                    x="Nom_Commercial",
                    y="Total_Vendu",
                    title="Top 5 Médicaments les plus vendus",
                    text_auto=True,
                    color="Nom_Commercial",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_top, use_container_width=True)

            with col2:
                st.markdown("### 📉 Plus faible rotation")
                if not least_medicament.empty:
                    nom_low = least_medicament.iloc[0]["Nom_Commercial"]
                    qte_low = int(least_medicament.iloc[0]["Total_Vendu"])
                    st.warning(f"📉 Médicament : **{nom_low}**\n\n💊 Quantité vendue : **{qte_low}**")
                else:
                    st.info("Aucune donnée pour la faible rotation.")
                fig_low = px.bar(
                    bottom5_df,
                    x="Nom_Commercial",
                    y="Total_Vendu",
                    title="Top 5 Médicaments les moins vendus",
                    text_auto=True,
                    color="Nom_Commercial",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_low, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Erreur lors de l'affichage : {e}")
else:
    st.warning("Les données 'vente', 'detailVente' et 'client' ne sont pas disponibles.")







# tsy azoko fa mandeha

st.markdown("### Nombre moyen de jours avant rupture de stock")

try:
    vente_df = df["vente"].copy()
    stock_df = df["stock"].copy()
    lot_df = df["lot"].copy()

    # Vérification existence de ID_Medicament
    if "ID_Medicament" not in vente_df.columns or "ID_Medicament" not in stock_df.columns:
        vente_df = pd.merge(vente_df, lot_df[["id_lot", "ID_Medicament"]], on="id_lot", how="left")
        stock_df = pd.merge(stock_df, lot_df[["id_lot", "ID_Medicament"]], on="id_lot", how="left")

    # Convertir les dates
    vente_df["Date_Vente"] = pd.to_datetime(vente_df["Date_Vente"], errors='coerce')
    stock_df["date_entree"] = pd.to_datetime(stock_df["date_entree"], errors='coerce')

    # Fusion ventes + stock via id_lot
    merged_df = pd.merge(vente_df, stock_df[["id_lot", "date_entree"]], on="id_lot", how="inner")

    # Vérifier que ID_Medicament est bien là
    if "ID_Medicament" not in merged_df.columns:
        merged_df = pd.merge(merged_df, lot_df[["id_lot", "ID_Medicament"]], on="id_lot", how="left")

    # Calcul des jours avant rupture
    rupture_info = []
    for id_lot, group in merged_df.groupby("id_lot"):
        date_entree = group["date_entree"].iloc[0]
        date_derniere_vente = group["Date_Vente"].max()
        jours_avant_rupture = (date_derniere_vente - date_entree).days

        rupture_info.append({
            "id_lot": id_lot,
            "ID_Medicament": group["ID_Medicament"].iloc[0],
            "jours_avant_rupture": jours_avant_rupture
        })

    rupture_df = pd.DataFrame(rupture_info)

    # Ajouter le nom du médicament s’il existe
    if "medicament" in df and "Nom_Commercial" in df["medicament"].columns:
        rupture_df = pd.merge(rupture_df, df["medicament"][["ID_Medicament", "Nom_Commercial"]], on="ID_Medicament", how="left")
    else:
        rupture_df["Nom_Commercial"] = rupture_df["ID_Medicament"]

    # Moyenne
    moyenne_rupture = rupture_df["jours_avant_rupture"].mean()
    st.success(f"**{moyenne_rupture:.2f} jours** en moyenne avant rupture de stock d’un lot.")

    # Graphique
    fig = px.bar(
        rupture_df.sort_values("jours_avant_rupture", ascending=False),
        x="Nom_Commercial",
        y="jours_avant_rupture",
        text_auto=True,
        title="Jours avant rupture par médicament",
        labels={"jours_avant_rupture": "Jours", "Nom_Commercial": "Médicament"},
        color="Nom_Commercial"
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erreur lors du calcul : {e}")
