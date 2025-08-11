import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
from views import employe_views, dashboard_views
from data.mongodb_client import MongoDBClient
from pipelines import pipelines_employe

from style import style









# Initialisation
st.set_page_config(page_title="EMPLOYE", layout="wide")

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
<div class="box">Employés</div>
""")

#importation html et css
st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)

if employe_views.employe_collection:
  st.markdown(employe_views.kpis_html, unsafe_allow_html=True)


with st.container():
    col1,col2 = st.columns(2)

    with col1:
      #DataFrame
      data = employe_views.effectif_par_employe_categorie
      df_eff_categorie = pd.DataFrame(data)
      df_eff_categorie.rename(columns={"_id":"Catégorie"}, inplace=True)


      # Graphique camembert avec Plotly Express
      fig = px.pie(
          df_eff_categorie,
          names='Catégorie',
          values='Effectif',
          hole=0.4
      )

      # Centrage du titre avec xanchor
      fig.update_layout(
          title=dict(
              text="Répartition par categories",
              x=0.5,
              xanchor='center',
              font=dict(size=18)
          ),
          paper_bgcolor="rgba(0,0,0,0)",  
          plot_bgcolor="rgba(0,0,0,0)",   
          margin=dict(l=0, r=0, t=30, b=0),
      )

      # Affichage dans Streamlit
      st.plotly_chart(fig, use_container_width=True)

    with col2:
      #DataFrame
      data = employe_views.effectif_par_employe_fonction
      df_eff_categorie = pd.DataFrame(data)
      df_eff_categorie.rename(columns={"_id":"Fonction"}, inplace=True)


      # Graphique camembert avec Plotly Express
      fig = px.pie(
          df_eff_categorie,
          names='Fonction',
          values='Effectif',
          hole=0.4
      )

      # Centrage du titre avec xanchor
      fig.update_layout(
          title=dict(
              text="Répartition par Fonction",
              x=0.5,
              xanchor='center',
              font=dict(size=18)
          ),
          paper_bgcolor="rgba(0,0,0,0)",  
          plot_bgcolor="rgba(0,0,0,0)",   
          margin=dict(l=0, r=0, t=30, b=0),
      )

      # Affichage dans Streamlit
      st.plotly_chart(fig, use_container_width=True)



