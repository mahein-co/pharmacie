import pandas as pd
import streamlit as st 
import plotly.express as px
from streamlit.components.v1 import html
from data.mongodb_client import MongoDBClient
from pipelines import pipeline_overview
from views import appro_views











# Initialisation
st.set_page_config(page_title="Approvisionnement & Fournisseur", layout="wide")

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


with st.container():
        
        data = appro_views.Mois_plus_Appro
        df_mois_plus_appro = pd.DataFrame(data)
        # Appliquer le renommage avec inplace=True
        df_mois_plus_appro.rename(columns={"_id": "Mois", "total_approvisionnement": "Total Approvisionnement"}, inplace=True)
        df_mois_plus_appro["Mois"] = pd.to_datetime(df_mois_plus_appro["Mois"])
        df_mois_plus_appro = df_mois_plus_appro.sort_values(by="Mois")

        # CSS pour la carte
        st.markdown("""
            <style>
            .card {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Graphique en ligne sans texte sur les points
        fig = px.line(
            df_mois_plus_appro,
            x="Mois",
            y="Total Approvisionnement",
            markers=True,
            color_discrete_sequence=px.colors.sequential.Plasma
        )

        fig.update_layout(
            xaxis_title="Mois",
            yaxis_title="Total Approvisionnement",
            title={
                'text': "Approvisionnement par mois",
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            title_font=dict(size=18),
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_tickangle=-45
        )

        # Affichage dans Streamlit
        st.plotly_chart(fig, use_container_width=True)


with st.container():
      col1,col2 = st.columns(2)
      


