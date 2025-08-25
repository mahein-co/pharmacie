import pandas as pd
import streamlit as st 
import plotly.express as px
from streamlit.components.v1 import html
from data.mongodb_client import MongoDBClient
from pipelines import pipeline_overview
from views import appro_views,dashboard_views
from datetime import date

from style import style





#========= importation style ==============
st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)
st.markdown(style.button_style, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.sidebar.image("assets/images/logoMahein.png", caption="", use_container_width=True)



# Initialisation
st.set_page_config(page_title="Approvisionnement & Fournisseur", layout="wide")
col_title, col_empty, col_filter = st.columns([3, 1, 2])
with col_title:
    html("""
    <style>
        @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
        
    .box {
        color: #0A9548;
        font-family: 'Dancing Script', cursive;
        font-size: 45px;
        margin-top:-1rem;
    }
        
    </style>
    <div class="box">Approvisionnements - Fournisseurs</div>
    """)


# GLOBAL VARIABLES ------------------------------------------------
TODAY = date.today()
date_debut = dashboard_views.first_date_vente if dashboard_views.first_date_vente else TODAY
date_fin = TODAY



# FILTRE DATE -------------------------------------------------
with col_filter:
    col1,col2 = st.columns([3,2])
    if "date_range" not in st.session_state:
        st.session_state.date_range = None

    with col1:
        st.session_state.date_range = st.date_input("CHOISISSEZ 02 DATES", value=(date_debut, TODAY))
    
    with col2:
        apply_button = st.button("Appliquer");



if appro_views.overview_collection:
    st.markdown(appro_views.kpis_html,unsafe_allow_html=True)


with st.container():
        # --- Données ---
        data = appro_views.Mois_plus_Appro
        df = pd.DataFrame(data)

        # --- Ordre des mois ---
        mois_order = ["Janv", "Fév", "Mars", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]
        df["Mois"] = pd.Categorical(df["Mois"], categories=mois_order, ordered=True)

        # --- Sélection des années ---
        selected_years = st.multiselect("Sélectionner Année", sorted(df["Année"].unique()))

        # --- Filtrage par année ---
        df_filtered = df.copy()
        if selected_years:
            df_filtered = df_filtered[df_filtered["Année"].isin(selected_years)]
        else:
            # Cas par défaut : total global par année
            df_filtered = df.groupby(["Année", "Mois"], as_index=False)["total_approvisionnement"].sum()

        # --- Supprimer les mois après le dernier mois avec valeur ---
        def couper_fin_zero(group):
            dernier_mois = group.loc[group["total_approvisionnement"] > 0, "Mois"].max()
            return group[group["Mois"] <= dernier_mois]

        df_filtered = df_filtered.groupby("Année", group_keys=False).apply(couper_fin_zero)

        # --- Tri par année puis par mois ---
        df_filtered = df_filtered.sort_values(["Année", "Mois"])

        # --- CSS pour la carte ---
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

        # --- Graphique ---
        fig = px.line(
            df_filtered,
            x="Mois",
            y="total_approvisionnement",
            color="Année",
            markers=True
        )

        fig.update_layout(
            title="Évolution de l’approvisionnement par mois",
            xaxis_title="Mois",
            yaxis_title="Total Approvisionnement",
            xaxis=dict(categoryorder="array", categoryarray=mois_order),
            hovermode="x unified",
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=30, r=30, t=30, b=30),

        )

        st.plotly_chart(fig, use_container_width=True)


with st.container():
    col1,col2,col3 = st.columns(3)

    with col1:
          # 📊 Création du dataframe
          data = appro_views.Temps_moyen_fournisseur
          df_temps_moyen_fourn = pd.DataFrame(data)

          # 🧹 Renommage et tri
          df_temps_moyen_fourn.rename(columns={"_id": "Fournisseurs", "temps_moyen_livraison": "Temps"}, inplace=True)
          df_temps_moyen_fourn = df_temps_moyen_fourn.sort_values(by="Temps", ascending=False)

          # 📈 Création du graphique
          fig = px.bar(
              df_temps_moyen_fourn,
              x="Fournisseurs",
              y="Temps",
              text="Temps",
              color="Temps",
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
              yaxis=dict(range=[0, df_temps_moyen_fourn["Temps"].max() + 2]),
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
          df_taux_retard_livraison.rename(columns={"fournisseur": "Fournisseurs", "taux_retard": "Taux"}, inplace=True)
          df_taux_retard_livraison = df_taux_retard_livraison.sort_values(by="Taux", ascending=False)

          # 📈 Création du graphique
          fig = px.bar(
              df_taux_retard_livraison,
              x="Fournisseurs",
              y="Taux",
              text="Taux",
              color="Taux",
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
              yaxis=dict(range=[0, df_taux_retard_livraison["Taux"].max() + 5]),
              uniformtext_minsize=8,
              uniformtext_mode='hide',
              paper_bgcolor="rgba(0,0,0,0)",
              height=350,  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=30, r=30, t=30, b=30),
          )

          # 🖼️ Affichage dans Streamlit
          st.plotly_chart(fig)

    with col3:
            data = appro_views.Commande_moyen_par_fournisseur
            df_commande_moyen_fourn = pd.DataFrame(data)
            df_commande_moyen_fourn.rename(columns={"Nombre moyen de commandes": "Nombre"}, inplace=True)
            # 🔽 Tri décroissant par nombre moyen de commandes
            df_temps_moyen_fourn = df_commande_moyen_fourn.sort_values(by="Nombre", ascending=False)

            # 📈 Création du graphique
            fig = px.bar(
                df_commande_moyen_fourn,
                x="Fournisseur", 
                y="Nombre",
                text="Nombre",
                color="Nombre",
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
                yaxis=dict(range=[0, df_temps_moyen_fourn["Nombre"].max() + 2]),
                uniformtext_minsize=8,
                uniformtext_mode='hide',
                paper_bgcolor="rgba(0,0,0,0)",
                height=350,  
                plot_bgcolor="rgba(0,0,0,0)",   
                margin=dict(l=30, r=30, t=30, b=30),
            )

            # 🖼️ Affichage dans Streamlit
            st.plotly_chart(fig)

from dashbot.chat_approvisionnement import create_chatbot

qa = create_chatbot()

# Préparation des données 
total_approvisionnement = "\n".join([f"{row['Mois']}: {row['Année']}: {row['total_approvisionnement']}" for _, row in df_filtered.iterrows()])
temps_moyen_livraison = "\n".join([f"{row['Fournisseurs']}: {row['Temps']}" for _, row in df_temps_moyen_fourn.iterrows()])
taux_retard_livraison = "\n".join([f"{row['Fournisseurs']}: {row['Taux']}" for _, row in df_taux_retard_livraison.iterrows()])
Commande_moyen_fourn =  "\n".join([f"{row['Fournisseur']}: {row['Nombre']}" for _, row in df_commande_moyen_fourn.iterrows()])

prompt = f"""
Voici les données des approvisionnements :

Total approvisionnement :
{total_approvisionnement}

Temps moyen de livraison par fournisseur :
{temps_moyen_livraison}

Nombre moyen de commandes par fournisseur :
{Commande_moyen_fourn}
"""

# Chatbot interactif
st.title("💬 Chatbot Analyse des employés")

if "messages_employe" not in st.session_state:
    st.session_state.messages_employe = []

for msg in st.session_state.messages_employe:
    st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input("Posez une question sur les employés"):
    st.session_state.messages_employe.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    # On combine la question de l’utilisateur avec les données préparées
    full_prompt = f"{prompt}\n\nQuestion de l'utilisateur : {question}"
    response = qa.run(full_prompt)

    st.session_state.messages_employe.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
