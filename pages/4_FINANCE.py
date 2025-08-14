import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pymongo import MongoClient
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
# Récupération des données depuis la vue MongoDB
# Exemple : extraction brute sans agrégation MongoDB complexe
# --- Données ---
# --- Charger les données ---

# --- Style CSS pour la card ---


# # Assurer que la colonne est bien au format datetime
# df['date_de_vente'] = pd.to_datetime(df['date_de_vente'])
# df['chiffre_affaires'] = df['quantite'] * df['prix_unitaire']

# # Résumés temporels
# daily_revenue = df.resample('D', on='date_de_vente')['chiffre_affaires'].sum().reset_index()
# weekly_revenue = df.resample('W', on='date_de_vente')['chiffre_affaires'].sum().reset_index()
# monthly_revenue = df.resample('ME', on='date_de_vente')['chiffre_affaires'].sum().reset_index()
# year_revenue = df.resample('YE', on='date_de_vente')['chiffre_affaires'].sum().reset_index()

# filtre = st.selectbox("Filtrer par :", ["Jour", "Semaine", "Mois", "Année"])

# if filtre == "Jour":
#     df_filtre = daily_revenue.copy()
#     df_filtre['label'] = df_filtre['date_de_vente'].dt.strftime('%d %b')
# elif filtre == "Semaine":
#     df_filtre = weekly_revenue.copy()
#     df_filtre['label'] = df_filtre['date_de_vente'].dt.strftime('Sem. %W')
# elif filtre == "Mois":
#     df_filtre = monthly_revenue.copy()
#     df_filtre['label'] = df_filtre['date_de_vente'].dt.strftime('%b %Y')
# elif filtre == "Année":
#     df_filtre = year_revenue.copy()
#     df_filtre['label'] = df_filtre['date_de_vente'].dt.strftime('%Y')

# df_filtre.rename(columns={
#     'date_de_vente': 'Période',
#     'chiffre_affaires': "Chiffre d'affaires"
# }, inplace=True)

# total_chiffre_affaire = df_filtre["Chiffre d'affaires"].sum()
# dernier_ca = df_filtre["Chiffre d'affaires"].iloc[-1]


#importation html et css
st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)
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

    import calendar

    # Chargement des données
    data = finance_views.CA_finance
    df_finance = pd.DataFrame(data)

    # Nettoyage
    df_mois = df_finance.dropna(subset=['mois', 'chiffre_affaire_mois', 'annee', 'nom_medicament'])

    # 🔹 Ajouter un numéro de mois pour trier (basé sur noms FR ou EN)
    mois_map = {month: i for i, month in enumerate(calendar.month_abbr) if month}  # {'Jan':1, 'Feb':2,...}
    df_mois['mois_num'] = df_mois['mois'].map(mois_map)

    col1, col2 = st.columns([1, 3])
    with col1:
        filtre = st.selectbox("Afficher par :", ['Mois'])

        # Multiselect années
        annees_dispo = sorted(df_finance['annee'].dropna().unique().astype(int))
        annees_choisies = st.multiselect("Sélectionner les années :", annees_dispo, default=[max(annees_dispo)])

        # Multiselect médicaments
        medicaments_dispo = sorted(df_finance['nom_medicament'].dropna().unique())
        medicaments_choisis = st.multiselect("Sélectionner les médicaments :", medicaments_dispo)

        st.markdown(finance_views.kpis_html, unsafe_allow_html=True)

    with col2:
        # --- Filtrage ---
        if medicaments_choisis:
            df_filtre = df_mois[df_mois['nom_medicament'].isin(medicaments_choisis)]
        else:
            df_filtre = df_mois.groupby(['mois', 'annee', 'mois_num'], as_index=False).agg({
                'chiffre_affaire_mois': 'sum'
            })
            df_filtre['nom_medicament'] = 'Global'

        if annees_choisies:
            df_filtre = df_filtre[df_filtre['annee'].isin(annees_choisies)]

        # --- Affichage par MOIS ---
        if filtre == "Mois" and not df_filtre.empty:
            df_filtre['Année'] = df_filtre['annee'].astype(int)
            df_filtre['Ligne'] = df_filtre['nom_medicament'] + " - " + df_filtre['Année'].astype(str)

            # Tri par numéro de mois
            df_filtre = df_filtre.sort_values(by="mois_num")

            fig = px.line(
                df_filtre,
                x="mois",
                y="chiffre_affaire_mois",
                color="Ligne",
                markers=True,
                title=f"Chiffre d'affaire mensuel - {', '.join(medicaments_choisis) if medicaments_choisis else 'Global'}"
            )

            fig.update_traces(mode="lines+markers")
            fig.update_layout(
                title={'x': 0.5, 'xanchor': 'center'},
                title_font=dict(size=18),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis_title="Mois",
                yaxis_title="Chiffre d'affaire (€)",
                xaxis=dict(categoryorder="array", categoryarray=list(mois_map.keys()))
            )
            st.plotly_chart(fig, use_container_width=True)


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
                'y': 0.90,            # Hauteur du titre (1 = tout en haut)
                'x': 0.5,    # Centre horizontalement
                'xanchor': 'center',
                'yanchor': 'top'
            },
            width=400,  # largeur en pixels (plus réaliste que 50)
            height=350,
            title_font=dict(size=18),
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=80, b=0),
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
                'y': 0.90,            # Hauteur du titre (1 = tout en haut)
                'x': 0.5,             # Centré horizontalement
                'xanchor': 'center',  # Ancre horizontale
                'yanchor': 'bottom'   # Ancre verticale
            },
            width=400,  # largeur en pixels (plus réaliste que 50)
            height=350, # hauteur en pixels
            title_font=dict(size=18),  # Taille du titre
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=80, b=0)  # ✅ Un seul margin, t=100 pour espace
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
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=30, b=0),
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
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=30, b=0),
        )

        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

        # 🔹 Fin de la carte
        st.markdown("</div>", unsafe_allow_html=True)

#Marge benefinaire
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
                    paper_bgcolor="rgba(0,0,0,0)",  
                    plot_bgcolor="rgba(0,0,0,0)",   
                    margin=dict(l=0, r=50, t=30, b=0),
                )

        # Affichage dans Streamlit
        st.plotly_chart(fig)
with st.container():

    col1, col2 = st.columns([1,3])

with col1:
    # 🔹 Style personnalisé
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
    data = finance_views.Evolution_pertes
    df_pertes = pd.DataFrame(data)
    df_pertes.rename(columns={"total_pertes": "Total Perte"}, inplace=True)

    # 🔹 Dictionnaire mois
    mois_dict = {"Jan":1, "Fév":2, "Mar":3, "Avr":4, "Mai":5, "Juin":6,
                 "Juil":7, "Aoû":8, "Sep":9, "Oct":10, "Nov":11, "Déc":12}
    df_pertes['Mois_Num'] = df_pertes['Mois'].map(mois_dict)

    # 🔹 Filtre année
    annees_dispo = sorted(df_pertes['Annee'].unique(), reverse=True)
    annee_selectionnee = st.selectbox("Sélectionner l'année", annees_dispo)

    # 🔹 Préparer les données à afficher (année sélectionnée + précédente si disponible)
    annees_a_afficher = [annee_selectionnee]
    annee_precedente = annee_selectionnee - 1
    if annee_precedente in df_pertes['Annee'].values:
        annees_a_afficher.append(annee_precedente)

    df_graph = df_pertes[df_pertes['Annee'].isin(annees_a_afficher)]

    # 🔹 Pour que X soit toujours Jan -> Déc (même si certains mois manquent)
    mois_order = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
                  "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    df_graph['Mois'] = pd.Categorical(df_graph['Mois'], categories=mois_order, ordered=True)
    df_graph = df_graph.sort_values(['Annee','Mois'])

    with col2:
        # 🔹 Graphique
        fig = px.line(
            df_graph,
            x='Mois',
            y='Total Perte',
            color='Annee',  # Une couleur par année
            markers=True,
            labels={"Total Perte":"Chiffre d'affaire (€)", "Mois":"Mois", "Annee":"Année"}
        )

        # 🔹 Toujours afficher tous les mois sur l'axe X
        fig.update_xaxes(categoryorder='array', categoryarray=mois_order)

        fig.update_layout(
            title=f"📈 Évolution du chiffre d'affaires - {annee_selectionnee} et année précédente",
            font=dict(size=14),
            plot_bgcolor='white'
        )
        fig.update_traces(line=dict(width=3))
        st.plotly_chart(fig, use_container_width=True)
