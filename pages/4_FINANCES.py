import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
from views import finance_views, dashboard_views
from datetime import date
import calendar

from style import style


# Initialisation
st.set_page_config(page_title="FINANCE", layout="wide")

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
        margin-bottom:-7rem;
        
    }
    </style>
    <div class="box">Finances</div>
    """)

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


with col_filter:
    col1,col2 = st.columns([3,2])
    if "date_range" not in st.session_state:
        st.session_state.date_range = None

    with col1:
        st.session_state.date_range = st.date_input("CHOISISSEZ 02 DATES", value=(date_debut, TODAY))
    
    with col2:
        apply_button = st.button("Appliquer");


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

    col1, col2 = st.columns([1,3])

    with col1:
        # Multiselect médicaments
        medicaments_dispo = sorted(df_finance['nom_medicament'].dropna().unique())
        medicaments_choisis = st.multiselect("Sélectionner les médicaments :", medicaments_dispo)

         # Multiselect années
        annees_dispo = sorted(df_finance['annee'].dropna().unique().astype(int))
        annees_choisies = st.multiselect("Sélectionner les années :", annees_dispo, default=[max(annees_dispo)])

    with col2:

    # CHIFFRE D'AFFAIRE ------------------------------------
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
                title=f"Évolution du chiffre d’affaires mensuel - {', '.join(medicaments_choisis) if medicaments_choisis else 'Année'}"
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

        # Renommer les colonnes
        df_rapporte_moins.rename(columns={"nom_medicament": "Médicaments", "total_gain": "Total Gain"}, inplace=True)

        # --- Convertir la colonne date en datetime si elle existe ---
        # (il faut que ta table ait une colonne date, ex: 'date_de_vente')
        df_rapporte_moins['date_de_vente'] = pd.to_datetime(df_rapporte_moins['date_de_vente'])

        # --- Vérifier si bouton Appliquer cliqué ---
        if apply_button and st.session_state.date_range:
            date_debut, date_fin = st.session_state.date_range
        else:
            date_debut, date_fin = df_rapporte_moins['date_de_vente'].min(), df_rapporte_moins['date_de_vente'].max()

        # --- Filtrer le dataframe par date ---
        df_filtre = df_rapporte_moins[
            (df_rapporte_moins['date_de_vente'] >= pd.to_datetime(date_debut)) &
            (df_rapporte_moins['date_de_vente'] <= pd.to_datetime(date_fin))
        ]

        # --- Agrégation si besoin (par exemple somme du gain par médicament) ---
        df_agg = df_filtre.groupby('Médicaments', as_index=False)['Total Gain'].sum()
        df_top3_moins = df_agg.sort_values(by="Total Gain", ascending=True).head(3)

        # --- Graphique camembert ---
        fig = px.pie(
            df_top3_moins,
            names="Médicaments",
            values="Total Gain",
            hole=0.4
        )

        fig.update_layout(
            title={
                'text': "Médicaments qui rapportent le moins",
                'y': 0.90,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            width=400,
            height=335,
            title_font=dict(size=18),
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=30, r=30, t=80, b=30),
        )

        st.plotly_chart(fig, use_container_width=True)


    with col2:
        # --- Récupérer les données ---
        data = finance_views.medoc_rapporte_plus
        df_rapporte_plus = pd.DataFrame(data)

        # Renommer les colonnes
        df_rapporte_plus.rename(columns={"nom_medicament": "Médicaments", "total_gain": "Total Gain"}, inplace=True)

        # --- Convertir la colonne date en datetime ---
        df_rapporte_plus['date_de_vente'] = pd.to_datetime(df_rapporte_plus['date_de_vente'])

        # --- Filtre par date ---
        if 'date_range_plus' not in st.session_state:
            st.session_state.date_range_plus = (df_rapporte_plus['date_de_vente'].min(), df_rapporte_plus['date_de_vente'].max())

        date_debut, date_fin = st.session_state.date_range_plus

        # Appliquer le filtre
        df_filtre = df_rapporte_plus[
            (df_rapporte_plus['date_de_vente'] >= pd.to_datetime(date_debut)) &
            (df_rapporte_plus['date_de_vente'] <= pd.to_datetime(date_fin))
        ]

        # --- Agrégation et top 3 plus rapporteurs ---
        df_agg = df_filtre.groupby('Médicaments', as_index=False)['Total Gain'].sum()
        df_top3_plus = df_agg.sort_values(by="Total Gain", ascending=False).head(3)

        # --- Style card ---
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

        # --- Graphique camembert (donut) ---
        fig = px.pie(
            df_top3_plus,
            names="Médicaments",
            values="Total Gain",
            hole=0.4
        )

        fig.update_layout(
            title={
                'text': "Médicaments qui rapportent le plus",
                'y': 0.90,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'bottom'
            },
            width=400,
            height=335,
            title_font=dict(size=18),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=30, r=30, t=80, b=30),
        )

        # Affichage dans Streamlit
        st.plotly_chart(fig, use_container_width=True)
# MARGE FORTE ET FAIBLE PRIX ------------------------------------
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
        <div class="box">Marges</div>
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
    # --- Récupérer les données ---
    data = finance_views.medoc_forte_marge
    df_forte_marge = pd.DataFrame(data)

    # 🔹 Renommage et nettoyage
    df_forte_marge.rename(columns={
        "nom_medicament": "Médicaments",
        "marge_prix": "Marges",
        "date_de_vente": "Date"  # si tu as la colonne date
    }, inplace=True)

    # Convertir la date si existante
    if "Date" in df_forte_marge.columns:
        df_forte_marge["Date"] = pd.to_datetime(df_forte_marge["Date"])

    # 🔹 Filtre par date (optionnel)
    if "Date" in df_forte_marge.columns:
        if 'date_range_marge' not in st.session_state:
            st.session_state.date_range_marge = (df_forte_marge['Date'].min(), df_forte_marge['Date'].max())

        date_debut, date_fin = st.session_state.date_range_marge

        df_forte_marge = df_forte_marge[
            (df_forte_marge['Date'] >= pd.to_datetime(date_debut)) &
            (df_forte_marge['Date'] <= pd.to_datetime(date_fin))
        ]

    # 🔹 Limiter aux top 10 marges
    df_forte_marge = df_forte_marge.sort_values(by="Marges", ascending=False).head(3)
    df_forte_marge["Marges"] = df_forte_marge["Marges"].round(2)

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

    # 🔹 Graphique bar
    fig = px.bar(
        df_forte_marge,
        x="Médicaments",
        y="Marges",
        color="Marges",
        color_continuous_scale=px.colors.sequential.Plasma
    )

    fig.update_layout(
        xaxis_title="Médicaments",
        yaxis_title="Marges prix",
        title={
            'text': "Médicaments à forte marge",
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        title_font=dict(size=18),
        yaxis=dict(range=[0, df_forte_marge["Marges"].max() * 1.2]),
        showlegend=False,
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",  
        plot_bgcolor="rgba(0,0,0,0)",   
        margin=dict(l=0, r=0, t=30, b=0),
    )

    fig.update_traces(textposition='outside')

    # 🔹 Affichage dans Streamlit
    st.plotly_chart(fig, use_container_width=True)
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
    # --- Récupérer les données ---
    data = finance_views.medoc_faible_marge
    df_faible_marge = pd.DataFrame(data)

    # 🔹 Renommage et nettoyage
    df_faible_marge.rename(columns={
        "nom_medicament": "Médicaments",
        "marge_prix": "Marges",
        "date_de_vente": "Date"  # si tu as la colonne date
    }, inplace=True)

    # Convertir la date si existante
    if "Date" in df_faible_marge.columns:
        df_faible_marge["Date"] = pd.to_datetime(df_faible_marge["Date"])

    # 🔹 Filtre par date (optionnel)
    if "Date" in df_faible_marge.columns:
        if 'date_range_faible_marge' not in st.session_state:
            st.session_state.date_range_faible_marge = (df_faible_marge['Date'].min(), df_faible_marge['Date'].max())

        date_debut, date_fin = st.session_state.date_range_faible_marge

        df_faible_marge = df_faible_marge[
            (df_faible_marge['Date'] >= pd.to_datetime(date_debut)) &
            (df_faible_marge['Date'] <= pd.to_datetime(date_fin))
        ]

    # 🔹 Limiter aux top 10 marges faibles (tri croissant)
    df_faible_marge = df_faible_marge.sort_values(by="Marges", ascending=True).head(3)
    df_faible_marge["Marges"] = df_faible_marge["Marges"].round(2)

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

    # 🔹 Graphique bar
    fig = px.bar(
        df_faible_marge,
        x="Médicaments",
        y="Marges",
        color="Marges",
        color_continuous_scale=px.colors.sequential.Plasma
    )

    fig.update_layout(
        xaxis_title="Médicaments",
        yaxis_title="Marges prix",
        title={
            'text': " Médicaments à faible marge",
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        title_font=dict(size=18),
        yaxis=dict(range=[0, df_faible_marge["Marges"].max() * 1.2]),
        showlegend=False,
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",  
        plot_bgcolor="rgba(0,0,0,0)",   
        margin=dict(l=0, r=0, t=30, b=0),
    )

    fig.update_traces(textposition='outside')

    # 🔹 Affichage dans Streamlit
    st.plotly_chart(fig, use_container_width=True)
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
        "prix_unitaire": "Prix de vente",
        "prix_fournisseur": "Prix d'achat",
        "marge_prix": "Marges bénéficiaires"
    }, inplace=True)

    # Extraction directe des valeurs (sans moyenne)
    prix_achat = df_marge_moyen.loc[0, "Prix d'achat"]
    marge = df_marge_moyen.loc[0, "Marges bénéficiaires"]
    prix_vente = df_marge_moyen.loc[0, "Prix de vente"]

    # Préparation des données pour le funnel chart
    funnel_data = pd.DataFrame({
        "_": ["Prix de vente","Prix d'achat", "Marges bénéficiaires"],
        "Valeur": [round(prix_vente), round(prix_achat), round(marge)]
    })

    # Création du graphique entonnoir 2D
    fig = px.funnel(
        funnel_data,
        x="Valeur",
        y="_",
    )

    fig.update_layout(
                title={
                    'text': "Marges moyennes (MGA)",
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

from dashbot.chat_finance import create_chatbot 

qa = create_chatbot()

#CA_mois = "\n".join([f"{row['annee']}: {row['chiffre_affaire_mois']}" for _, row in df_filtre.iterrows()])
rapporte_plus = "\n".join([f"{row['Médicaments']}: {row['Total Gain']}" for _, row in df_rapporte_plus.iterrows()])
#rapporte_moins = "\n".join([f"{row['Médicaments']}: {row['Total Gain']}" for _, row in df_rapporte_moins.iterrows()])
#forte_marge = "\n".join([f"{row['Médicaments']}: {row['Marges']}" for _, row in df_forte_marge.iterrows()])
#faible_marge = "\n".join([f"{row['Médicaments']}: {row['Marges']}" for _, row in df_faible_marge.iterrows()])
funnel_data = "\n".join([f"{row['Prix de vente']}: {row["Prix d'chats"]}: {row['Marges bénéficiaires']}" for _, row in funnel_data.iterrows()])


# prompt prêt à l’emploi
prompt = f"""
Voici les données des finances :

# Chiffre d'affaire mensuel :
#{CA_mois}

#Médicaments qui rapportent moins :
#{rapporte_moins}

Médicaments qui rapportent plus :
{rapporte_plus}

#Forte marge de prix des médicamants :
#{forte_marge}

#Faible marge de prix des médicamants :
#{faible_marge}

Marge moyenne de prix des médicamants :
{funnel_data}

"""



# Chatbot interactif
st.title("💬 Chatbot Analyse des finances")

if "messages_finances" not in st.session_state:
    st.session_state.messages_finances = []

for msg in st.session_state.messages_finances:
    st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input("Posez une question sur le finance"):
    st.session_state.messages_finances.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    # On combine la question de l’utilisateur avec les données préparées
    full_prompt = f"{prompt}\n\nQuestion de l'utilisateur : {question}"
    response = qa.run(full_prompt)
    #response = qa({"query": full_prompt})

    st.session_state.messages_finances.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
with st.container():
        # with col4:
# 🔹 Style personnalisé
    # 🔹 Données
    data_pertes = finance_views.Evolution_pertes
    df_pertes = pd.DataFrame(data_pertes)
