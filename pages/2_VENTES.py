import streamlit as st
import pandas as pd
from streamlit.components.v1 import html
import plotly.graph_objects as go
import plotly.express as px
from views import vente_views,dashboard_views
from data.mongodb_client import MongoDBClient 
from pipelines import pipeline_overview
from datetime import date

from style import style






# ========== CSS Style ===============
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#========= importation style ==============
st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)
st.markdown(style.button_style, unsafe_allow_html=True)

#======== sidebar =====================
with st.sidebar:
    st.sidebar.image("assets/images/logoMahein.png", caption="", use_container_width=True)

#====================GLOBAL VARIABLES =======================
TODAY = date.today()
date_debut = dashboard_views.first_date_vente if dashboard_views.first_date_vente else TODAY
date_fin = TODAY


#1. Chiffre d'affaires
df_CA = pd.DataFrame(dashboard_views.chiffre_affaire_total)
chiffre_affaire = df_CA["chiffre_affaire_total"].sum()

#2.Nombres ventes
df_nbventes = pd.DataFrame(vente_views.nombre_ventes)
nombre_ventes = df_nbventes["nb_ventes"].sum()

col_title, col_empty, col_filter = st.columns([2, 2, 2])
with col_title:
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


# FILTRE DATE -------------------------------------------------
# if dashboard_views.employe_collection and dashboard_views.overview_collection and dashboard_views.medicament_collection:
with col_filter:
    col1,col2 = st.columns([3,2])
    if "date_range" not in st.session_state:
        st.session_state.date_range = None

    with col1:
        st.session_state.date_range = st.date_input("CHOISISSEZ 02 DATES", value=(date_debut, TODAY))
    
    with col2:
        apply_button = st.button("Appliquer");

with st.container():
    if len(st.session_state.date_range) == 2:
        date_debut, date_fin = st.session_state.date_range
        if (date_debut <= date_fin):

            # 1. Chiffre d'affaires
            # Conversion en datetime
            df_CA["date_de_vente"] = pd.to_datetime(df_CA["date_de_vente"])
            # Filtre des dates (élément par élément)
            date_filter = (df_CA["date_de_vente"].dt.date >= date_debut) & (df_CA["date_de_vente"].dt.date <= date_fin)
            # Somme du chiffre d'affaires
            chiffre_affaire = df_CA.loc[date_filter, "chiffre_affaire_total"].sum()

            # 2. Nombre de ventes
            df_nbventes["date_de_vente"] = pd.to_datetime(df_nbventes["date_de_vente"])

            date_filter = (
                (df_nbventes["date_de_vente"].dt.date >= date_debut) & 
                (df_nbventes["date_de_vente"].dt.date <= date_fin)
            )

            nombre_ventes = df_nbventes.loc[date_filter, "nb_ventes"].sum()
        

    # Affichage KPI
    st.markdown(vente_views.get_kpis(chiffre_affaire,nombre_ventes),unsafe_allow_html=True)

# Scorecard et Top vendeur ---------------------------------
with st.container():
    col1,col2 = st.columns(2)

    with col1:
        # Données
        data = vente_views.top_vendeur
        df_top_vendeur = pd.DataFrame(data)
        df_top_vendeur['date_de_vente'] = pd.to_datetime(df_top_vendeur['date_de_vente'])

        # Vérifier si bouton appliqué
        if apply_button and st.session_state.date_range:
            date_debut, date_fin = st.session_state.date_range
        else:
            date_debut, date_fin = df_top_vendeur['date_de_vente'].min(), df_top_vendeur['date_de_vente'].max()

        # Filtrer
        df_filtre = df_top_vendeur[
            (df_top_vendeur['date_de_vente'] >= pd.to_datetime(date_debut)) &
            (df_top_vendeur['date_de_vente'] <= pd.to_datetime(date_fin))
        ]

        # Agréger
        df_agg = df_filtre.groupby('_id', as_index=False)['chiffre_affaire'].sum()
        df_agg = df_agg.rename(columns={"_id": "Vendeur", "chiffre_affaire": "Chiffre d’affaires"})
        top_vendeurs = df_agg.sort_values(by="Chiffre d’affaires", ascending=False).head(3)

        # Graphique
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
        df_vendeur_non_habilite['date_de_vente'] = pd.to_datetime(df_vendeur_non_habilite['date_de_vente'])

        # --- Vérifier si bouton appliqué ---
        if apply_button and st.session_state.date_range:
            date_debut, date_fin = st.session_state.date_range
        else:
            date_debut, date_fin = df_vendeur_non_habilite['date_de_vente'].min(), df_vendeur_non_habilite['date_de_vente'].max()

        # --- Filtrage ---
        df_filtre = df_vendeur_non_habilite[
            (df_vendeur_non_habilite['date_de_vente'] >= pd.to_datetime(date_debut)) &
            (df_vendeur_non_habilite['date_de_vente'] <= pd.to_datetime(date_fin))
        ]

        # --- Agrégation et classement ---
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
        # --- Données ---
        data = vente_views.top_medicaments
        df_top_medicaments = pd.DataFrame(data)
        df_top_medicaments['date_de_vente'] = pd.to_datetime(df_top_medicaments['date_de_vente'])

        # --- Vérifier si bouton Appliquer cliqué ---
        if apply_button and st.session_state.date_range:
            date_debut, date_fin = st.session_state.date_range
        else:
            date_debut, date_fin = df_top_medicaments['date_de_vente'].min(), df_top_medicaments['date_de_vente'].max()

        # --- Filtrer ---
        df_filtre = df_top_medicaments[
            (df_top_medicaments['date_de_vente'] >= pd.to_datetime(date_debut)) &
            (df_top_medicaments['date_de_vente'] <= pd.to_datetime(date_fin))
        ]

        # --- Agrégation ---
        df_agg = df_filtre.groupby('_id', as_index=False)['quantite_totale_vendue'].sum()
        df_agg = df_agg.rename(columns={"_id": "Médicaments", "quantite_totale_vendue": "Quantité totale vendue"})

        # --- Top 3 ---
        top_medicaments = df_agg.sort_values(by="Quantité totale vendue", ascending=False).head(3)

        # --- Graphique ---
        fig = px.bar(
            top_medicaments,
            x="Quantité totale vendue",
            y="Médicaments",
            orientation='h',
            color="Quantité totale vendue",
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


with col2:
    # --- Données ---
    data = vente_views.Medoc_moins_vendus
    df_Medoc_moins = pd.DataFrame(data)
    df_Medoc_moins['date_de_vente'] = pd.to_datetime(df_Medoc_moins['date_de_vente'])

    # --- Vérifier si bouton Appliquer cliqué ---
    if apply_button and st.session_state.date_range:
        date_debut, date_fin = st.session_state.date_range
    else:
        date_debut, date_fin = df_Medoc_moins['date_de_vente'].min(), df_Medoc_moins['date_de_vente'].max()

    # --- Filtrer ---
    df_filtre = df_Medoc_moins[
        (df_Medoc_moins['date_de_vente'] >= pd.to_datetime(date_debut)) &
        (df_Medoc_moins['date_de_vente'] <= pd.to_datetime(date_fin))
    ]

    # --- Agrégation ---
    df_agg = df_filtre.groupby('_id', as_index=False)['quantite_totale_vendue'].sum()
    df_agg = df_agg.rename(columns={"_id": "Médicaments", "quantite_totale_vendue": "Quantité totale vendue"})

    # --- Top 3 moins vendus ---
    Medoc_moins = df_agg.sort_values(by="Quantité totale vendue", ascending=True).head(3)

    # --- Graphique ---
    fig = px.bar(
        Medoc_moins,
        x="Quantité totale vendue",
        y="Médicaments",
        orientation='h',
        color="Quantité totale vendue",
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

with st.container():
    # --- Données ---
    data = vente_views.saisonalite
    df_saison = pd.DataFrame(data)
    df_saison['date_de_vente'] = pd.to_datetime(df_saison['date_de_vente'])

    # --- Filtre global selon bouton Appliquer ---
    if apply_button and st.session_state.date_range:
        date_debut, date_fin = st.session_state.date_range
    else:
        date_debut, date_fin = df_saison['date_de_vente'].min(), df_saison['date_de_vente'].max()

    # --- Filtrer ---
    df_filtre = df_saison[
        (df_saison['date_de_vente'] >= pd.to_datetime(date_debut)) &
        (df_saison['date_de_vente'] <= pd.to_datetime(date_fin))
    ]

    # --- Renommer colonnes ---
    df_filtre.rename(columns={"quantite": "Quantite", "nom_medicament": "Médicaments"}, inplace=True)

    # --- Ordre des jours ---
    ordre_jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    df_filtre['jour'] = pd.Categorical(df_filtre['jour'], categories=ordre_jours, ordered=True)

    # --- Pivot table ---
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

    # --- Création heatmap ---
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

    # --- Annotations ---
    annotations = []
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

    # --- Style CSS (optionnel) ---
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

    # --- Affichage ---
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
        "annee": "Annee",
        "date_de_vente": "Date"
    }, inplace=True)

    # --- Forcer ordre des mois ---
    df_evolution["Mois"] = pd.Categorical(df_evolution["Mois"], categories=ordre_mois, ordered=True)

    # --- Initialisation date_range ---
    if "date_range" not in st.session_state:
        st.session_state.date_range = (df_evolution["Date"].min(), df_evolution["Date"].max())

    # --- Filtrage par dates ---
    df_plot = df_evolution.copy()
    if apply_button and st.session_state.date_range:
        start_date, end_date = st.session_state.date_range
        # S’assurer que ce sont des datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df_plot = df_plot[(df_plot["Date"] >= start_date) & (df_plot["Date"] <= end_date)]

    with col1:
        # --- Optionnel : filtres médicaments et années ---
        medoc_list = sorted(df_plot["Médicaments"].unique())
        selected_medocs = st.multiselect("Choisir un ou plusieurs médicaments", medoc_list)

        year_list = sorted(df_plot["Annee"].unique(), reverse=True)
        selected_years = st.multiselect("Choisir une ou plusieurs années", year_list)

        if selected_medocs:
            df_plot = df_plot[df_plot["Médicaments"].isin(selected_medocs)]
        if selected_years:
            df_plot = df_plot[df_plot["Annee"].isin(selected_years)]

        # --- Agrégation journalière si date sélectionnée ---
        if apply_button and st.session_state.date_range:
            df_plot_agg = df_plot.groupby(['Date', 'Annee', 'Médicaments'])['Quantite'].sum().reset_index()
            x_col = "Date"
        else:
            # Agrégation mensuelle par défaut
            df_plot_agg = df_plot.groupby(['Annee', 'Mois', 'Médicaments'])['Quantite'].sum().reset_index()
            df_plot_agg["Mois"] = pd.Categorical(df_plot_agg["Mois"], categories=ordre_mois, ordered=True)
            x_col = "Mois"

        # --- Légende ---
        if not selected_medocs:
            df_plot_agg_global = df_plot_agg.groupby([x_col, 'Annee'])['Quantite'].sum().reset_index()
            df_plot_agg_global['Legend'] = df_plot_agg_global["Annee"].astype(str)
            df_plot_to_show = df_plot_agg_global
        else:
            df_plot_agg['Legend'] = df_plot_agg["Médicaments"].astype(str) + " – " + df_plot_agg["Annee"].astype(str)
            df_plot_to_show = df_plot_agg

        # --- Supprimer Quantité = 0 ---
        df_plot_to_show = df_plot_to_show[df_plot_to_show['Quantite'] > 0]

    with col2: 
        # --- Graphique ---
        fig = px.line(
            df_plot_to_show,
            x=x_col,
            y="Quantite",
            color="Legend",
            markers=True
        )
        fig.update_layout(
            title="Évolution des quantités",
            xaxis_title=x_col,
            yaxis_title="Quantité Totale",
            template="plotly_white",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
from dashbot.chat_vente import create_chatbot

qa = create_chatbot()

# Préparation des données 
top_vendeurs_text = "\n".join([f"{row['Vendeur']}: {row['Chiffre d’affaires']}" for _, row in top_vendeurs.iterrows()])
vendeurs_non_text = "\n".join([f"{row['Vendeur']}: {row['Chiffre d’affaires']}" for _, row in non_habilite_vendeurs.iterrows()])
top_meds_text = "\n".join([f"{row['Médicaments']}: {row['Quantité totale vendue']}" for _, row in top_medicaments.iterrows()])
moins_meds_text = "\n".join([f"{row['Médicaments']}: {row['Quantité totale vendue']}" for _, row in Medoc_moins.iterrows()])
# saison_text = "\n".join([f"{row['Médicaments']} ({row['jour']}): {row['Quantite']}" for _, row in df_saison.iterrows()])
# evolution_text = "\n".join([f"{row['Legend']} - {row['Mois']} {row['Annee']}: {row['Quantite']:}" for _, row in df_plot.iterrows()])

# Prompt complet 
prompt = f"""
Voici les données de ventes :

Top 3 vendeurs :
{top_vendeurs_text}

Vendeurs non habilités :
{vendeurs_non_text}

Top 3 médicaments :
{top_meds_text}

Médicaments les moins vendus :
{moins_meds_text}

"""

# Saisonnalité (ventes par jour et médicament) :
# {saison_text}

# Évolution des ventes par mois (proportionnelle) :


# {evolution_text}
# Chatbot interactif 
st.title("💬 Chatbot Analyse des ventes")

if "messages_vente" not in st.session_state:
    st.session_state.messages_vente = []

for msg in st.session_state.messages_vente:
    st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input("Posez une question sur les ventes"):
    st.session_state.messages_vente.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    full_prompt = f"{prompt}\n\nQuestion de l'utilisateur : {question}"
    response = qa.run(full_prompt)

    st.session_state.messages_vente.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)