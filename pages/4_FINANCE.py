import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
from views import finance_views
import calendar

from style import style


# Initialisation
st.set_page_config(page_title="FINANCE", layout="wide")

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
<div class="box">Finance</div>
""")

# importation html et css
st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)

# FILTRES ------------------------------------
with st.container():
    st.markdown("""
    <style>
        .custom-card {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)

    

    # Chargement des données
    data = finance_views.CA_finance
    df_finance = pd.DataFrame(data)

    # Nettoyage
    df_mois = df_finance.dropna(subset=['mois', 'chiffre_affaire_mois', 'annee', 'nom_medicament'])

    # 🔹 Ajouter un numéro de mois pour trier (basé sur noms FR ou EN)
    mois_map = {month: i for i, month in enumerate(calendar.month_abbr) if month}  # {'Jan':1, 'Feb':2,...}
    df_mois['mois_num'] = df_mois['mois'].map(mois_map)

    col1, col2 = st.columns(2)

    with col1:
        # Multiselect médicaments
        medicaments_dispo = sorted(df_finance['nom_medicament'].dropna().unique())
        medicaments_choisis = st.multiselect("Sélectionner les médicaments :", medicaments_dispo)

    with col2:
         # Multiselect années
        annees_dispo = sorted(df_finance['annee'].dropna().unique().astype(int))
        annees_choisies = st.multiselect("Sélectionner les années :", annees_dispo, default=[max(annees_dispo)])

    # with col4:
    #     st.markdown(finance_views.kpis_html, unsafe_allow_html=True)


    # with col4:
# 🔹 Style personnalisé
    st.markdown("""
        <style>
            .custom-card {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 🔹 Données
    data = finance_views.Evolution_pertes
    df_pertes = pd.DataFrame(data)
    df_pertes.rename(columns={"total_pertes": "Total Perte"}, inplace=True)

    # 🔹 Dictionnaire mois
    mois_dict = {"Jan":1, "Fév":2, "Mar":3, "Avr":4, "Mai":5, "Juin":6,
                "Juil":7, "Aoû":8, "Sep":9, "Oct":10, "Nov":11, "Déc":12}
    df_pertes['Mois_Num'] = df_pertes['Mois'].map(mois_dict)

    # 🔹 Filtre année
    annees_dispo = sorted(df_pertes['Annee'].unique(), reverse=True)
    annee_selectionnee = annees_choisies[-1]  if annees_choisies else max(annees_dispo) # st.selectbox("Sélectionner l'année", annees_dispo)
    # 🔹 Préparer les données à afficher (année sélectionnée + précédente si disponible)
    annees_a_afficher = [annee_selectionnee]
    annee_precedente = annee_selectionnee - 1
    if annee_precedente in df_pertes['Annee'].values:
        annees_a_afficher.append(annee_precedente)

    df_graph = df_pertes[df_pertes['Annee'].isin(annees_a_afficher)]

    # 🔹 Pour que X soit toujours Jan -> Déc (même si certains mois manquent)
    mois_order = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
                "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    df_graph['Mois'] = pd.Categorical(df_graph['Mois'], categories=mois_order, ordered=True)
    df_graph = df_graph.sort_values(['Annee','Mois'])

# CHIFFRE D'AFFAIRE ------------------------------------
with st.container():
        # --- Filtrage ---
        if medicaments_choisis:
            df_filtre = df_mois[df_mois['nom_medicament'].isin(medicaments_choisis)]
        else:
            df_filtre = df_mois.groupby(['mois', 'annee', 'mois_num'], as_index=False).agg({
                'chiffre_affaire_mois': 'sum'
            })
            df_filtre['nom_medicament'] = 'Année'

        if annees_choisies:
            df_filtre = df_filtre[df_filtre['annee'].isin(annees_choisies)]

        # --- Affichage par MOIS ---
        if not df_filtre.empty:
            df_filtre['Année'] = df_filtre['annee'].astype(int)
            df_filtre['Ligne'] = df_filtre['nom_medicament'] + " - " + df_filtre['Année'].astype(str)

            # Tri par numéro de mois
            df_filtre = df_filtre.sort_values(by="mois_num")

            fig = px.line(
                df_filtre,
                x="mois",
                y="chiffre_affaire_mois",
                color="Ligne",
                markers=True,
                title=f"Chiffre d'affaire mensuel - {', '.join(medicaments_choisis) if medicaments_choisis else 'Année'}"
            )

            fig.update_traces(mode="lines+markers")
            fig.update_layout(
                title={'x': 0.5, 'xanchor': 'center'},
                title_font=dict(size=18),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis_title="Mois",
                height=335,
                yaxis_title="Chiffre d'affaire (Ar)",
                xaxis=dict(categoryorder="array", categoryarray=list(mois_map.keys()))
            )
            st.plotly_chart(fig, use_container_width=True)



# MEDICAMENT QUI RAPPORTENT MOINS ET PLUS -------------------
with st.container():
    col1,col2 = st.columns(2)

    with col1:
        data = finance_views.medoc_rapporte_moins
        df_rapporte_moins = pd.DataFrame(data)
        df_rapporte_moins.rename(columns={"_id" : "Médicaments", "total_gain" : "Total Gain"},inplace=True)

        st.markdown("""
            <style>
                .custom-card {
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 30px;
                }
            </style>
        """, unsafe_allow_html=True)

        # 🔸 Graphique camembert
        fig = px.pie(
            df_rapporte_moins,
            names="Médicaments",
            values="Total Gain",
            hole=0.4  # Donut style
        )

        # ✅ Mise à jour du layout pour centrer le titre proprement
        fig.update_layout(
            title={
                'text': "Médicaments rapportent moins",
                'y': 0.90,            # Hauteur du titre (1 = tout en haut)
                'x': 0.5,    # Centre horizontalement
                'xanchor': 'center',
                'yanchor': 'top'
            },
            width=400,  # largeur en pixels (plus réaliste que 50)
            height=335,
            title_font=dict(size=18),
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=80, b=0),
        )

        # 🎯 Affichage dans Streamlit
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        data = finance_views.medoc_rapporte_plus
        df_rapporte_plus = pd.DataFrame(data)
        df_rapporte_plus.rename(columns={"_id" : "Médicaments", "total_gain" : "Total Gain"},inplace=True)

        st.markdown("""
            <style>
                .custom-card {
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 30px;
                }
            </style>
        """, unsafe_allow_html=True)

        # 🔸 Graphique camembert
        fig = px.pie(
            df_rapporte_plus,
            names="Médicaments",
            values="Total Gain",
            hole=0.4  # Donut style
        )

        # ✅ Mise à jour du layout pour centrer le titre proprement
        fig.update_layout(
            title={
                'text': "Médicaments rapportent plus",
                'y': 0.90,            # Hauteur du titre (1 = tout en haut)
                'x': 0.5,             # Centré horizontalement
                'xanchor': 'center',  # Ancre horizontale
                'yanchor': 'bottom'   # Ancre verticale
            },
            width=400,  # largeur en pixels (plus réaliste que 50)
            height=335, # hauteur en pixels
            title_font=dict(size=18),  # Taille du titre
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=80, b=0)  # ✅ Un seul margin, t=100 pour espace
        )

        # 🎯 Affichage dans Streamlit
        st.plotly_chart(fig, use_container_width=True)

# MARGE FORTE ET FAIBLE PRIX ------------------------------------
st.markdown("""
        <style>
            @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
        .box {
            color: #7827e6;
            font-family: 'Quicksand', cursive;
            font-size: 1.8rem;
            margin-top:2rem;
            text-align: center;
            font-weight: bold;
        }
        </style>     
        <div class="box">Marge de prix</div>
    """, unsafe_allow_html=True)

col1,col2,col3 = st.columns(3)
with col1:
    st.markdown("""
    <style>
        .custom-card {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True) 
    # 🔹 Données
    data = finance_views.medoc_forte_marge
    df_forte_marge = pd.DataFrame(data)

    # 🔹 Nettoyage / renommage
    df_forte_marge.rename(columns={
        "nom_medicament": "Médicaments",
        "marge_prix": "Marge"
    }, inplace=True)
    df_forte_marge["Marge"] = df_forte_marge["Marge"].round(2)
    df_forte_marge = df_forte_marge.sort_values(by="Marge", ascending=False)

    # 🔹 CSS pour carte centrée
    st.markdown("""
        <style>
            .custom-card {
                background-color: #f9f9f9;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin: 30px auto;
                max-width: 800px;
            }
            .custom-card h4 {
                text-align: center;
                font-size: 24px;
                color: #333333;
            }
        </style>
    """, unsafe_allow_html=True)

    # 🔹 Graphique
    fig = px.bar(
        df_forte_marge,
        x="Médicaments",
        y="Marge",
        text="Marge",
        color="Marge",
        color_continuous_scale=px.colors.sequential.Plasma
    )

    fig.update_layout(
        xaxis_title="Médicaments",
        yaxis_title="Marge prix",
        title={
                    'text': "Forte marge ",
                    'x': 0.5,  # Centre horizontalement
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
        title_font=dict(size=18),  # Taille du titre
        yaxis=dict(range=[0, df_forte_marge["Marge"].max() * 1.2]),
        showlegend=False,
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",  
        plot_bgcolor="rgba(0,0,0,0)",   
        margin=dict(l=0, r=0, t=30, b=0),
    )   

    fig.update_traces(textposition='outside')

    st.plotly_chart(fig, use_container_width=True)

    # 🔹 Fin de la carte
    st.markdown("</div>", unsafe_allow_html=True)
    
with col2:
    st.markdown("""
        <style>
            .custom-card {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
        </style>
    """, unsafe_allow_html=True)
    data = finance_views.medoc_faible_marge
    df_faible_marge = pd.DataFrame(data)
    
    df_faible_marge.rename(columns={
        "nom_medicament": "Médicaments",
        "marge_prix": "Marge"
    }, inplace=True)
    df_faible_marge["Marge"] = df_faible_marge["Marge"].round(2)
    df_faible_marge = df_faible_marge.sort_values(by="Marge", ascending=False)

    # 🔹 CSS pour carte centrée
    st.markdown("""
        <style>
            .custom-card {
                background-color: #f9f9f9;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin: 30px auto;
                max-width: 800px;
            }
            .custom-card h4 {
                text-align: center;
                font-size: 24px;
                color: #333333;
            }
        </style>
    """, unsafe_allow_html=True)

    # 🔹 Graphique
    fig = px.bar(
        df_faible_marge,
        x="Médicaments",
        y="Marge",
        text="Marge",
        color="Marge",
        color_continuous_scale=px.colors.sequential.Plasma
    )

    fig.update_layout(
        xaxis_title="Médicaments",
        yaxis_title="Marge prix",
        title={
                    'text': " Faible marge ",
                    'x': 0.5,  # Centre horizontalement
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
        title_font=dict(size=18),  # Taille du titre
        yaxis=dict(range=[0, df_faible_marge["Marge"].max() * 1.2]),
        showlegend=False,
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",  
        plot_bgcolor="rgba(0,0,0,0)",   
        margin=dict(l=0, r=0, t=30, b=0),
    )

    fig.update_traces(textposition='outside')

    st.plotly_chart(fig, use_container_width=True)

    # 🔹 Fin de la carte
    st.markdown("</div>", unsafe_allow_html=True)
    
with col3:
    # 🔹 Style personnalisé (carte)
    st.markdown("""
        <style>
            .custom-card {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Chargement des données
    data = finance_views.marge_benefice_moyen
    df_marge_moyen = pd.DataFrame(data)

    # Renommage des colonnes
    df_marge_moyen.rename(columns={
        "prix_unitaire": "Prix Vente",
        "prix_fournisseur": "Prix Achats",
        "marge_prix": "Marge Bénéficiaire"
    }, inplace=True)

    # Extraction directe des valeurs (sans moyenne)
    prix_achat = df_marge_moyen.loc[0, "Prix Achats"]
    marge = df_marge_moyen.loc[0, "Marge Bénéficiaire"]
    prix_vente = df_marge_moyen.loc[0, "Prix Vente"]

    # Préparation des données pour le funnel chart
    funnel_data = pd.DataFrame({
        "Étape": ["Prix Vente","Prix Achats", "Marge Bénéficiaire"],
        "Valeur": [prix_vente, prix_achat, marge]
    })

    # Création du graphique entonnoir 2D
    fig = px.funnel(
        funnel_data,
        x="Valeur",
        y="Étape",
    )

    fig.update_layout(
                title={
                    'text': "Marge moyenne des médicaments",
                    'x': 0.5,  # Centre horizontalement
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                title_font=dict(size=18),  # Taille du titre
                paper_bgcolor="rgba(0,0,0,0)",
                height=320,  
                plot_bgcolor="rgba(0,0,0,0)",   
                margin=dict(l=0, r=50, t=30, b=0),
            )

    st.markdown("""<div class="little-space"></div>""", unsafe_allow_html=True)
    # Affichage dans Streamlit
    st.plotly_chart(fig)

