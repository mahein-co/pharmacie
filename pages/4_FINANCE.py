import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit.components.v1 import html
from views import finance_views
from data.mongodb_client import MongoDBClient
from pipelines import pipelines_finance




# Initialisation
st.set_page_config(page_title="FINANCE", layout="wide")

html("""
<style>
    @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
    
  .box {
    color: #eee;
    padding: 20px;
    font-family: 'Dancing Script', cursive;
    border-radius: 10px;
    font-size: 74px;
  }
</style>
<div class="box">Finance</div>
""")

# --------------------
# Données exemple
# --------------------


np.random.seed(42)
dates = pd.date_range(start="2024-01-01", end="2024-07-21", freq='D')
data = pd.DataFrame({
    'date': np.random.choice(dates, 200),
    'montant': np.random.randint(1000, 10000, size=200)
})
data['date'] = pd.to_datetime(data['date'])

# Filtre : Jour, Semaine, Mois
filtre = st.selectbox("Filtrer par :", ["Jour", "Semaine", "Mois"])

if filtre == "Jour":
    data_grouped = data.groupby(data['date'].dt.date)['montant'].sum().reset_index()
    data_grouped['label'] = pd.to_datetime(data_grouped['date']).dt.strftime('%d %b')
elif filtre == "Semaine":
    data['semaine'] = data['date'].dt.to_period("W").apply(lambda r: r.start_time)
    data_grouped = data.groupby('semaine')['montant'].sum().reset_index()
    data_grouped['label'] = pd.to_datetime(data_grouped['semaine']).dt.strftime('Sem. %W')
elif filtre == "Mois":
    data['mois'] = data['date'].dt.to_period("M").dt.to_timestamp()
    data_grouped = data.groupby('mois')['montant'].sum().reset_index()
    data_grouped['label'] = pd.to_datetime(data_grouped['mois']).dt.strftime('%b %Y')

total_ca = data['montant'].sum()
dernier_val = data_grouped['montant'].iloc[-1]

#importation html et css
st.markdown(finance_views.custom_css, unsafe_allow_html=True)
st.markdown(finance_views.kpis_style, unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])
with col1:
    st.markdown(finance_views.kpis_html, unsafe_allow_html=True)
with col2:
    st.line_chart(data=data_grouped.set_index('label')['montant'], use_container_width=True)


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
        df_forte_marge = df_forte_marge.sort_values(by="Marge", ascending=False).head(3)

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
        df_faible_marge = df_faible_marge.sort_values(by="Marge", ascending=False).head(3)

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
    
