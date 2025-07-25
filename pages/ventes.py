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
from pipelines import pipelines_ventes
from views import dashboard_views

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
vente_collection = MongoDBClient(collection_name="vente")
employe_collection = MongoDBClient(collection_name="employe")
medicament_collection = MongoDBClient(collection_name="medicament")

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

    #2--nombres de ventes
    nombre_ventes = vente_collection.count_distinct_agg(field_name="id_vente")

    #panier_moyen
    panier_moyen =  round(dashboard_views.total_chiffre_affaire / nombre_ventes, 2)
    
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
                <h4>💰 Chiffre d'affaires total(MGA)</h4>
                <p>{dashboard_views.total_chiffre_affaire}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="scorecard">
                <h4>🧺 Panier moyen(MGA)</h4>
                <p>{panier_moyen}</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="scorecard">
                <h4>🛒 Nombre de ventes</h4>
                <p>{nombre_ventes}</p>
            </div>
        """, unsafe_allow_html=True)


# Données exemples
ventes_mensuelles = pd.DataFrame({
    'Mois': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'],
    'Nombre de ventes': [120, 150, 170, 160, 180, 210]
})


# Top 3 vendeur 
top_3_vendeur = vente_collection.make_specific_pipeline(pipeline=pipelines_ventes.pipeline_top_vendeurs, title="Recuperation de top vendeur 3")

# Vendeur non habilite
vendeur_non_habilite = vente_collection.make_specific_pipeline(pipeline=pipelines_ventes.pipeline_vendeurs_non_habilite, title="Recuperation de vendeurs non habilités")

# Medicaments les plus vendus
medicaments_plus_vendus = vente_collection.make_specific_pipeline(
    pipeline=pipelines_ventes.pipeline_medicaments_plus_vendus,
    title="Recuperation medicaments plus vendus"
)
# Medicaments les moins vendus
medicaments_moins_vendus = vente_collection.make_specific_pipeline(
    pipeline=pipelines_ventes.pipeline_medicaments_moins_vendus,
    title="Recuperation medicaments moins vendus"
)

# Medicament le plus cher
medicaments_plus_cher = medicament_collection.make_specific_pipeline(
    pipeline=pipelines_ventes.pipeline_medicament_plus_cher,
    title="Recuperation de medicament le plus cher"
)

print("medicaments_plus_cher: ", medicaments_plus_cher)

# Medicament le plus cher
medicaments_moins_cher = medicament_collection.make_specific_pipeline(
    pipeline=pipelines_ventes.pipeline_medicament_moins_cher,
    title="Recuperation de medicament le moins cher"
)
print("medicaments_moins_cher: ", medicaments_moins_cher)

# Medicament le plus rentable
medicament_plus_rentable = medicament_collection.make_specific_pipeline(
    pipeline=pipelines_ventes.pipeline_medicament_plus_rentable,
    title="Recuperation de medicament le plus rentable"
)
print("medicament_plus_rentable: ", medicament_plus_rentable)


# Medicament le moins rentable
medicament_moins_rentable = medicament_collection.make_specific_pipeline(
    pipeline=pipelines_ventes.pipeline_medicament_moins_rentable,
    title="Recuperation de medicament le moins rentable"
)
print("medicament_moins_rentable: ", medicament_moins_rentable)


# Medicament le moins cher 

# Conteneur Streamlit
with st.container():
    col1, col2 = st.columns(2)

    # with col1:
    #     st.markdown("<h3>Évolution du nombre total de ventes</h3>", unsafe_allow_html=True)
    #     fig_line = px.line(ventes_mensuelles, x='Mois', y='Nombre de ventes', markers=True,
    #                        line_shape='linear', color_discrete_sequence=['#2d6a4f'])
    #     fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    #     st.plotly_chart(fig_line, use_container_width=True)

    with col1:
        st.markdown("<h3>Top vendeurs</h3>", unsafe_allow_html=True)
        fig_barh = px.bar(vendeur_non_habilite[-3:],
                          x='total_quantite_vendue', y='nom', orientation='h',
                          color='total_quantite_vendue', color_continuous_scale='reds')
        fig_barh.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig_barh, use_container_width=True)

    with col2:
        st.markdown("<h3>Top vendeurs</h3>", unsafe_allow_html=True)
        fig_barh = px.bar(top_3_vendeur,
                          x='total_quantite_vendue', y='nom', orientation='h',
                          color='total_quantite_vendue', color_continuous_scale='greens')
        fig_barh.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig_barh, use_container_width=True)




# Données d'exemple
# data_ventes = pd.DataFrame({
#     'Médicament': ['Paracétamol', 'Ibuprofène', 'Amoxicilline', 'Aspirine', 'Doliprane', 'Zyrtec'],
#     'Quantité vendue': [300, 250, 100, 80, 270, 60]
# })

# Top 3 les plus vendus
# top_3 = data_ventes.sort_values(by='Quantité vendue', ascending=False).head(3)
# top_3['Label'] = top_3['Médicament'] + ' 🔥'

# # Top 3 les moins vendus
# bottom_3 = data_ventes.sort_values(by='Quantité vendue', ascending=True).head(3)
# bottom_3['Label'] = bottom_3['Médicament'] + ' ❄️'


# Affichage
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>Top 3 Médicaments les plus vendus</h3>", unsafe_allow_html=True)
        fig_top = px.bar(medicaments_plus_vendus, 
                         x='quantite_totale_vendue', y='nom',
                         orientation='h', color='quantite_totale_vendue',
                         color_continuous_scale='greens')
        fig_top.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown("<h3>Top 3 Médicaments les moins vendus</h3>", unsafe_allow_html=True)
        fig_bottom = px.bar(medicaments_moins_vendus, 
                            x='quantite_totale_vendue', y='nom',
                            orientation='h', color='quantite_totale_vendue',
                            color_continuous_scale='reds')
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












