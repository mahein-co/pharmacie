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




# fourniseurs


st.markdown("<h2 style='color: green;'>Approvisionnements & Fournisseurs</h2>", unsafe_allow_html=True)

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




with st.container():

    # Valeurs fictives (à remplacer par tes vraies données)
    nombre_approvisionnements = 154
    temps_moyen_livraison = 3.4  # en jours
    commandes_par_fournisseur = 12.7
    Nombre_total_fourniseurs = 200

    # Titre de la section
    st.markdown("<h3>Indicateurs clés d'approvisionnement</h3>", unsafe_allow_html=True)

    # 3 colonnes pour les 3 scorecards
    col1, col2, col3,col4 = st.columns(4)

    # Style de scorecard (fonction pour réutiliser)
    def render_scorecard(title, value, icon, border_color):
        st.markdown(
            f"""
            <div style="
                background-color: #1e1e28;
                padding: 1rem 1.5rem;
                border-left: 5px solid {border_color};
                border-radius: 12px;
                color: white;
                font-family: 'Segoe UI', sans-serif;
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                height: 100%;
            ">
                <div style="font-size: 0.9rem; margin-bottom: 0.3rem;">
                    <span style="vertical-align: middle; margin-right: 5px;">{icon}</span> {title}
                </div>
                <div style="font-size: 1.8rem; font-weight: bold;">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Affichage dans chaque colonne
    with col1:
        render_scorecard(
            title="Nombre total d’approvisionnements",
            value=nombre_approvisionnements,
            icon="📦",
            border_color="#2dc653"
        )

    with col2:
        render_scorecard(
            title="Temps moyen de livraison (jours)",
            value=f"{temps_moyen_livraison:.1f}",
            icon="⏱️",
            border_color="#52b788"
        )

    with col3:
        render_scorecard(
            title="commandes moyen par fournisseur",
            value=f"{commandes_par_fournisseur:.1f}",
            icon="🤝",
            border_color="#40916c"
        )
    
    with col4:
        render_scorecard(
            title="Total fournisseur",
            value=f"{Nombre_total_fourniseurs:.1f}",
            icon="🤝",
            border_color="#40916c"
        )


# Données fictives
data_livraison = pd.DataFrame({
    'Fournisseur': ['PharmaPlus', 'MedExpress', 'BioSanté', 'PharmaCare'],
    'Temps moyen (jours)': [2.5, 4.1, 3.2, 5.0],
    'Livraisons en retard': [3, 7, 4, 9]
})

# Couleur verte pharmacie
couleur_vert = "#52b788"

with st.container():
    col1, col2 = st.columns(2)

    # Diagramme 1 : Temps moyen
    with col1:
        st.markdown("<h4>Temps moyen de livraison par fournisseur</h4>",unsafe_allow_html=True)

        fig1 = px.bar(
            data_livraison,
            x='Fournisseur',
            y='Temps moyen (jours)',
            text='Temps moyen (jours)',
            color_discrete_sequence=[couleur_vert]
        )

        fig1.update_traces(texttemplate='%{text:.1f} j', textposition='outside')
        fig1.update_layout(
            yaxis_title="Jours",
            xaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            height=400,
            margin=dict(t=10, b=10)
        )

        st.plotly_chart(fig1, use_container_width=True)

    # Diagramme 2 : Livraisons en retard
    with col2:
        st.markdown("<h4>Nombre de livraisons en retard par fournisseur</h4>",unsafe_allow_html=True)

        fig2 = px.bar(
            data_livraison,
            x='Fournisseur',
            y='Livraisons en retard',
            text='Livraisons en retard',
            color_discrete_sequence=["#40916c"]
        )

        fig2.update_traces(texttemplate='%{text}', textposition='outside')
        fig2.update_layout(
            yaxis_title="Livraisons en retard",
            xaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            height=400,
            margin=dict(t=10, b=10)
        )

        st.plotly_chart(fig2, use_container_width=True)


with st.container():

    
    # Exemple de données fictives
    data_commandes = pd.DataFrame({
        'Fournisseur': ['Fournisseur A', 'Fournisseur B', 'Fournisseur C', 'Fournisseur D'],
        'Nombre Commandes': [120, 90, 150, 100]
    })

    data_approvisionnements = pd.DataFrame({
        'Mois': pd.date_range(start='2024-01-01', periods=12, freq='M'),
        'Approvisionnements': [100, 110, 130, 120, 140, 180, 170, 160, 190, 200, 210, 230]
    })


    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h3>Nombre moyen de commandes par fournisseur</h3>", unsafe_allow_html=True)

            # Calcul du nombre moyen de commandes
            moyenne = data_commandes["Nombre Commandes"].mean()
            data_commandes["Moyenne"] = moyenne

            fig_bar = px.bar(
                data_commandes,
                x='Fournisseur',
                y='Nombre Commandes',
                color='Fournisseur',
                text='Nombre Commandes',
                title="Commandes par Fournisseur"
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            
            st.markdown("<h3>Approvisionnements mensuels</h3>", unsafe_allow_html=True)

            # Filtre de mois
            mois_selectionne = st.selectbox(
                "Choisissez un mois pour surligner",
                options=data_approvisionnements['Mois'].dt.strftime('%B %Y')
            )

            # Line chart
            fig_line = px.line(
                data_approvisionnements,
                x='Mois',
                y='Approvisionnements',
                markers=True,
                title="Évolution des approvisionnements par mois"
            )

            # Ajouter un point mis en valeur
            mois_dt = pd.to_datetime(mois_selectionne)
            if mois_dt in data_approvisionnements['Mois'].values:
                valeur = data_approvisionnements.loc[data_approvisionnements['Mois'] == mois_dt, 'Approvisionnements'].values[0]
                fig_line.add_scatter(x=[mois_dt], y=[valeur], mode='markers+text',
                                    marker=dict(color='red', size=12),
                                    text=["Sélectionné"], textposition="top center")

            st.plotly_chart(fig_line, use_container_width=True)
































