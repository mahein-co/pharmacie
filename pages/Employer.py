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
    # Données d'exemple
    data = pd.DataFrame({
            'Nom': ['Alice', 'Bob', 'Charlie', 'Diana', 'Ethan'],
            'Salaire': [3000, 3500, 4000, 3200, 3800],
            'Age': [28, 34, 30, 29, 40]
            })

        # Calculs
    effectif_total = len(data)
    salaire_moyen = round(data['Salaire'].mean(), 2)
    age_moyen = round(data['Age'].mean(), 1)
        

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
                    <p>{effectif_total}</p>
                </div>
            """, unsafe_allow_html=True)

    with col2:
            st.markdown(f"""
                <div class="scorecard">
                    <h4>Salaire moyen</h4>
                    <p>{salaire_moyen} €</p>
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

# Données fictives
df_employes = pd.DataFrame({
    'Nom': ['Alice', 'Bob', 'Charlie', 'Diana', 'Ethan', 'Fatima', 'Georges', 'Hana', 'Ivan', 'Julia'],
    'Catégorie': ['Cadre', 'Technicien', 'Cadre', 'Employé', 'Employé', 'Cadre', 'Technicien', 'Employé', 'Employé', 'Cadre'],
    'Départ': ['Stagiaire', 'Stagiaire', 'Employé', 'Employé', 'Stagiaire', 'Employé', 'Stagiaire', 'Employé', 'Employé', 'Stagiaire'],
    'Actuel': ['Cadre', 'Technicien', 'Cadre', 'Technicien', 'Employé', 'Cadre', 'Cadre', 'Employé', 'Technicien', 'Cadre']
})

# Conteneur principal avec deux colonnes
with st.container():
    col1, col2 = st.columns(2)

    # -----------------------
    # 📊 CAMEMBERT avec px
    # -----------------------
    with col1:
        st.markdown("<h3>Effectif total d’employés par catégorie</h3>", unsafe_allow_html=True)

        df_cat = df_employes['Catégorie'].value_counts().reset_index()
        df_cat.columns = ['Catégorie', 'Effectif']

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
        st.markdown("<h3>Évolution de carrière</h3>", unsafe_allow_html=True)

        flux = df_employes.groupby(['Départ', 'Actuel']).size().reset_index(name='Count')
        labels = list(set(flux['Départ']).union(set(flux['Actuel'])))
        label_to_index = {label: i for i, label in enumerate(labels)}

        sources = [label_to_index[d] for d in flux['Départ']]
        targets = [label_to_index[a] for a in flux['Actuel']]
        values = flux['Count']

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="lightgreen"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color="rgba(0,255,136,0.4)"
            ))])

        fig_sankey.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_sankey, use_container_width=True)
