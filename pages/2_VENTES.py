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
    color: #0A9548;
    font-family: 'Dancing Script', cursive;
    font-size: 74px;
    margin-top:-1rem;
  }
</style>
<div class="box">Ventes</div>
""")


st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)
with st.container():
    st.markdown("### Filtrer les ventes par date")
    # Sélecteur de date
    col1,col2 = st.columns([1,3])
    with col1:
        # --- Inputs utilisateur ---
        date_debut = st.date_input("Date début", value=None)
        date_fin = st.date_input("Date fin", value=None)
    with col2:
        df_CA = pd.DataFrame(dashboard_views.chiffre_affaire)
        # Conversion de la colonne date
        df_CA["_id"] = pd.to_datetime(df_CA["_id"])
        # Cas 1 : pas de filtre
        if not date_debut or not date_fin:
            somme_CA = df_CA["chiffre_affaire_total"].sum()
        else:
            # Vérif cohérence des dates
            if date_fin < date_debut:
                st.error("⚠️ La date de fin doit être supérieure à la date de début")
                somme_CA = df_CA["chiffre_affaire_total"].sum()  # fallback sur total

            else:
                mask = (df_CA["_id"].dt.date >= date_debut) & (df_CA["_id"].dt.date <= date_fin)
                print("Dedans: ", df_CA.loc[mask])
                somme_CA = df_CA.loc[mask, "chiffre_affaire_total"].sum()
        #ventes

        df_Nb_vente = pd.DataFrame(vente_views.nombre_ventes)

        # Conversion de la colonne date
        df_Nb_vente["date_de_vente"] = pd.to_datetime(df_Nb_vente["date_de_vente"])

        # Cas 1 : pas de filtre
        if not date_debut or not date_fin:
            somme_ventes = df_Nb_vente["nb_ventes"].sum()
        else:
            # Vérif cohérence des dates
            if date_fin <= date_debut:
                st.error("⚠️ La date de fin doit être supérieure à la date de début")
                somme_ventes = df_Nb_vente["nb_ventes"].sum()  # fallback sur total
            else:
                mask = (df_Nb_vente["date_de_vente"].dt.date >= date_debut) & (df_Nb_vente["date_de_vente"].dt.date <= date_fin)
                print("Dedans: ", df_Nb_vente.loc[mask])
                somme_ventes = df_Nb_vente.loc[mask, "nb_ventes"].sum()

        # Affichage KPI (avec formatage sans décimales et séparateurs milliers)

        # Affichage KPI (avec formatage sans décimales et séparateurs milliers)
        st.markdown(
            vente_views.get_kpis(chiffre_affaire=somme_CA, nombre_ventes=somme_ventes),
            unsafe_allow_html=True
        )

        

# Scorecard et Top vendeur ---------------------------------
with st.container():
    col1,col2 = st.columns(2)

    with col1:
       # Données exemple
        data = vente_views.top_vendeur
        df_top_vendeur = pd.DataFrame(data)
        df_top_vendeur['date_de_vente'] = pd.to_datetime(df_top_vendeur['date_de_vente'])

        # --- Cas où aucune date n'est sélectionnée ---
        if date_debut is None and date_fin is None:
            # Agrégation globale par vendeur
            df_agg = df_top_vendeur.groupby('_id', as_index=False)['chiffre_affaire'].sum()
            df_agg = df_agg.rename(columns={"_id": "Vendeur", "chiffre_affaire": "Chiffre d’affaires"})
            top_vendeurs = df_agg.sort_values(by="Chiffre d’affaires", ascending=False).head(3)

        # --- Cas où des dates sont sélectionnées ---
        else:
            if date_debut is None:
                date_debut = df_top_vendeur['date_de_vente'].min()
            if date_fin is None:
                date_fin = df_top_vendeur['date_de_vente'].max()

            df_filtre = df_top_vendeur[
                (df_top_vendeur['date_de_vente'] >= pd.to_datetime(date_debut)) &
                (df_top_vendeur['date_de_vente'] <= pd.to_datetime(date_fin))
            ]

            df_agg = df_filtre.groupby('_id', as_index=False)['chiffre_affaire'].sum()
            df_agg = df_agg.rename(columns={"_id": "Vendeur", "chiffre_affaire": "Chiffre d’affaires"})
            top_vendeurs = df_agg.sort_values(by="Chiffre d’affaires", ascending=False).head(3)

        # --- Graphique Plotly ---
        fig = px.bar(
            top_vendeurs,
            x="Chiffre d’affaires",
            y="Vendeur",
            orientation='h',
            color="Chiffre d’affaires",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Top 3 vendeurs"
        )
        fig.update_layout(
            title=dict(text="Top 3 vendeurs", x=0.5, xanchor='center', font=dict(size=20, color='black')),
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

    with col2:
    
        # Données
        data = vente_views.vendeur_non_habilite
        df_vendeur_non_habilite = pd.DataFrame(data)
        # --- Agrégation et top vendeurs ---
        df_vendeur_non_habilite['date_de_vente'] = pd.to_datetime(df_vendeur_non_habilite['date_de_vente'])

        if date_debut is None and date_fin is None:
            df_agg = df_vendeur_non_habilite.groupby('_id', as_index=False)['chiffre_affaire'].sum()
            df_agg = df_agg.rename(columns={"_id": "Vendeur", "chiffre_affaire": "Chiffre d’affaires"})
            non_habilite_vendeurs = df_agg.sort_values(by="Chiffre d’affaires", ascending=True).head(3)
        else:
            if date_debut is None:
                date_debut = df_vendeur_non_habilite['date_de_vente'].min()
            if date_fin is None:
                date_fin = df_vendeur_non_habilite['date_de_vente'].max()

            df_filtre = df_vendeur_non_habilite[
                (df_vendeur_non_habilite['date_de_vente'] >= pd.to_datetime(date_debut)) &
                (df_vendeur_non_habilite['date_de_vente'] <= pd.to_datetime(date_fin))
            ]
            df_agg = df_filtre.groupby('_id', as_index=False)['chiffre_affaire'].sum()
            df_agg = df_agg.rename(columns={"_id": "Vendeur", "chiffre_affaire": "Chiffre d’affaires"})
            non_habilite_vendeurs = df_agg.sort_values(by="Chiffre d’affaires", ascending=True).head(3)

        # --- Graphique ---
        fig = px.bar(
            non_habilite_vendeurs,
            x="Chiffre d’affaires",
            y="Vendeur",
            orientation='h',
            color="Chiffre d’affaires",
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig.update_layout(
            title=dict(text="Vendeurs non habilités", x=0.5, xanchor='center', font=dict(size=20, color='black')),
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="Montant des ventes",
            yaxis_title="Vendeur",
            showlegend=False,
            height=350
        )
        fig.update_yaxes(autorange="reversed")

        st.plotly_chart(fig, use_container_width=True)



# Graphiques Top Médicaments et Moins Vendus -----------------------------
with st.container():
    col1,col2 = st.columns(2)

    with col1:
        # --- Données exemple ---
        data = vente_views.top_medicaments
        df_top_medicaments = pd.DataFrame(data)
        df_top_medicaments['date_de_vente'] = pd.to_datetime(df_top_medicaments['date_de_vente'])

        # --- Définir les bornes si aucune date ---
        if date_debut is None:
            date_debut = df_top_medicaments['date_de_vente'].min()
        if date_fin is None:
            date_fin = df_top_medicaments['date_de_vente'].max()

        # --- Filtrer par dates ---
        df_filtre = df_top_medicaments[
            (df_top_medicaments['date_de_vente'] >= pd.to_datetime(date_debut)) &
            (df_top_medicaments['date_de_vente'] <= pd.to_datetime(date_fin))
        ]

        # --- Agrégation par médicament ---
        df_agg = df_filtre.groupby('_id', as_index=False)['quantite_totale_vendue'].sum()
        df_agg = df_agg.rename(columns={"_id": "Médicaments", "quantite_totale_vendue": "quantite totale vendue"})

        # --- Top 3 médicaments ---
        top_medicaments = df_agg.sort_values(by="quantite totale vendue", ascending=False).head(3)

        # --- Graphique ---
        fig = px.bar(
            top_medicaments,
            x="quantite totale vendue",
            y="Médicaments",
            orientation='h',
            color="quantite totale vendue",
            color_continuous_scale=px.colors.sequential.Plasma,
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

        st.markdown('</div>', unsafe_allow_html=True)


    with col2:
        # --- Données exemple ---
        data = vente_views.Medoc_moins_vendus
        df_Medoc_moins = pd.DataFrame(data)
        df_Medoc_moins['date_de_vente'] = pd.to_datetime(df_Medoc_moins['date_de_vente'])

        # --- Définir les bornes si aucune date ---
        if date_debut is None:
            date_debut = df_Medoc_moins['date_de_vente'].min()
        if date_fin is None:
            date_fin = df_Medoc_moins['date_de_vente'].max()

        # --- Filtrer par dates ---
        df_filtre = df_Medoc_moins[
            (df_Medoc_moins['date_de_vente'] >= pd.to_datetime(date_debut)) &
            (df_Medoc_moins['date_de_vente'] <= pd.to_datetime(date_fin))
        ]

        # --- Agrégation par médicament ---
        df_agg = df_filtre.groupby('_id', as_index=False)['quantite_totale_vendue'].sum()
        df_agg = df_agg.rename(columns={"_id": "Médicaments", "quantite_totale_vendue": "quantite totale vendue"})

        # --- Top 3 moins vendus ---
        Medoc_moins = df_agg.sort_values(by="quantite totale vendue", ascending=True).head(3)

        # --- Graphique Plotly ---
        fig = px.bar(
            Medoc_moins,
            x="quantite totale vendue",
            y="Médicaments",
            orientation='h',
            color="quantite totale vendue",
            color_continuous_scale=px.colors.sequential.Plasma,
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
    # --- Données exemple ---
        data = vente_views.saisonalite
        df_saison = pd.DataFrame(data)

        # --- Conversion en datetime ---
        df_saison['date_de_vente'] = pd.to_datetime(df_saison['date_de_vente'])

        # --- Définir les bornes si aucune date ---
        if date_debut is None:
            date_debut = df_saison['date_de_vente'].min()
        if date_fin is None:
            date_fin = df_saison['date_de_vente'].max()

        # --- Filtrer par dates ---
        df_filtre = df_saison[
            (df_saison['date_de_vente'] >= pd.to_datetime(date_debut)) &
            (df_saison['date_de_vente'] <= pd.to_datetime(date_fin))
        ]

        # --- Renommer les colonnes ---
        df_filtre.rename(columns={"quantite": "Quantite", "nom_medicament": "Médicaments"}, inplace=True)

        # --- Ordre des jours de la semaine ---
        ordre_jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        df_filtre['jour'] = pd.Categorical(df_filtre['jour'], categories=ordre_jours, ordered=True)

        # --- Pivot table : Médicaments en index, jours en colonnes, somme des quantités ---
        pivot = df_filtre.pivot_table(
            index='Médicaments',
            columns='jour',
            values='Quantite',
            aggfunc='sum',
            fill_value=0
        )

        z = pivot.values.tolist()
        x = pivot.columns.tolist()
        y = pivot.index.tolist()

        # --- Création heatmap avec dégradé vert ---
        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale=[
                [0, '#8EA26B'],   
                [0.5, '#487835'], 
                [1, '#0A9548']    
            ],
            colorbar=dict(title='Quantité Totale'),
        ))

        # --- Annotations des valeurs dans chaque case ---
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
                            font=dict(color='white'),
                            xanchor='center',
                            yanchor='middle'
                        )
                    )

        fig.update_layout(
            title={
                "text": 'Répartition des quantités de médicaments vendues par jour de la semaine',
                'y': 0.95,                              
                'x': 0.5, 
                'xanchor': 'center',                   
                'yanchor': 'top',                      
                "font": dict(size=24, color="#0A9548")
            },
            xaxis_title='Jour',
            yaxis_title='Médicaments',
            annotations=annotations,
            yaxis=dict(autorange='reversed'),
            height=500 
        )

        # --- Style CSS pour la carte dans Streamlit (optionnel) ---
        st.markdown("""
        <div class="card">
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

        # --- Affichage du graphique ---
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
# Graphique d'évolution des ventes par médicament -----------------------------
with st.container():
    st.markdown("""
        <style>
            @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
        .box {
            color: #0A9548;
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
        "quantite": "Quantite",
        "nom_medicament": "Médicaments",
        "mois": "Mois",
        "annee": "Annee"
    }, inplace=True)

    # Forcer ordre des mois
    df_evolution["Mois"] = pd.Categorical(df_evolution["Mois"], categories=ordre_mois, ordered=True)

    # --- Filtre Médicaments & Année ---
    with col1:
        medoc_list = sorted(df_evolution["Médicaments"].unique())
        selected_medocs = st.multiselect("Choisir un ou plusieurs médicaments", medoc_list)

        year_list = sorted(df_evolution["Annee"].unique(), reverse=True)
        selected_years = st.multiselect("Choisir une ou plusieurs années", year_list)

    # --- Filtrage ---
        if not selected_medocs:
            # Aucun médicament sélectionné => total global par année
            if selected_years:
                df_plot = df_evolution[df_evolution["Annee"].isin(selected_years)]
            else:
                df_plot = df_evolution.copy()
            
            df_plot = df_plot.groupby(["Annee", "Mois"])["Quantite"].sum().reset_index()
            
            # Supprimer les lignes où Quantite = 0
            df_plot = df_plot[df_plot["Quantite"] > 0]
            
            df_plot["Legend"] = df_plot["Annee"].astype(str)
            title_suffix = " (Total Global par Année)"
        else:
                df_plot = df_evolution[df_evolution["Médicaments"].isin(selected_medocs)]
                if selected_years:
                    df_plot = df_plot[df_plot["Annee"].isin(selected_years)]
                
                # Supprimer les lignes où Quantite = 0
                df_plot = df_plot[df_plot["Quantite"] > 0]
                
                df_plot["Legend"] = df_plot["Médicaments"] + " - " + df_plot["Annee"].astype(str)
                title_suffix = ""
    # --- Graphique ---
    with col2:
        fig = px.line(df_plot, x="Mois", y="Quantite", color="Legend",
                    markers=True)
        fig.update_layout(
            xaxis_title="Mois",
            yaxis_title="Quantité Totale",
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=30, r=0, t=30, b=30),
            height=230,
        )
        st.plotly_chart(fig, use_container_width=True)
