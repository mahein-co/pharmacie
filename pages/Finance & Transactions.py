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




# transaction


st.markdown("<h2 style='color: green;'>Finance & Transactions</h2>", unsafe_allow_html=True)

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








#Marge bénéficiaire moyenne et Médicament avec la plus forte marge

if df is not None and "medicament" in df and "stock" in df:
    medicament = df["medicament"]
    stock = df["stock"]

    # Fusionner stock et medicament
    merged_df = pd.merge(stock, medicament, on="ID_Medicament", how="left")

    # Calcul de la marge bénéficiaire en pourcentage
    merged_df["Marge_Pourcent"] = ((merged_df["Prix_Vente"] - merged_df["Prix_Achat"]) / merged_df["Prix_Vente"]) * 100

    # Connexion à DuckDB en mémoire
    con = duckdb.connect(database=':memory:')
    con.register('pharmacie', merged_df)

    # Palette de couleurs personnalisée
    custom_plasma = [
        "#0d0887", "#5c01a6", "#9c179e",
        "#6a41b4", "#4f76c4", "#3a93c6"
    ]

    # Création de deux colonnes avec Streamlit
    col1, col2 = st.columns(2)

    # Afficher Marge bénéficiaire moyenne dans la première colonne
    with col1:
        st.markdown("### 💰 Marge bénéficiaire moyenne (%) par médicament")
        try:
            query_marge = """
                SELECT 
                    Nom_Commercial,
                    ROUND(AVG(Marge_Pourcent), 2) AS Marge_Moyenne_Pourcent
                FROM pharmacie
                GROUP BY Nom_Commercial
                ORDER BY Marge_Moyenne_Pourcent DESC
            """
            marge_df = con.execute(query_marge).fetchdf()

            if not marge_df.empty:
                
                # ✅ Ajout du pourcentage par médicament (optionnel mais utile)
                total_marge = marge_df["Marge_Moyenne_Pourcent"].sum()
                marge_df["Pourcentage"] = (marge_df["Marge_Moyenne_Pourcent"] / total_marge) * 100
                marge_df["Pourcentage"] = marge_df["Pourcentage"].round(2)

                # ✅ Sauvegarde JSON
                marge_json = marge_df[["Nom_Commercial", "Marge_Moyenne_Pourcent", "Pourcentage"]]
                with open("json/marge_moyenne_par_medicament.json", "w", encoding="utf-8") as f:
                    json.dump(marge_json.to_dict(orient="records"), f, ensure_ascii=False, indent=4)

                
                
                fig_marge = px.bar(
                    marge_df,
                    x="Marge_Moyenne_Pourcent",
                    y="Nom_Commercial",
                    orientation="h",
                    title="💰 Marge bénéficiaire moyenne (%) par médicament",
                    labels={"Marge_Moyenne_Pourcent": "Marge (%)", "Nom_Commercial": "Médicament"},
                    text="Marge_Moyenne_Pourcent",
                    color="Nom_Commercial",
                    color_discrete_sequence=custom_plasma
                )
                fig_marge.update_layout(
                    yaxis=dict(categoryorder="total ascending"),
                    showlegend=False
                )
                st.plotly_chart(fig_marge, use_container_width=True)
                
                  # ✅ Moyenne globale
                moyenne_globale_query = """
                    SELECT ROUND(AVG(Marge_Pourcent), 2) AS Marge_Totale_Moyenne FROM pharmacie
                """
                moyenne_globale = con.execute(moyenne_globale_query).fetchone()[0]
                st.info(f"📊 **Marge bénéficiaire moyenne globale : {moyenne_globale}%**")
        
            else:
                st.info("Aucune donnée de marge disponible.")
        except Exception as e:
            st.error(f"❌ Erreur lors du calcul de la marge bénéficiaire moyenne : {e}")

    # Afficher Médicament avec la plus forte marge dans la deuxième colonne
    with col2:
        try:
            query_top5_marge = """
                SELECT 
                    Nom_Commercial,
                    ROUND(AVG(Marge_Pourcent), 2) AS Marge_Moyenne_Pourcent
                FROM pharmacie
                GROUP BY Nom_Commercial
                ORDER BY Marge_Moyenne_Pourcent DESC
                LIMIT 5
            """
            top5_marge_df = con.execute(query_top5_marge).fetchdf()

            if not top5_marge_df.empty:
                
                # ✅ Sauvegarde JSON pour le Top 5 des médicaments les plus rentables
                top5_json = top5_marge_df[["Nom_Commercial", "Marge_Moyenne_Pourcent"]]
                with open("json/top5_marge_medocs.json", "w", encoding="utf-8") as f:
                    json.dump(top5_json.to_dict(orient="records"), f, ensure_ascii=False, indent=4)
                    
            
                # Affichage du 1er
                nom = top5_marge_df.iloc[0]["Nom_Commercial"]
                marge = top5_marge_df.iloc[0]["Marge_Moyenne_Pourcent"]
                st.success(f"💎 **Médicament le plus rentable :** {nom} avec **{marge}%** de marge bénéficiaire moyenne.")

                # Graphique barres
                fig = px.bar(
                    top5_marge_df,
                    x="Marge_Moyenne_Pourcent",
                    y="Nom_Commercial",
                    orientation="h",
                    title="Top 5 des médicaments les plus rentables",
                    labels={"Nom_Commercial": "Médicament", "Marge_Moyenne_Pourcent": "Marge (%)"},
                    text="Marge_Moyenne_Pourcent",
                    color="Nom_Commercial",
                    color_discrete_sequence=px.colors.sequential.Plasma_r
                )
                fig.update_layout(
                    yaxis=dict(categoryorder="total ascending"),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucun médicament trouvé avec une marge calculable.")
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération du graphique : {e}")

else:
    st.error("❌ Les données 'medicament' et 'stock' ne sont pas présentes dans le DataFrame.")








if df is not None and "medicament" in df and "stock" in df:
    medicament = df["medicament"]
    stock = df["stock"]

    # Fusionner stock et medicament
    merged_df = pd.merge(stock, medicament, on="ID_Medicament", how="left")

    # Connexion à DuckDB en mémoire
    con = duckdb.connect(database=':memory:')
    con.register('pharmacie', merged_df)

    # Palette de couleurs personnalisée
    custom_plasma = [
        "#0d0887", "#5c01a6", "#9c179e",
        "#6a41b4", "#4f76c4", "#3a93c6"
    ]

    # 🔻 Calcul des pertes estimées
    try:
        # Ajouter les colonnes de pertes
        merged_df["Quantite_Perdue"] = merged_df["Quantite_Commande"] - merged_df["quantite_disponible"]
        merged_df["Quantite_Perdue"] = merged_df["Quantite_Perdue"].clip(lower=0)  # Pas de pertes négatives
        merged_df["Perte_Estimee"] = merged_df["Quantite_Perdue"] * merged_df["Prix_Unitaire"]

        # Assurer que la date est bien au format datetime
        merged_df["date_entree"] = pd.to_datetime(merged_df["date_entree"], errors="coerce")

        # Re-enregistrement dans DuckDB avec les nouvelles colonnes
        con.unregister("pharmacie")
        con.register("pharmacie", merged_df)

        # Total des pertes
        query_total_perte = """
            SELECT 
                SUM(Perte_Estimee) AS Total_Perte
            FROM pharmacie
        """
        perte_totale = con.execute(query_total_perte).fetchone()[0]
        perte_totale = round(perte_totale, 2) if perte_totale is not None else 0

        # Affichage du total
        st.markdown("### 🧾 Total estimé des pertes dues aux médicaments invendus ou abîmés")
        st.warning(f"💸 **Perte estimée : {perte_totale} Ar**")

        # ✅ Graphe de l'évolution des pertes dans le temps
        perte_temps_df = merged_df.groupby("date_entree").agg({"Perte_Estimee": "sum"}).reset_index()
        perte_temps_df = perte_temps_df.sort_values("date_entree")

        if not perte_temps_df.empty:
            fig_perte = px.line(
                perte_temps_df,
                x="date_entree",
                y="Perte_Estimee",
                title="📉 Évolution des pertes estimées dans le temps",
                labels={"date_entree": "Date d'entrée", "Perte_Estimee": "Perte estimée (Ar)"},
                markers=True
            )
            fig_perte.update_traces(line=dict(color="#D62728", width=3))
            fig_perte.update_layout(xaxis_title="Date", yaxis_title="Perte estimée (Ar)")
            st.plotly_chart(fig_perte, use_container_width=True)
        else:
            st.info("Aucune donnée de perte disponible dans le temps.")
    except Exception as e:
        st.error(f"❌ Erreur lors du calcul des pertes estimées : {e}")

else:
    st.error("❌ Les données 'medicament' et 'stock' ne sont pas présentes dans le DataFrame.")












if df is not None and "medicament" in df and "stock" in df:
    medicament = df["medicament"]
    stock = df["stock"]

    # Fusion
    merged_df = pd.merge(stock, medicament, on="ID_Medicament", how="left")
    merged_df["date_entree"] = pd.to_datetime(merged_df["date_entree"], errors="coerce")

    # Calcul des colonnes utiles
    merged_df["Quantite_Sortie"] = (merged_df["Quantite_Commande"] - merged_df["quantite_disponible"]).clip(lower=0)
    merged_df["Quantite_Entree"] = merged_df["Quantite_Commande"]
    merged_df["Ecart"] = merged_df["Quantite_Entree"] - merged_df["Quantite_Sortie"]

    # Agrégation par date
    ecart_df = merged_df.groupby("date_entree").agg({
        "Quantite_Entree": "sum",
        "Quantite_Sortie": "sum",
        "Ecart": "sum"
    }).reset_index().sort_values("date_entree")

    # Affichage du graphe
    st.markdown("### ⚖️ Écart entre transactions entrantes et sortantes")
    if not ecart_df.empty:
        fig_ecart = px.line(
            ecart_df,
            x="date_entree",
            y=["Quantite_Entree", "Quantite_Sortie", "Ecart"],
            labels={
                "value": "Quantité",
                "variable": "Type de transaction",
                "date_entree": "Date"
            },
            title="📊 Évolution des quantités entrantes, sortantes et de l'écart"
        )
        fig_ecart.update_traces(mode="lines+markers")
        fig_ecart.update_layout(legend_title_text="Transaction")
        st.plotly_chart(fig_ecart, use_container_width=True)
    else:
        st.info("Aucune donnée disponible pour calculer les écarts.")

else:
    st.error("❌ Les données 'medicament' et 'stock' ne sont pas présentes dans le DataFrame.")
