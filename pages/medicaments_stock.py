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

st.markdown("<h2 style='color: green;'>Vue en details des Médicaments</h2>", unsafe_allow_html=True)

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



# Médicaments critiques en stock (<10 unités)

st.markdown("Détails Médicaments critiques en stock ")
            
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
    
    #Médicaments en surplus (>500 unités)

    st.markdown("Médicaments en surplus")
            
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


