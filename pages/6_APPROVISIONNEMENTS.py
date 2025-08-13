import pandas as pd
import streamlit as st 
import plotly.express as px
from streamlit.components.v1 import html
from data.mongodb_client import MongoDBClient
from pipelines import pipeline_overview
from views import appro_views

from style import style









# Initialisation
st.set_page_config(page_title="Approvisionnement & Fournisseur", layout="wide")

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
<div class="box">Approvisionnement - Fournisseur</div>
""")

st.markdown(style.custom_css,unsafe_allow_html=True)
st.markdown(style.kpis_style,unsafe_allow_html=True)
if appro_views.overview_collection:
    st.markdown(appro_views.kpis_html,unsafe_allow_html=True)


with st.container():
    col1,col2 = st.columns(2)

    with col1:
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
            paper_bgcolor="rgba(0,0,0,0)",
            height=335,  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=30, r=30, t=30, b=30),
            showlegend=False,
            # xaxis_tickangle=-45
        )

        # Affichage dans Streamlit
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        data = appro_views.Commande_moyen_par_fournisseur
        df_commande_moyen_fourn = pd.DataFrame(data)

        # 🔽 Tri décroissant par nombre moyen de commandes
        df_temps_moyen_fourn = df_commande_moyen_fourn.sort_values(by="Nombre moyen de commandes", ascending=False)

        # 📈 Création du graphique
        fig = px.bar(
            df_commande_moyen_fourn,
            x="Fournisseur", 
            y="Nombre moyen de commandes",
            text="Nombre moyen de commandes",
            color="Nombre moyen de commandes",
            color_continuous_scale=px.colors.sequential.Teal
        )

        # 🎨 Mise en forme
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(
            title={
                'text': "Nombre moyen de commandes par fournisseur",
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Fournisseurs",
            yaxis_title="Nombre moyen de commandes",
            yaxis=dict(range=[0, df_temps_moyen_fourn["Nombre moyen de commandes"].max() + 2]),
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            paper_bgcolor="rgba(0,0,0,0)",
            height=350,  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=30, r=30, t=30, b=30),
        )

        # 🖼️ Affichage dans Streamlit
        st.plotly_chart(fig)


with st.container():
      col1,col2 = st.columns(2)

      with col1:
          # 📊 Création du dataframe
          data = appro_views.Temps_moyen_fournisseur
          df_temps_moyen_fourn = pd.DataFrame(data)

          # 🧹 Renommage et tri
          df_temps_moyen_fourn.rename(columns={"_id": "Fournisseurs", "temps_moyen_livraison": "Temps Moyen Livraison"}, inplace=True)
          df_temps_moyen_fourn = df_temps_moyen_fourn.sort_values(by="Temps Moyen Livraison", ascending=False)

          # 📈 Création du graphique
          fig = px.bar(
              df_temps_moyen_fourn,
              x="Fournisseurs",
              y="Temps Moyen Livraison",
              text="Temps Moyen Livraison",
              color="Temps Moyen Livraison",
              color_continuous_scale=px.colors.sequential.Teal
          )

          # 🎨 Mise en forme
          fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
          fig.update_layout(
              title={
                  'text': "Temps moyen de livraison par fournisseur",
                  'x': 0.5,
                  'xanchor': 'center',
                  'yanchor': 'top'
              },
              xaxis_title="Fournisseurs",
              yaxis_title="Temps Moyen Livraison (jours)",
              yaxis=dict(range=[0, df_temps_moyen_fourn["Temps Moyen Livraison"].max() + 2]),
              uniformtext_minsize=8,
              uniformtext_mode='hide',
              paper_bgcolor="rgba(0,0,0,0)",
              height=350,  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=30, r=30, t=30, b=30),
          )

          # 🖼️ Affichage dans Streamlit
          st.plotly_chart(fig)

      with col2:
          data = appro_views.taux_retard_livraison
          df_taux_retard_livraison = pd.DataFrame(data)
          df_taux_retard_livraison.rename(columns={"fournisseur": "Fournisseurs", "taux_retard": "Taux retard"}, inplace=True)
          df_taux_retard_livraison = df_taux_retard_livraison.sort_values(by="Taux retard", ascending=False)

          # 📈 Création du graphique
          fig = px.bar(
              df_taux_retard_livraison,
              x="Fournisseurs",
              y="Taux retard",
              text="Taux retard",
              color="Taux retard",
              color_continuous_scale=px.colors.sequential.Teal
          )

          # 🎨 Mise en forme
          fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
          fig.update_layout(
              title={
                  'text': "Taux de retard de livraison par fournisseur",
                  'x': 0.5,
                  'xanchor': 'center',
                  'yanchor': 'top'
              },
              xaxis_title="Fournisseurs",
              yaxis_title="Taux de retard (%)",
              yaxis=dict(range=[0, df_taux_retard_livraison["Taux retard"].max() + 5]),
              uniformtext_minsize=8,
              uniformtext_mode='hide',
              paper_bgcolor="rgba(0,0,0,0)",
              height=350,  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=30, r=30, t=30, b=30),
          )

          # 🖼️ Affichage dans Streamlit
          st.plotly_chart(fig)


