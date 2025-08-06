import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from utils import load_data
from db import init_duckdb
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
import plotly.graph_objects as go


from data.mongodb_client import MongoDBClient
from pipelines import pipelines_employe

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

#initiation a mongoDB 
employe_collection = MongoDBClient(collection_name="employe")

employe_documents = employe_collection.find_all_documents()


st.markdown("<h2 style='color: green;'>EMPLOYERS</h2>", unsafe_allow_html=True)

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







with st.container():

    st.markdown("<h3>📊 Indicateurs clés des performances</h3>", unsafe_allow_html=True)

    if employe_collection:
    
        #2--Salaire moyen 
        salaire_moyen = employe_collection.make_specific_pipeline(pipeline=pipelines_employe.Salaire_moyen,title="salaire moyen")

        try:
            salaire_moyen = salaire_moyen[0]["salaire_moyen"] if salaire_moyen else 0
        except Exception as e:
            salaire_moyen = 0

        # 1--Nombre total employers 
        Nb_employers = employe_collection.count_distinct_agg(field_name="id_employe")

        #3-- Age moyen 

        age_moyen = employe_collection.make_specific_pipeline(pipeline=pipelines_employe.Age_moyen,title="age moyen")

        try:
            age_moyen = age_moyen[0]["age_moyen"] if age_moyen else 0
        except Exception as e:
            age_moyen = 0
    
        

        # CSS sombre moderne
    st.markdown("""
            <style>
            .scorecard {
                background-color: #1e1e1e;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                border-left: 6px solid #00FF88;
                color: white;
                text-align: left;
                margin: 5px;
            }
            .scorecard h4 {
                font-size: 16px;
                margin-bottom: 5px;
            }
            .scorecard p {
                font-size: 24px;
                font-weight: bold;
                margin: 0;
            }
            </style>
        """, unsafe_allow_html=True)

        # Affichage des scorecards
    col1, col2, col3 = st.columns(3)

    with col1:
            st.markdown(f"""
                <div class="scorecard">
                    <h4>Effectif total d’employés</h4>
                    <p>{Nb_employers}</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
            st.markdown(f"""
                <div class="scorecard">
                    <h4>Salaire moyen</h4>
                    <p>{salaire_moyen} Ar</p>
                </div>
            """, unsafe_allow_html=True)

    with col3:
            st.markdown(f"""
                <div class="scorecard">
                    <h4>Âge moyen</h4>
                    <p>{age_moyen} ans</p>
                </div>
            """, unsafe_allow_html=True)




st.set_page_config(layout="wide")



# Conteneur principal avec deux colonnes
with st.container():
    col1, col2 = st.columns(2)


    if employe_collection:
    # Récupération des données via pipeline
        eff_categorie = employe_collection.make_specific_pipeline(pipeline=pipelines_employe.Eff_categorie, title="effectif par categorie")
        eff_fonction = employe_collection.make_specific_pipeline(pipeline=pipelines_employe.Eff_fonction,title="effectif par fonction")
    
    # Convertir en DataFrame
    df_cat = pd.DataFrame(eff_categorie)
    df_cat.columns = ['Catégorie', 'Effectif']

    #Convertir en DataFrame
    df_fct = pd.DataFrame(eff_fonction)
    df_fct.columns = ['Fonction','Effectif']

    # Affichage dans Streamlit
    with col1:
        st.markdown("<h3>Effectif total d’employés par catégorie</h3>", unsafe_allow_html=True)

        fig_pie = px.pie(df_cat,
                         names='Catégorie',
                         values='Effectif',
                         hole=0.4,
                         color_discrete_sequence=px.colors.sequential.Agsunset)

        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)


    # -----------------------
    # 🔀 SANKEY (pas possible avec px, on utilise go)
    # -----------------------
    with col2:
        st.markdown("<h3>Effectif total par fonction</h3>", unsafe_allow_html=True)

        fig_pie = px.pie(df_fct,
                         names='Fonction',
                         values='Effectif',
                         hole=0.4,
                         color_discrete_sequence=px.colors.sequential.Agsunset)

        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
with st.container():
    st.markdown("<h3>Evolution de fonction</h3>", unsafe_allow_html=True)

    
    # 🔹 Exemple : Données du pipeline MongoDB
    data = [
        {"annee": 2017, "fonction": "Comptable", "effectif": 2},
        {"annee": 2017, "fonction": "Gérant", "effectif": 1},
        {"annee": 2019, "fonction": "Pharmacien assistant", "effectif": 2},
        {"annee": 2020, "fonction": "Comptable", "effectif": 1},
        {"annee": 2022, "fonction": "Agent de comptoir", "effectif": 2},
        {"annee": 2024, "fonction": "Comptable", "effectif": 1},
        {"annee": 2023, "fonction": "Pharmacien titulaire", "effectif": 1}
    ]

    df = pd.DataFrame(data)

    # 🔸 Créer source / target labels
    df["source"] = df["annee"].astype(str)
    df["target"] = df["annee"].astype(str) + " - " + df["fonction"]

    # 🔸 Labels uniques
    labels = pd.unique(df[["source", "target"]].values.ravel().tolist())

    # 🔸 Mapping label → index
    label_map = {label: i for i, label in enumerate(labels)}
    df["source_id"] = df["source"].map(label_map)
    df["target_id"] = df["target"].map(label_map)

    # 🔸 Sankey figure
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="lightblue"
        ),
        link=dict(
            source=df["source_id"],
            target=df["target_id"],
            value=df["effectif"],
            color="rgba(31, 119, 180, 0.4)"
        )
    ))

    fig.update_layout(title_text="📈 Évolution des fonctions par année d’embauche", font_size=12)

    # 🔸 Affichage dans Streamlit
    st.plotly_chart(fig, use_container_width=True)



    



    

