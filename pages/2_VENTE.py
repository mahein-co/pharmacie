import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
import plotly.graph_objects as go
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



# Scorecard et Top vendeur ---------------------------------
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
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="Montant des ventes",
            yaxis_title="Vendeur",
            showlegend=False,
            height=350,
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_traces(textposition='outside', textfont=dict(color='#48494B'))

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
                text="Vendeurs non habilités",
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="Montant des ventes",
            yaxis_title="Vendeur",
            showlegend=False,
            height=350,
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', textfont=dict(color='#48494B'))

        st.plotly_chart(fig, use_container_width=True)

        # Fermer carte
        st.markdown('</div>', unsafe_allow_html=True)

# Graphiques Top Médicaments et Moins Vendus -----------------------------
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
                text="Médicaments les plus vendus",
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            xaxis_title="Quantité vendue",
            yaxis_title="Médicaments",
            showlegend=False,
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=30, b=0),
        )

        fig.update_yaxes(autorange="reversed")
        fig.update_traces(textposition='outside', textfont=dict(color='#48494B'))

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
                text="Médicaments les moins vendus",
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            xaxis_title="Quantité vendue",
            yaxis_title="Médicaments",
            showlegend=False,
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=30, b=0),
        )

        fig.update_yaxes(autorange="reversed")
        fig.update_traces(textposition='outside', textfont=dict(color='#48494B'))

        st.plotly_chart(fig, use_container_width=True)

        # Fermeture du div .card
        st.markdown('</div>', unsafe_allow_html=True)

# Heatmap des quantités vendues par jour et médicament -----------------------------
with st.container():
    # Supposons que vente_views.saisonalite soit déjà chargé
    data = vente_views.saisonalite
    df_saison = pd.DataFrame(data)
    
    # Renommer les colonnes
    df_saison.rename(columns={"quantite_totale": "Quantite Totale", "nom_medicament": "Médicaments"}, inplace=True)

    # Ordre des jours de la semaine
    ordre_jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    df_saison['jour'] = pd.Categorical(df_saison['jour'], categories=ordre_jours, ordered=True)

    # Pivot table : Médicaments en index, jours en colonnes
    pivot = df_saison.pivot(index='Médicaments', columns='jour', values='Quantite Totale')

    z = pivot.values.tolist()
    x = pivot.columns.tolist()
    y = pivot.index.tolist()

    # Création heatmap avec dégradé vert
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x,
        y=y,
        colorscale=[
            [0, '#E0B0FF'],   
            [0.5, '#A87BC7'], 
            [1, '#734A91']    
        ],
        colorbar=dict(title='Quantité Totale'),
    ))

    # Annotations des valeurs dans chaque case
    annotations = []
    max_val = pivot.max().max() if pivot.max().max() else 0  # éviter erreur si pivot vide

    for i, medicament in enumerate(y):
        for j, jour in enumerate(x):
            val = z[i][j]
            if pd.notnull(val):
                annotations.append(
                    go.layout.Annotation(
                        text=str(int(val)),
                        x=jour,
                        y=medicament,
                        showarrow=False,
                        font=dict(color='white' if val > (max_val / 2) else 'black'),
                        xanchor='center',
                        yanchor='middle'
                    )
                )

    fig.update_layout(
        title={
            "text":'Répartition des quantités de médicaments vendues par jour de la semaine',
            'y':0.95,                              
            'x':0.5, 
            'xanchor': 'center',                   
            'yanchor': 'top',                      
            "font": dict(
            size=24,       
            color="#7827e6", 
        )
        }, 
        xaxis_title='Jour',
        yaxis_title='Médicaments',
        annotations=annotations,
        yaxis=dict(autorange='reversed'),
        height=500 
    )

    # Style CSS pour la carte dans Streamlit (optionnel)
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

    # Affichage du graphique
    st.plotly_chart(fig, use_container_width=True)

# Graphique d'évolution des ventes par médicament -----------------------------
with st.container():
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
        <div class="box">Évolution des ventes d'un médicament</div>
    """, unsafe_allow_html=True)
    # --- Mise en page ---
    col1, col2 = st.columns([1, 3])
    # --- Style card (optionnel) ---
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

    # --- Ordre des mois ---
    ordre_mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    # --- Récupération des données ---
    data = vente_views.Medoc_evolution
    df_evolution = pd.DataFrame(data)

    # --- Renommage colonnes ---
    df_evolution.rename(columns={
        "quantite_totale": "Quantite Totale",
        "nom_medicament": "Médicaments",
        "mois": "Mois",
        "annee": "Annee"
    }, inplace=True)

    # Forcer ordre des mois
    df_evolution["Mois"] = pd.Categorical(df_evolution["Mois"], categories=ordre_mois, ordered=True)

    # --- Filtre Médicaments & Année ---
    with col1:
        medoc_list = sorted(df_evolution["Médicaments"].unique())
        st.markdown("""<div class="little-space"></div>""", unsafe_allow_html=True)
        selected_medoc = st.selectbox("Choisissez un médicaments", medoc_list)
        year_list = sorted(df_evolution["Annee"].unique(), reverse=True)
        current_year = st.selectbox("Année actuelle", year_list, index=0)

    # --- Filtrage ---
    df_current = df_evolution[(df_evolution["Médicaments"] == selected_medoc) & 
                            (df_evolution["Annee"] == current_year)].sort_values("Mois")

    previous_year = current_year - 1
    df_previous = df_evolution[(df_evolution["Médicaments"] == selected_medoc) & 
                            (df_evolution["Annee"] == previous_year)].sort_values("Mois")

    # --- Graphique ---
    with col2:
        fig = px.line()

        # Ajouter courbe actuelle
        if not df_current.empty:
            fig.add_scatter(x=df_current["Mois"], y=df_current["Quantite Totale"],
                            mode='lines+markers', name=f"{current_year}")

        # Ajouter courbe précédente si dispo
        if not df_previous.empty:
            fig.add_scatter(x=df_previous["Mois"], y=df_previous["Quantite Totale"],
                            mode='lines+markers', name=f"{previous_year}")

        fig.update_layout(
            title=f"{selected_medoc}",
            xaxis_title="Mois",
            yaxis_title="Quantité Totale",
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=30, r=30, t=30, b=30),
            height=235,
        )

        st.plotly_chart(fig, use_container_width=True)

