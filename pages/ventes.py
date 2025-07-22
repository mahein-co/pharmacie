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

st.markdown("<h2 style='color: green;'>VENTES</h2>", unsafe_allow_html=True)

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
    st.markdown("<h3>📊 Indicateurs clés</h3>", unsafe_allow_html=True)

    # Données d'exemple
    # Exemple de données de ventes
    data = pd.DataFrame({
        'vente_id': [1, 2, 3, 4, 5],
        'montant': [15000, 20000, 12000, 18000, 22000]
    })

    chiffre_affaires_total = data['montant'].sum()
    nombre_ventes = data['vente_id'].nunique()
    panier_moyen = round(chiffre_affaires_total / nombre_ventes, 2)

    # CSS pour les scorecards
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

    # Affichage des 3 scorecards dans des colonnes
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="scorecard">
                <h4>💰 Chiffre d'affaires total</h4>
                <p>{chiffre_affaires_total:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="scorecard">
                <h4>🧺 Panier moyen</h4>
                <p>{f"{panier_moyen:,.0f} MGA"}</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="scorecard">
                <h4>🛒 Nombre de ventes</h4>
                <p>{nombre_ventes:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)



# Données exemples
ventes_mensuelles = pd.DataFrame({
    'Mois': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'],
    'Nombre de ventes': [120, 150, 170, 160, 180, 210]
})

top_vendeurs = pd.DataFrame({
    'Vendeur': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'Ventes': [320, 280, 260, 240, 220]
})

# Conteneur Streamlit
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>Évolution du nombre total de ventes</h3>", unsafe_allow_html=True)
        fig_line = px.line(ventes_mensuelles, x='Mois', y='Nombre de ventes', markers=True,
                           line_shape='linear', color_discrete_sequence=['#2d6a4f'])
        fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.markdown("<h3>Top vendeurs</h3>", unsafe_allow_html=True)
        fig_barh = px.bar(top_vendeurs.sort_values('Ventes'),
                          x='Ventes', y='Vendeur', orientation='h',
                          color='Ventes', color_continuous_scale='greens')
        fig_barh.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig_barh, use_container_width=True)




# Données d'exemple
data_ventes = pd.DataFrame({
    'Médicament': ['Paracétamol', 'Ibuprofène', 'Amoxicilline', 'Aspirine', 'Doliprane', 'Zyrtec'],
    'Quantité vendue': [300, 250, 100, 80, 270, 60]
})

# Top 3 les plus vendus
top_3 = data_ventes.sort_values(by='Quantité vendue', ascending=False).head(3)
top_3['Label'] = top_3['Médicament'] + ' 🔥'

# Top 3 les moins vendus
bottom_3 = data_ventes.sort_values(by='Quantité vendue', ascending=True).head(3)
bottom_3['Label'] = bottom_3['Médicament'] + ' ❄️'

# Affichage
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>Top 3 Médicaments les plus vendus</h3>", unsafe_allow_html=True)
        fig_top = px.bar(top_3.sort_values(by='Quantité vendue'), 
                         x='Quantité vendue', y='Label',
                         orientation='h', color='Quantité vendue',
                         color_continuous_scale='greens')
        fig_top.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown("<h3>Top 3 Médicaments les moins vendus</h3>", unsafe_allow_html=True)
        fig_bottom = px.bar(bottom_3.sort_values(by='Quantité vendue'), 
                            x='Quantité vendue', y='Label',
                            orientation='h', color='Quantité vendue',
                            color_continuous_scale='greens')
        fig_bottom.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bottom, use_container_width=True)





with st.container():
    # Données d'exemple
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    ventes = np.random.poisson(lam=20, size=len(dates))

    df = pd.DataFrame({'date': dates, 'ventes': ventes})
    df['mois'] = df['date'].dt.month
    df['jour_semaine'] = df['date'].dt.day_name()

    # Pivot table : jours en index, mois en colonnes
    pivot_table = df.pivot_table(index='jour_semaine', columns='mois', values='ventes', aggfunc='mean')

    # Trier les jours dans l’ordre
    jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_table = pivot_table.reindex(jours_ordre)

    # Affichage heatmap avec plotly
    fig = px.imshow(
        pivot_table,
        labels=dict(x="Mois", y="Jour de la semaine", color="Moyenne ventes"),
        x=[str(m) for m in pivot_table.columns],  # colonnes mois en string
        y=pivot_table.index,
        color_continuous_scale='YlGnBu',
        aspect="auto"
    )

    fig.update_layout(title="Heatmap saisonnalité des ventes", height=450, width=700)
    st.plotly_chart(fig)












