import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
from views import medicament_views,dashboard_views
from itertools import product
from style import style, icons


from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.metrics import mean_squared_error



# Initialisation ------------------------------------
st.set_page_config(page_title="MEDICAMENT", layout="wide")

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
    <div class="box">Médicaments</div>
    """)

st.markdown(style.custom_css,unsafe_allow_html=True)
st.markdown(style.kpis_style,unsafe_allow_html=True)


with col_filter:
    # st.markdown("#### Filtrer les ventes par")
    col1,col2 = st.columns(2)
    # --- Inputs utilisateur ---
    with col1:
        date_debut = st.date_input("Date de début du filtre", value=None)
    with col2:
        date_fin = st.date_input("Date de fin du filtre", value=None, min_value=(date_debut))



if medicament_views.overview_collection :
  st.markdown(medicament_views.kpis_html,unsafe_allow_html=True)

else:
    st.error("Il est impossible de charger les données depuis la database.")

# ANTICIPATION DE RUPTURE DE STOCK && PREDICTION DU RISQUE DE RETARD DE LIVRAISON ---------------------
# PREDICTION DE RUPTURE DE STOCK
# Étape 1 : préparation des colonnes nécessaires
overview_df = pd.DataFrame(dashboard_views.vente_docs)
overview_df['jour_semaine'] = overview_df['date_de_vente'].dt.dayofweek  # 0 = Lundi, 6 = Dimanche
overview_df['mois_num'] = overview_df['date_de_vente'].dt.month

# Medicament dataframe
medicament_df = pd.DataFrame(dashboard_views.medicament_docs)
# Get unique id_medicament and nom
medicament_df = medicament_df.drop_duplicates(subset=['id_medicament'])
medicament_df = medicament_df[['id_medicament', 'nom', 'prix_unitaire', 'fournisseur', 'prix_fournisseur', 'Quantity_arrival']]
medifcament_to_filter = medicament_df.to_dict(orient="records")

def get_medicament_to_predict(medicament_choisi):
    if not medicament_choisi:
        return medifcament_to_filter[0]

    medicament_to_predict = next((item for item in medifcament_to_filter if item["nom"] == medicament_choisi), None)
    return medicament_to_predict

with st.container():
    # Title anticipation de rupture de stock
    # html("""
    # <style>
    #     @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
        
    # .box {
    #     color: #0A9548;
    #     font-family: 'Quicksand', cursive;
    #     font-weight: bold;
    #     font-size: 27px;
    #     margin-top:3rem;
    #     margin-bottom:-5rem;
    #     text-align: left;
    # }
    # </style>
    # <p class="box">Anticipation des ruptures de stock d’un médicament</p>
    # """)
    
    st.markdown("""<div class="kpi-container-third">""", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])
    with col1:
        options = [item['nom'] for item in medifcament_to_filter]
        medicament_choisi = st.selectbox("Choisissez un médicament", options)
        medicament_to_predict = get_medicament_to_predict(medicament_choisi)

        # Card
        medicament_info = f"""
            <div class="kpi-card">
                <div style="text-align: left; position:absolute;">
                {icons.prix_vente_icon_html}
                </div>
                    <p class="kpi-title" style="font-size:1rem;">Prix Unitaire (MGA)</p>
                    <p class="kpi-value" style="font-size:1.5rem;">{medicament_to_predict["prix_unitaire"]}</p>
            </div>
            <div class="kpi-card">
                <div style="text-align: left; position:absolute;">
                {icons.prix_fournisseur_icon_html}
                </div>
                    <p class="kpi-title" style="font-size:1rem;">Prix Fournisseur (MGA)</p>
                    <p class="kpi-value" style="font-size:1.5rem;">{medicament_to_predict["prix_fournisseur"]}</p>
                </div>
            </div>
        """

        st.markdown(medicament_info, unsafe_allow_html=True)

    # Étape 1 : préparation des colonnes nécessaires
    overview_df['jour_semaine'] = overview_df['date_de_vente'].dt.dayofweek  # 0 = Lundi, 6 = Dimanche
    overview_df['mois_num'] = overview_df['date_de_vente'].dt.month

    # Étape 2 : calcul des probabilités historiques par mois et jour de semaine
    combo_group = overview_df.groupby(['id_medicament', 'mois_num', 'jour_semaine'])['quantite']
    combo_zero = combo_group.apply(lambda x: (x == 0).sum()).reset_index(name='nb_zero')
    combo_total = combo_group.count().reset_index(name='total')

    combo_stats = pd.merge(combo_zero, combo_total, on=['id_medicament', 'mois_num', 'jour_semaine'])
    combo_stats['proba_zero'] = combo_stats['nb_zero'] / combo_stats['total']

    # Mapper les noms des jours de la semaine pour affichage
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    combo_stats['jour_semaine'] = combo_stats['jour_semaine'].map(dict(enumerate(jours)))

    # Étape 3 : projection pour les 6 mois à venir
    last_date = overview_df['date_de_vente'].max()
    next_months = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=6, freq='MS')
    mois_numeros = next_months.month
    mois_annees = next_months.year

    # Générer toutes les combinaisons possibles
    unique_meds = combo_stats['id_medicament'].unique()
    jours_semaine = combo_stats['jour_semaine'].unique()
    combinations = list(product(unique_meds, zip(mois_annees, mois_numeros), jours_semaine))

    forecast_rows = []

    # Étape 4 : construire la table de prévision avec dégradation hebdomadaire
    for med_id, (annee, mois), jour in combinations:
        match = combo_stats[
            (combo_stats['id_medicament'] == med_id) &
            (combo_stats['mois_num'] == mois) &
            (combo_stats['jour_semaine'] == jour)
        ]
        base_proba = match['proba_zero'].values[0] if not match.empty else 0.0

        for semaine_idx in range(4):  # environ 4 semaines par mois
            adjusted_proba = max(base_proba - 0.01 * semaine_idx, 0)
            forecast_rows.append({
                'id_medicament': med_id,
                'annee': annee,
                'mois': mois,
                'jour_semaine': jour,
                'semaine_du_mois': semaine_idx + 1,
                'proba_zero': adjusted_proba
            })

    forecast_df = pd.DataFrame(forecast_rows)

    # Choisir un médicament au hasard parmi ceux de la prévision
    # med_random = random.choice(forecast_df['id_medicament'].unique())

    # Filtrer les données pour ce médicament
    med_data = forecast_df[forecast_df['id_medicament'] == medicament_to_predict["id_medicament"]].copy()

    # Créer une date synthétique pour l'axe des x : début de chaque semaine du mois
    med_data['date_synthetique'] = pd.to_datetime({
        'year': med_data['annee'],
        'month': med_data['mois'],
        'day': 1
    }) + pd.to_timedelta((med_data['semaine_du_mois'] - 1) * 7, unit='D')

    # Regrouper par date synthétique en prenant la moyenne des probabilités sur tous les jours de la semaine
    agg_data = med_data.groupby('date_synthetique')['proba_zero'].mean().reset_index()

    with col2:
        # Tracer avec matplotlib
        fig_stock_prediction = px.line(
            agg_data,
            x="date_synthetique",
            y="proba_zero",
            markers=True,
            title=f"Évolution des probabilités de rupture de stocks - {medicament_to_predict['nom']}"
        )
        fig_stock_prediction.update_layout(
            xaxis_title="Date",
            yaxis_title="Probabilité de rupture",
            title={
                'y':0.95,                              
                'x':0.5,                               
                'xanchor': 'center',                   
                'yanchor': 'top'                      
            }, 
            plot_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='lightgrey'),
            yaxis=dict(showgrid=True, gridcolor='lightgrey'),
            height=315,
            margin=dict(l=0, r=0, t=30, b=0),
        )
        st.plotly_chart(fig_stock_prediction, use_container_width=True)

    st.markdown("""</div>""", unsafe_allow_html=True)

    # PREDICTION DE RETARD DE LIVRAISON
    # Titre de Prédiction du risque de retard de livraison par fournisseur
    # html("""
    # <style>
    #     @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
        
    # .box {
    #     color: #0A9548;
    #     font-family: 'Quicksand', cursive;
    #     font-weight: bold;
    #     font-size: 27px;
    #     margin-top:4rem;
    #     margin-bottom:-7rem;
    #     text-align: left;
    # }
    # </style>
    # <p class="box">Prédiction du risque de retard de livraison par fournisseur</p>
    # """)
    
    col1, col2, col3 = st.columns(3)
    st.markdown("""
        <style>
        .metric-box {
            background-color: #1e1e26;
            border-left: 5px solid #00cc66;
            border-radius: 12px;
            padding: 16px 20px;
            margin: 8px 0;
            color: white;
            box-shadow: 0 0 4px rgba(0,0,0,0.2);
        }
        .metric-label {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
    # Selecting features and target
    features = ['nom', 'Quantity_arrival', 'fournisseur']
    target = 'retard_jour'
    df_medicament = pd.DataFrame(dashboard_views.medicament_docs)
    # Prepare feature matrix X and target vector y
    X = df_medicament[features].copy()
    y = df_medicament[target]

    # Encode categorical features
    label_encoders = {}
    for col in ['nom', 'fournisseur']:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        label_encoders[col] = le

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train XGBoost regressor
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict on test set and calculate RMSE
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred)
    rmse /= 100

    # Fonction pour faire une prédiction à partir de nouvelles valeurs
    def predire_retard(nom, quantity_arrival, fournisseur):
        # Encodage des variables catégorielles avec les encodeurs précédents
        try:
            nom_encoded = label_encoders['nom'].transform([nom])[0]
            fournisseur_encoded = label_encoders['fournisseur'].transform([fournisseur])[0]
        except ValueError as e:
            return str(e)  # retourne une erreur si la valeur n'a pas été vue pendant l'entraînement

        # Construction du vecteur d'entrée
        input_data = pd.DataFrame([[nom_encoded, quantity_arrival, fournisseur_encoded]],
                                columns=['nom', 'Quantity_arrival', 'fournisseur'])

        # Prédiction
        predicted_retard = model.predict(input_data)[0]
        if predicted_retard < 0 :
            return 0
        return round(predicted_retard, 2)

    # Exemple de prédiction
    example_prediction = predire_retard(medicament_to_predict["nom"], medicament_to_predict["Quantity_arrival"], medicament_to_predict["fournisseur"])

    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div style="text-align: left; position:absolute;">
                {icons.fournisseur_icon_html}
                </div>
                    <p class="kpi-title" style="font-size:1rem;">Fournisseur principal</p>
                    <p class="kpi-value" style="font-size:1.5rem;">{medicament_to_predict["fournisseur"]}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
   
    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div style="text-align: left; position:absolute;">
                    {icons.prediction_icon_html}
                </div>
                <p class="kpi-title" style="font-size:1rem;">Risque de retard de livraison (jours)</p>
                <p class="kpi-value" style="font-size:1.5rem;">{int(example_prediction)}</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div style="text-align: left; position:absolute;">
                {icons.evaluation_rmse_icon_html}
                </div>
                <p class="kpi-title" style="font-size:1rem;">Évaluation (RMSE)</p>
                <p class="kpi-value" style="font-size:1.5rem;">{rmse:.2f}</p>
            </div>
        """, unsafe_allow_html=True)

# ROTATION DES MEDICAMENTS ----------------------------------------
with st.container():

    col1, col2 = st.columns(2)

    with col1:
        data = medicament_views.medoc_forte_rotation
        df_forte_rotation = pd.DataFrame(data)

        # ✅ Renommage correct des colonnes
        df_forte_rotation.rename(columns={"_id": "Médicaments", "quantite_totale_vendue": "Quantités totales vendues"}, inplace=True)

        df_forte_rotation = df_forte_rotation.sort_values(by="Quantités totales vendues", ascending=False).head(3)

        # CSS pour la carte
        st.markdown("""
            <style>
            .card {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            </style>
            """, unsafe_allow_html=True)

        # Graphique
        fig = px.bar(
            df_forte_rotation,
            x="Quantités totales vendues",
            y="Médicaments",
            orientation='h',
            text="Quantités totales vendues",
            color="Quantités totales vendues",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Médicaments à forte rotation"
        )

        fig.update_layout(
            title=dict(
                text="Médicaments à forte rotation",
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            xaxis_title="Quantités vendues",
            yaxis_title="Médicaments",
            showlegend=False,
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=20, r=20, t=30, b=20),
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        data = medicament_views.medoc_faible_rotation
        df_faible_rotation = pd.DataFrame(data)

        # ✅ Renommage correct des colonnes
        df_faible_rotation.rename(columns={"_id": "Médicaments", "quantite_totale_vendue": "Quantités totales vendues"}, inplace=True)

        df_faible_rotation = df_faible_rotation.sort_values(by="Quantités totales vendues", ascending=False).head(3)

        # CSS pour la carte
        st.markdown("""
            <style>
            .card {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            </style>
            """, unsafe_allow_html=True)

        # Graphique
        fig = px.bar(
            df_faible_rotation,
            x="Quantités totales vendues",
            y="Médicaments",
            orientation='h',
            text="Quantités totales vendues",
            color="Quantités totales vendues",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Médicaments à faible rotation"
        )

        fig.update_layout(
            title=dict(
                text="Médicaments à faible rotation",
                x=0.5,
                xanchor='center',
                font=dict(size=20, color='black')
            ),
            xaxis_title="Quantités vendues",
            yaxis_title="Médicaments",
            showlegend=False,
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",   
            margin=dict(l=0, r=0, t=30, b=0),
            # margin=dict(l=20, r=20, t=50, b=10)
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_traces(textposition='outside')

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# MEDICAMENTS LES PLUS CHERS ET MOINS CHERS -----------------------
col1, col2 = st.columns(2)

with col1:
    data = medicament_views.medoc_plus_cher
    df_medoc_plus_cher = pd.DataFrame(data)
    df_medoc_plus_cher.rename(columns={"nom_medicament": "Médicament", "prix_unitaire" : "Prix unitaire" , "fournisseur" : "Fournisseur" , "lot_id" : "Lot"},inplace=True)
    df_medoc_plus_cher = medicament_views.mettre_en_premier(df_medoc_plus_cher, "Médicament")

    # 👉 1. CSS global (UNE SEULE FOIS)
    st.markdown("""
        <style>
            .custom-card {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
            .custom-card h4 {
                text-align: left;
                margin-top: 0;
                margin-bottom: 20px;
            }
            .table-wrapper {
                overflow-x: auto;
            }
            .custom-table {
                width: 100%;
                border-collapse: collapse;
            }
            .custom-table th, .custom-table td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }
            .custom-table th {
                background-color: #f0f0f0;
                font-weight: bold;
            }
            .custom-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    """, unsafe_allow_html=True)

    # 👉 2. Fonction pour afficher une carte avec titre centré + tableau
    def render_table(df_medoc_plus_cher, titre="Tableau des données"):
        table_html = f"""
        <div class='custom-card'>
            <h4>{titre}</h4>
            <div class='table-wrapper'>
                <table class='custom-table'>
                    <tr>
                        {''.join([f"<th>{col}</th>" for col in df_medoc_plus_cher.columns])}
                    </tr>
                    {''.join([
                        "<tr>" + ''.join([f"<td>{row[col]}</td>" for col in df_medoc_plus_cher.columns]) + "</tr>"
                        for _, row in df_medoc_plus_cher.iterrows()
                    ])}
                </table>
            </div>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)

    # 👉 3. Appel
    if df_medoc_plus_cher.empty:
        st.markdown("""
            <div class='custom-card'>
                <h4>Liste de médicaments les plus chers</h4>
                <p style='text-align:center; color: #888;'>Aucune Data</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        render_table(df_medoc_plus_cher, titre="Liste de médicaments les plus chers")

with col2:
    data = medicament_views.medoc_moins_cher
    df_medoc_moins_cher = pd.DataFrame(data)
    df_medoc_moins_cher.rename(columns={"nom_medicament": "Médicament", "prix_unitaire" : "Prix unitaire" , "fournisseur" : "Fournisseur" , "lot_id" : "Lot"},inplace=True)
    df_medoc_moins_cher = medicament_views.mettre_en_premier(df_medoc_moins_cher, "Médicament")
    # 👉 1. CSS global (UNE SEULE FOIS)
    st.markdown("""
        <style>
            .custom-card {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
            .custom-card h4 {
                text-align: left;
                margin-top: 0;
                margin-bottom: 20px;
            }
            .table-wrapper {
                overflow-x: auto;
            }
            .custom-table {
                width: 100%;
                border-collapse: collapse;
            }
            .custom-table th, .custom-table td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }
            .custom-table th {
                background-color: #f0f0f0;
                font-weight: bold;
            }
            .custom-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    """, unsafe_allow_html=True)

    # 👉 2. Fonction pour afficher une carte avec titre centré + tableau
    def render_table(df_medoc_moins_cher, titre="Tableau des données"):
        table_html = f"""
        <div class='custom-card'>
            <h4>{titre}</h4>
            <div class='table-wrapper'>
                <table class='custom-table'>
                    <tr>
                        {''.join([f"<th>{col}</th>" for col in df_medoc_moins_cher.columns])}
                    </tr>
                    {''.join([
                        "<tr>" + ''.join([f"<td>{row[col]}</td>" for col in df_medoc_moins_cher.columns]) + "</tr>"
                        for _, row in df_medoc_moins_cher.iterrows()
                    ])}
                </table>
            </div>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)

    # 👉 3. Appel
    if df_medoc_moins_cher.empty:
        st.markdown("""
            <div class='custom-card'>
                <h4>Liste de médicaments les moins chers</h4>
                <p style='text-align:center; color: #888;'>Aucune Data</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        render_table(df_medoc_moins_cher, titre="Liste de médicaments les moins chers")


# STOCK DE MEDICAMENTS ---------------------------------------------
col1,col2 = st.columns(2)
with col1 :

# ✅ Données 
    Data = medicament_views.medoc_critique_result
    critique = pd.DataFrame(list(Data))
    critique["lots"]= critique["lots"][0][0]["lot_id"]
    critique.rename(columns={"_id": "Médicament", "total_quantite": "Quantités restantes", "lots":"Lot"}, inplace=True)

    st.markdown("""
        <style>
            .custom-card {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
            .custom-card h4 {
                text-align: left;
                margin-top: 0;
                margin-bottom: 20px;
            }
            .table-wrapper {
                overflow-x: auto;
            }
            .custom-table {
                width: 100%;
                border-collapse: collapse;
            }
            .custom-table th, .custom-table td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }
            .custom-table th {
                background-color: #f0f0f0;
                font-weight: bold;
            }
            .custom-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    """, unsafe_allow_html=True)

    # 👉 2. Fonction pour afficher une carte avec titre centré + tableau
    def render_table(critique, titre="Tableau des données"):
        table_html = f"""
        <div class='custom-card'>
            <h4>{titre}</h4>
            <div class='table-wrapper'>
                <table class='custom-table'>
                    <tr>
                        {''.join([f"<th>{col}</th>" for col in critique.columns])}
                    </tr>
                    {''.join([
                        "<tr>" + ''.join([f"<td>{row[col]}</td>" for col in critique.columns]) + "</tr>"
                        for _, row in critique.iterrows()
                    ])}
                </table>
            </div>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)

    # 👉 3. Appel
    if critique.empty:
        st.markdown("""
            <div class='custom-card'>
                <h4>Rupture du stock sur derniers mois</h4>
                <p style='text-align:center; color: #888;'>Aucune Data</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        render_table(critique, titre="Médicaments -70 Unités en stock")

with col2:
    data = medicament_views.medoc_surplus_result
    df_surplus = pd.DataFrame(data)
    df_surplus["lots"]= df_surplus["lots"][0][0]["lot_id"]
    df_surplus.rename(columns={"_id":"Médicaments","total_quantite":"Quantités restantes", "lots":"Lot"},inplace=True)

    # 👉 1. CSS global (UNE SEULE FOIS)
    st.markdown("""
        <style>
            .custom-card {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 30px;
            }
            .custom-card h4 {
                text-align: left;
                margin-top: 0;
                margin-bottom: 20px;
            }
            .table-wrapper {
                overflow-x: auto;
            }
            .custom-table {
                width: 100%;
                border-collapse: collapse;
            }
            .custom-table th, .custom-table td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }
            .custom-table th {
                background-color: #f0f0f0;
                font-weight: bold;
            }
            .custom-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    """, unsafe_allow_html=True)

    # 👉 2. Fonction pour afficher une carte avec titre centré + tableau
    def render_table(df_surplus, titre="Tableau des données"):
        table_html = f"""
        <div class='custom-card'>
            <h4>{titre}</h4>
            <div class='table-wrapper'>
                <table class='custom-table'>
                    <tr>
                        {''.join([f"<th>{col}</th>" for col in df_surplus.columns])}
                    </tr>
                    {''.join([
                        "<tr>" + ''.join([f"<td>{row[col]}</td>" for col in df_surplus.columns]) + "</tr>"
                        for _, row in df_surplus.iterrows()
                    ])}
                </table>
            </div>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)

    # 👉 3. Appel
    if df_surplus.empty:
        st.markdown("""
            <div class='custom-card'>
                <h4>Rupture du stock sur derniers mois</h4>
                <p style='text-align:center; color: #888;'>Aucune Data</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        render_table(df_surplus, titre="Médicaments +700 Unités en stock")


# MEDICAMENTS EN RUPTURE DE STOCK ---------------------------------
data = medicament_views.rupture_stock
df_rupture = pd.DataFrame(data)
df_rupture.rename(columns={"_id" : "Lot", "Derniere Vente": "Dernière vente", "categorie" : "Catégorie"},inplace=True)
df_rupture.drop(columns=["Rupture"], inplace=True)
df_rupture = medicament_views.mettre_en_premier(df_rupture, "Médicament") 
# 👉 1. CSS global (UNE SEULE FOIS)
st.markdown("""
    <style>
        .custom-card {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        .custom-card h4 {
            text-align: left;
            margin-top: 0;
            margin-bottom: 20px;
        }
        .table-wrapper {
            overflow-x: auto;
        }
        .custom-table {
            width: 100%;
            border-collapse: collapse;
        }
        .custom-table th, .custom-table td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        .custom-table th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        .custom-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
""", unsafe_allow_html=True)

# 👉 2. Fonction pour afficher une carte avec titre centré + tableau
def render_table(df_rupture, titre="Tableau des données"):
    table_html = f"""
    <div class='custom-card'>
        <h4>{titre}</h4>
        <div class='table-wrapper'>
            <table class='custom-table'>
                <tr>
                    {''.join([f"<th>{col}</th>" for col in df_rupture.columns])}
                </tr>
                {''.join([
                    "<tr>" + ''.join([f"<td>{row[col]}</td>" for col in df_rupture.columns]) + "</tr>"
                    for _, row in df_rupture.iterrows()
                ])}
            </table>
        </div>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

# 👉 3. Appel
if df_rupture.empty:
    st.markdown("""
        <div class='custom-card'>
            <h4>Rupture du stock sur derniers mois</h4>
            <p style='text-align:center; color: #888;'>Aucune Data</p>
        </div>
    """, unsafe_allow_html=True)
else:
    render_table(df_rupture, titre="Rupture de stock sur les derniers mois")


# import streamlit as st
# import pandas as pd

# # Données de stock (exemple actuel et précédent)
# data = {
#     "Médicament": ["Paracétamol", "Ibuprofène", "Amoxicilline", "Aspirine"],
#     "Stock actuel": [50, 20, 35, 5],
#     "Stock précédent": [45, 30, 40, 10]
# }

# df = pd.DataFrame(data)

# # ➕ Calcul de variation %
# df["Évolution (%)"] = ((df["Stock actuel"] - df["Stock précédent"]) / df["Stock précédent"]) * 100
# df["Évolution (%)"] = df["Évolution (%)"].round(2)

# # 💡 Fonction pour style d'évolution (avec emoji et couleur)
# def format_variation(val):
#     if val > 0:
#         return f"🟢 +{val}%"
#     elif val < 0:
#         return f"🔴 {val}%"
#     else:
#         return f"⚪  0%"

# df["Évolution"] = df["Évolution (%)"].apply(format_variation)

# # 🧼 Suppression de la colonne brute
# df_affichage = df[["Médicament", "Stock actuel", "Stock précédent", "Évolution"]]

# # 🎨 CSS custom pour style carte
# st.markdown("""
# <style>
# .metric-table td {
#     padding: 0.5em 1em;
#     font-size: 1.1em;
# }
# .metric-table th {
#     background-color: #f0f2f6;
#     padding: 0.5em 1em;
#     font-size: 1.1em;
# }
# </style>
# """, unsafe_allow_html=True)

# # Affichage HTML simulé
# st.markdown("<h3>📦 Suivi des stocks par médicament</h3>", unsafe_allow_html=True)
# st.markdown(df_affichage.to_html(classes="metric-table", index=False, escape=False), unsafe_allow_html=True)



# # 🎯 Filtres
# with st.sidebar:
#     st.header("🔍 Filtres")
#     medicament_list = critique["Médicament"].unique()
#     selected_medicaments = st.multiselect(
#         "Nom du médicament",
#         options=medicament_list,
#         default=medicament_list
#     )

# # # 🎯 Application des filtres
# # filtered_df = critique[critique["Médicament"].isin(selected_medicaments)]

# # 💅 CSS personnalisé
# st.markdown("""
#     <style>
#     .ag-root-wrapper {
#         border-radius: 20px;
#         font-family: Arial, sans-serif;
#         overflow: hidden;
#         box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
#     }
#     .ag-header, .ag-cell {
#         font-family: Arial, sans-serif;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # 🎨 Affichage du tableau avec AgGrid
# st.subheader("Médicaments filtrés")
# gb = GridOptionsBuilder.from_dataframe(filtered_df)
# gb.configure_default_column(filter=True, sortable=True, resizable=True, editable=False)
# gb.configure_grid_options(domLayout='normal')
# grid_options = gb.build()

# AgGrid(
#     filtered_df,
#     gridOptions=grid_options,
#     theme='material',  # autres options : 'streamlit', 'alpine', 'balham'
#     fit_columns_on_grid_load=True,
#     height=300,
#     width='100%'
# )


# ✅ Données 
# Data = medicament_views.medoc_surplus_result
# surplus = pd.DataFrame(list(Data))
# surplus["lots"]= surplus["lots"][0][0]["lot_id"]
# surplus.rename(columns={"_id": "Médicament", "total_quantite": "Total quantite"}, inplace=True)

# st.title("💊 Tableau des Médicaments sur plus")
# # 🎯 Filtres
# with st.sidebar:
#     st.header("🔍 Filtres")
#     medicament_list = surplus["Médicament"].unique()
#     selected_medicaments = st.multiselect(
#         "Nom du médicament",
#         options=medicament_list,
#         default=medicament_list
#     )

# # 🎯 Application des filtres
# filtered_df = surplus[surplus["Médicament"].isin(selected_medicaments)]

# # 💅 CSS personnalisé
# st.markdown("""
#     <style>
#     .ag-root-wrapper {
#         border-radius: 20px;
#         font-family: Arial, sans-serif;
#         overflow: hidden;
#         box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
#     }
#     .ag-header, .ag-cell {
#         font-family: Arial, sans-serif;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # 🎨 Affichage du tableau avec AgGrid
# st.subheader("Médicaments filtrés")
# gb = GridOptionsBuilder.from_dataframe(filtered_df)
# gb.configure_default_column(filter=True, sortable=True, resizable=True, editable=False)
# gb.configure_grid_options(domLayout='normal')
# grid_options = gb.build()

# AgGrid(
#     filtered_df,
#     gridOptions=grid_options,
#     theme='material',  # autres options : 'streamlit', 'alpine', 'balham'
#     fit_columns_on_grid_load=True,
#     height=300,
#     width='100%'
# )
# 🎯 Filtres


