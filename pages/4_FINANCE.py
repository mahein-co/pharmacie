import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit.components.v1 import html
from views import finance_views
from data.mongodb_client import MongoDBClient
from pipelines import pipelines_finance,pipeline_overview

from style import style


# Initialisation
st.set_page_config(page_title="FINANCE", layout="wide")

html("""
<style>
    @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
    
  .box {
    color: #7827e6;
    font-family: 'Dancing Script', cursive;
    font-size: 74px;
    margin-top:-1rem;
  }
</style>
<div class="box">Finance</div>
""")


# Data ------------------------------------ 
# Import des données depuis le backend
overview_documents = pipeline_overview.overview_collection.find_all_documents()
df = pd.DataFrame(overview_documents)
# Assurer que la colonne est bien au format datetime
df['date_de_vente'] = pd.to_datetime(df['date_de_vente'])
df['chiffre_affaires'] = df['quantite'] * df['prix_unitaire']

# Résumés temporels
daily_revenue = df.resample('D', on='date_de_vente')['chiffre_affaires'].sum().reset_index()
weekly_revenue = df.resample('W', on='date_de_vente')['chiffre_affaires'].sum().reset_index()
monthly_revenue = df.resample('ME', on='date_de_vente')['chiffre_affaires'].sum().reset_index()
year_revenue = df.resample('YE', on='date_de_vente')['chiffre_affaires'].sum().reset_index()

filtre = st.selectbox("Filtrer par :", ["Jour", "Semaine", "Mois", "Année"])

if filtre == "Jour":
    df_filtre = daily_revenue.copy()
    df_filtre['label'] = df_filtre['date_de_vente'].dt.strftime('%d %b')
elif filtre == "Semaine":
    df_filtre = weekly_revenue.copy()
    df_filtre['label'] = df_filtre['date_de_vente'].dt.strftime('Sem. %W')
elif filtre == "Mois":
    df_filtre = monthly_revenue.copy()
    df_filtre['label'] = df_filtre['date_de_vente'].dt.strftime('%b %Y')
elif filtre == "Année":
    df_filtre = year_revenue.copy()
    df_filtre['label'] = df_filtre['date_de_vente'].dt.strftime('%Y')

df_filtre.rename(columns={
    'date_de_vente': 'Période',
    'chiffre_affaires': "Chiffre d'affaires"
}, inplace=True)

total_chiffre_affaire = df_filtre["Chiffre d'affaires"].sum()
dernier_ca = df_filtre["Chiffre d'affaires"].iloc[-1]


#importation html et css
st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])
with col1:
    html_code = finance_views.get_kpi_html(filtre, total_chiffre_affaire)
    st.markdown(html_code, unsafe_allow_html=True)
with col2:
    # Affichage du graphique
    html("""
    <style>
        @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
        
    .box {
        color: #7827e6;
        font-family: 'Quicksand', cursive;
        font-size: 35px;
        margin-top:-1rem;
        text-align: center;
    }
    </style>
    <p class="box">Évolution du chiffre d'affaires</p>
    """)
    # st.subheader(f"Évolution du chiffre d'affaires par {filtre.lower()}")
    st.line_chart(data=df_filtre.set_index('Période')["Chiffre d'affaires"])


with st.container():
    col1,col2 = st.columns(2)

    with col1:
        data = finance_views.medoc_rapporte_moins
        df_rapporte_moins = pd.DataFrame(data)
        df_rapporte_moins.rename(columns={"_id" : "Médicaments", "total_gain" : "Total Gain"},inplace=True)

        st.markdown("""
            <style>
                .custom-card {
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 30px;
                }
            </style>
        """, unsafe_allow_html=True)

        # 🔸 Graphique camembert
        fig = px.pie(
            df_rapporte_moins,
            names="Médicaments",
            values="Total Gain",
            hole=0.4  # Donut style
        )

        # ✅ Mise à jour du layout pour centrer le titre proprement
        fig.update_layout(
            title={
                'text': "💰Médicament rapport Moins",
                'x': 0.5,  # Centre horizontalement
                'xanchor': 'center',
                'yanchor': 'top'
            },
            title_font=dict(size=18),  # Taille du titre
        )

        # 🎯 Affichage dans Streamlit
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        data = finance_views.medoc_rapporte_plus
        df_rapporte_plus = pd.DataFrame(data)
        df_rapporte_plus.rename(columns={"_id" : "Médicaments", "total_gain" : "Total Gain"},inplace=True)

        st.markdown("""
            <style>
                .custom-card {
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 30px;
                }
            </style>
        """, unsafe_allow_html=True)

        # 🔸 Graphique camembert
        fig = px.pie(
            df_rapporte_plus,
            names="Médicaments",
            values="Total Gain",
            hole=0.4  # Donut style
        )

        # ✅ Mise à jour du layout pour centrer le titre proprement
        fig.update_layout(
            title={
                'text': "💰 Médicament Rapport Plus",
                'x': 0.5,  # Centre horizontalement
                'xanchor': 'center',
                'yanchor': 'top'
            },
            title_font=dict(size=18),  # Taille du titre
        )

        # 🎯 Affichage dans Streamlit
        st.plotly_chart(fig, use_container_width=True)


with st.container():
    col1,col2 = st.columns(2)

    with col1:
        st.markdown("""
        <style>
            .custom-card {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
        </style>
    """, unsafe_allow_html=True) 
        # 🔹 Données
        data = finance_views.medoc_forte_marge
        df_forte_marge = pd.DataFrame(data)

        # 🔹 Nettoyage / renommage
        df_forte_marge.rename(columns={
            "nom_medicament": "Médicaments",
            "marge_prix": "Marge"
        }, inplace=True)
        df_forte_marge["Marge"] = df_forte_marge["Marge"].round(2)
        df_forte_marge = df_forte_marge.sort_values(by="Marge", ascending=False)

        # 🔹 CSS pour carte centrée
        st.markdown("""
            <style>
                .custom-card {
                    background-color: #f9f9f9;
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    margin: 30px auto;
                    max-width: 800px;
                }
                .custom-card h4 {
                    text-align: center;
                    font-size: 24px;
                    color: #333333;
                }
            </style>
        """, unsafe_allow_html=True)

        # 🔹 Graphique
        fig = px.bar(
            df_forte_marge,
            x="Médicaments",
            y="Marge",
            text="Marge",
            color="Marge",
            color_continuous_scale=px.colors.sequential.Plasma
        )

        fig.update_layout(
            xaxis_title="Médicaments",
            yaxis_title="Marge prix",
            title={
                        'text': "Forte marge ",
                        'x': 0.5,  # Centre horizontalement
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },
            title_font=dict(size=18),  # Taille du titre
            yaxis=dict(range=[0, df_forte_marge["Marge"].max() * 1.2]),
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )

        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

        # 🔹 Fin de la carte
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <style>
                .custom-card {
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 30px;
                }
            </style>
        """, unsafe_allow_html=True)
        data = finance_views.medoc_faible_marge
        df_faible_marge = pd.DataFrame(data)
        
        df_faible_marge.rename(columns={
            "nom_medicament": "Médicaments",
            "marge_prix": "Marge"
        }, inplace=True)
        df_faible_marge["Marge"] = df_faible_marge["Marge"].round(2)
        df_faible_marge = df_faible_marge.sort_values(by="Marge", ascending=False)

        # 🔹 CSS pour carte centrée
        st.markdown("""
            <style>
                .custom-card {
                    background-color: #f9f9f9;
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    margin: 30px auto;
                    max-width: 800px;
                }
                .custom-card h4 {
                    text-align: center;
                    font-size: 24px;
                    color: #333333;
                }
            </style>
        """, unsafe_allow_html=True)

        # 🔹 Graphique
        fig = px.bar(
            df_faible_marge,
            x="Médicaments",
            y="Marge",
            text="Marge",
            color="Marge",
            color_continuous_scale=px.colors.sequential.Plasma
        )

        fig.update_layout(
            xaxis_title="Médicaments",
            yaxis_title="Marge prix",
            title={
                        'text': " Faible marge ",
                        'x': 0.5,  # Centre horizontalement
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },
            title_font=dict(size=18),  # Taille du titre
            yaxis=dict(range=[0, df_faible_marge["Marge"].max() * 1.2]),
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )

        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

        # 🔹 Fin de la carte
        st.markdown("</div>", unsafe_allow_html=True)
with st.container():
        # 🔹 Style personnalisé (carte)
        st.markdown("""
            <style>
                .custom-card {
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 30px;
                }
            </style>
        """, unsafe_allow_html=True)

        # Chargement des données
        data = finance_views.marge_benefice_moyen
        df_marge_moyen = pd.DataFrame(data)

        # Renommage des colonnes
        df_marge_moyen.rename(columns={
            "prix_unitaire": "Prix Vente",
            "prix_fournisseur": "Prix Achats",
            "marge_prix": "Marge Bénéficiaire"
        }, inplace=True)

        # Extraction directe des valeurs (sans moyenne)
        prix_achat = df_marge_moyen.loc[0, "Prix Achats"]
        marge = df_marge_moyen.loc[0, "Marge Bénéficiaire"]
        prix_vente = df_marge_moyen.loc[0, "Prix Vente"]

        # Préparation des données pour le funnel chart
        funnel_data = pd.DataFrame({
            "Étape": ["Prix Vente","Prix Achats", "Marge Bénéficiaire"],
            "Valeur": [prix_vente, prix_achat, marge]
        })

        # Création du graphique entonnoir 2D
        fig = px.funnel(
            funnel_data,
            x="Valeur",
            y="Étape",
            title="Graphique entonnoir de la marge bénéficiaire"
        )

        fig.update_layout(
                    title={
                        'text': "Graphique entonnoir de la marge bénéficiaire",
                        'x': 0.5,  # Centre horizontalement
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },
                    title_font=dict(size=18),  # Taille du titre
                )

        # Affichage dans Streamlit
        st.plotly_chart(fig)

with st.container():
    st.markdown("""
    <style>
        .custom-card {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)
    
