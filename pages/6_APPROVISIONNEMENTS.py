import pandas as pd
import streamlit as st 
from streamlit.components.v1 import html
from data.mongodb_client import MongoDBClient
from pipelines import pipeline_overview
from views import appro_views











# Initialisation
st.set_page_config(page_title="EMPLOYE", layout="wide")

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
<div class="box">Approvisionnement & Fournisseur</div>
""")

st.markdown(appro_views.custom_css,unsafe_allow_html=True)
st.markdown(appro_views.kpis_style,unsafe_allow_html=True)
if appro_views.overview_collection:
    st.markdown(appro_views.kpis_html,unsafe_allow_html=True)
