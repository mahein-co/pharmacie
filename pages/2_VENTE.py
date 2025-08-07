import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
import plotly.express as px
from views import vente_views,dashboard_views
from data.mongodb_client import MongoDBClient 
from pipelines import pipeline_overview

from style import style






# ========== CSS Style ===============
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
<div class="box">Vente</div>
""")


st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)

st.markdown(vente_views.kpis_html, unsafe_allow_html=True)



# ========== LEFT SECTION (Visitors + Graph) ==========
with st.container():
    col1,col2 = st.columns(2)

    
    with col1:
        # Données exemple
        data = vente_views.top_vendeur
        df_top_vendeur = pd.DataFrame(data)
        df_top_vendeur.rename(columns={"_id":"Vendeur","chiffre_affaire":"Chiffre Affaire"}, inplace=True)
        # Trier pour top 3 en montant des ventes
        top_vendeurs = df_top_vendeur.sort_values(by="Chiffre Affaire", ascending=False).head(3)

        # CSS pour la carte
        st.markdown(
            """
            <style>
            .card {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            </style>
            """,
            unsafe_allow_html=True
        )


        # Graphique
        fig = px.bar(
            top_vendeurs,
            x="Chiffre Affaire",
            y="Vendeur",
            orientation='h',
            text="Chiffre Affaire",
            color="Chiffre Affaire",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Top 3 vendeurs"
        )
        fig.update_layout(
            title=dict(
                text="Top 3 vendeurs",# ou autre titre
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            xaxis_title="Montant des ventes",
            yaxis_title="Vendeur",
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=50, b=10)
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
    
        # Données
        data = vente_views.vendeur_non_habilite
        df_vendeur_non_habilite = pd.DataFrame(data)

        # Renommer les colonnes
        df_vendeur_non_habilite.rename(
            columns={"_id": "Vendeur", "chiffre_affaire": "Chiffre Affaire"}, 
            inplace=True
        )

        # Trier les 3 vendeurs non habilités avec le plus de chiffre d'affaires
        top_vendeurs = df_vendeur_non_habilite.sort_values(by="Chiffre Affaire", ascending=False).head(3)

        # CSS personnalisé
        st.markdown(
            """
            <style>
            .card {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        # Graphique Plotly
        fig = px.bar(
            top_vendeurs,
            x="Chiffre Affaire",
            y="Vendeur",
            orientation='h',
            text="Chiffre Affaire",
            color="Chiffre Affaire",  # meilleure lisibilité avec 3 vendeurs
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig.update_layout(
            title=dict(
                text="Top 3 vendeurs non habilités",
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            xaxis_title="Montant des ventes",
            yaxis_title="Vendeur",
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=50, b=10)
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

        # Fermer carte
        st.markdown('</div>', unsafe_allow_html=True)

with st.container():
    col1,col2 = st.columns(2)

    with col1:
        # Données exemple
        data = vente_views.top_medicaments
        df_top_medicaments = pd.DataFrame(data)
        df_top_medicaments.rename(columns={"_id": "Médicaments","quantite_totale_vendue":"quantite totale vendue"}, inplace=True)

        # Trier pour top 3 en montant des ventes
        top_medicaments = df_top_medicaments.sort_values(by="quantite totale vendue", ascending=False).head(3)

        # CSS pour la carte
        st.markdown(
            """
            <style>
            .card {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Graphique
        fig = px.bar(
        top_medicaments,
        x="quantite totale vendue",
        y="Médicaments",
        orientation='h',
        text="quantite totale vendue",
        color="quantite totale vendue",
        color_continuous_scale=px.colors.sequential.Plasma,
        title="Top 3 médicaments"
    )

        fig.update_layout(
            title=dict(
                text="Top 3 médicaments",
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            xaxis_title="Quantité vendue",
            yaxis_title="Médicaments",
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=50, b=10)
        )

        fig.update_yaxes(autorange="reversed")
        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

            # Fermer le div card
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        data = vente_views.Medoc_moins_vendus
        df_Medoc_moins = pd.DataFrame(data)
        
        # Renommer les colonnes
        df_Medoc_moins.rename(
            columns={"_id": "Médicaments", "quantite_totale_vendue": "Quantite Totale Vendue"},
            inplace=True
        )

        # Trier pour obtenir les 3 moins vendus
        Medoc_moins = df_Medoc_moins.sort_values(by="Quantite Totale Vendue", ascending=True).head(3)

        # CSS pour la carte
        st.markdown(
            """
            <style>
            .card {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Graphique Plotly
        fig = px.bar(
            Medoc_moins,
            x="Quantite Totale Vendue",
            y="Médicaments",
            orientation='h',
            text="Quantite Totale Vendue",
            color="Quantite Totale Vendue",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Médicaments Moins Vendus"
        )

        fig.update_layout(
            title=dict(
                text="Médicaments Moins Vendus",
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            xaxis_title="Quantité vendue",
            yaxis_title="Médicaments",
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=50, b=10)
        )

        fig.update_yaxes(autorange="reversed")
        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)

        # Fermeture du div .card
        st.markdown('</div>', unsafe_allow_html=True)

    
