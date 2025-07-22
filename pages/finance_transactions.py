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



# Exemple de données de vente
import streamlit as st
import pandas as pd
import numpy as np

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

# --------------------
# CSS style metric
# --------------------
st.markdown("""
<style>
.metric-box {
    background-color: #1e1e26;
    border-left: 5px solid #00cc66;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
    color: white;
    box-shadow: 0 0 4px rgba(0,0,0,0.2);
}
.metric-label {
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --------------------
# Affichage
# --------------------
with st.container():
    st.markdown("<h3>💰 Chiffre d'Affaire</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">💼 Total Chiffre d'Affaire</div>
                <div class="metric-value">{total_ca:,.0f} Ar</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">📅 CA ({filtre} Actuel)</div>
                <div class="metric-value">{dernier_val:,.0f} Ar</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.line_chart(data=data_grouped.set_index('label')['montant'], use_container_width=True)


# --------------------
# Données exemple
# --------------------
data = pd.DataFrame({
    'Médicament': ['Paracétamol', 'Ibuprofène', 'Amoxicilline', 'Aspirine', 'Doliprane'],
    'Ventes': [150000, 90000, 120000, 70000, 50000],
    'Coût': [100000, 60000, 80000, 40000, 30000]
})

data['Marge'] = data['Ventes'] - data['Coût']
data['Marge %'] = round((data['Marge'] / data['Ventes']) * 100, 2)

marge_moyenne = round(data['Marge %'].mean(), 2)

# Palette verte dégradée pharmacie
palette_vert_pharmacie = [ 
    "#1b4332", # vert foncé
    "#2d6a4f",
    "#40916c",
    "#74c69d", 
    "#b7e4c7"  # vert clair
]
# --------------------
# Interface
# --------------------
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>📉 Marge bénéficiaire moyenne</h3>", unsafe_allow_html=True)
        st.markdown(f"**💰 {marge_moyenne} %**")

        # Données entonnoir 2D
        funnel_data = pd.DataFrame({
            'Étape': ['Ventes', 'Coûts', 'Marge'],
            'Montant': [data['Ventes'].sum(), data['Coût'].sum(), data['Marge'].sum()]
        })

        fig_funnel = px.funnel(
            funnel_data,
            y='Étape',
            x='Montant',
            color_discrete_sequence=["#00cc66"]
        )

        fig_funnel.update_traces(marker_line_width=0)  # pas de bordure
        fig_funnel.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False
        )

        st.plotly_chart(fig_funnel, use_container_width=True)

    with col2:
        st.markdown("<h3>💸 Médicaments qui rapportent le plus</h3>", unsafe_allow_html=True)

        fig_pie = px.pie(
            data,
            names='Médicament',
            values='Marge',
            title='Répartition par bénéfice',
            hole=0,
            color_discrete_sequence=palette_vert_pharmacie
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# Exemple de données
data = pd.DataFrame({
    'Medicament': ['Paracetamol', 'Ibuprofene', 'Amoxicilline', 'Aspirine', 'Ceftriaxone', 'Diclofenac', 'Metformine'],
    'Marge': [25, 15, 40, 10, 35, 20, 5]
})

# Top 3 médicaments avec la marge la plus élevée
top3_max = data.nlargest(3, 'Marge')

# Top 3 médicaments avec la marge la plus faible
top3_min = data.nsmallest(3, 'Marge')

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>Top 3 Médicaments avec la plus forte marge</h3>", unsafe_allow_html=True)
        fig_max = px.bar(
            top3_max,
            x='Medicament',
            y='Marge',
            color='Marge',
            color_continuous_scale='Greens',
            text='Marge',
            range_y=[0, data['Marge'].max() + 10]
        )
        fig_max.update_traces(textposition='outside')
        fig_max.update_layout(yaxis_title="Marge (%)", xaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(fig_max, use_container_width=True)

    with col2:
        st.markdown("<h3>Top 3 Médicaments avec la plus faible marge</h3>", unsafe_allow_html=True)
        fig_min = px.bar(
            top3_min,
            x='Medicament',
            y='Marge',
            color='Marge',
            color_continuous_scale='Reds',
            text='Marge',
            range_y=[0, data['Marge'].max() + 10]
        )
        fig_min.update_traces(textposition='outside')
        fig_min.update_layout(yaxis_title="Marge (%)", xaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(fig_min, use_container_width=True)

with st.container():
    # Exemple de données : dates et pertes totales (en valeur monétaire)
    data = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=12, freq='M'),
        'Pertes_totales': [500, 700, 650, 800, 900, 1200, 1100, 1150, 1300, 1400, 1500, 1600]
    })

    st.markdown("<h3>Évolution totale des pertes dues aux médicaments invendus ou abîmés</h3>", unsafe_allow_html=True)

    fig = px.line(
        data,
        x='Date',
        y='Pertes_totales',
        markers=True,
        labels={'Pertes_totales': 'Pertes totales (€)', 'Date': 'Date'}
    )

    st.plotly_chart(fig, use_container_width=True)