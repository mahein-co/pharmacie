import streamlit as st
import pandas as pd
import numpy as np
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
