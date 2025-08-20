import streamlit as st
from streamlit.components.v1 import html
import math

import pandas as pd
import streamlit as st


from data.mongodb_ip_manager import MongoDBIPManager
from streamlit.components.v1 import html

from pipelines import pipeline_overview
from style import style, icons

# views
from views import dashboard_views, employe_views 

st.markdown("""
    <style>
        [data-testid="stToolbar"] [aria-label="Settings"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# Initialisation
st.set_page_config(page_title="Dashboard Pharmacie", layout="wide")
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">', unsafe_allow_html=True)

# importation de style CSS
st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.table_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)


# PING IP
def mongodb_ip_manager():   
    manager = MongoDBIPManager()

    current_ip = manager.get_current_ip()
    if current_ip:
        if not manager.ip_exists(current_ip):
            manager.add_ip(current_ip)
mongodb_ip_manager()

# Chargement CSS
with open("style/pharmacie.css", "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.sidebar.image("assets/images/logoMahein.png", caption="", use_container_width=True)

# -----------------------------------------------------------------
# DASHBOARD TITLE
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
    <div class="box">Overview</div>
    """)

# Filtre de date
with col_filter:
    col1,col2 = st.columns(2)
    # --- Inputs utilisateur ---
    with col1:
        date_debut = st.date_input("Date de début du filtre", value=None)
    with col2:
        date_fin = st.date_input("Date de fin du filtre", value=None, min_value=(date_debut))

# Charger les données
data = dashboard_views.medicaments_expires
df = pd.DataFrame(data)

# SCORECARD KPIS -----------------------------------------
# 1. chriffres d'affraire
if date_debut and date_fin:
    chiffre_affaire = pipeline_overview.get_chiffre_affaire_total(start_date=date_debut, end_date=date_fin)
chiffre_affaire = pipeline_overview.get_chiffre_affaire_total()

if date_debut and date_fin:
    nombre_ventes = pipeline_overview.get_nombre_de_ventes(start_date=date_debut, end_date=date_fin)
nombre_ventes = pipeline_overview.get_nombre_de_ventes()
nombre_ventes_str = f"{nombre_ventes:,}".replace(",", " ")
# I- 6 FIRST SCORECARD
if dashboard_views.employe_collection and dashboard_views.overview_collection and dashboard_views.medicament_collection:
    # 1. DAHSBOARD --------------------------------------------
    three_first_kpis_html = f"""
        <div class="kpi-container">
            <div class="kpi-card">
            <div style="text-align: left; position:absolute;">
            {icons.finance_icon_html}
            </div>
                <p class="kpi-title" style="font-size:1rem;">Chiffre d'affaires (MGA)</p>
                <p class="kpi-value" style="font-size:1.5rem;">{chiffre_affaire}</p>
            </div>
            <div class="kpi-card">
            <div style="text-align: left; position:absolute;">
            {icons.stock_icon_html}
            </div>
                <p class="kpi-title" style="font-size:1rem;">Valeur des stocks (MGA)</p>
                <p class="kpi-value" style="font-size:1.5rem;">{f"{int(dashboard_views.valeur_totale_stock):,}".replace(",", " ")}</p>
            </div>
            <div class="kpi-card">
            <div style="text-align: left; position:absolute;">
            {icons.perte_icon_html}
            </div>
            <p class="kpi-title" style="font-size:1rem; color:#48494B;">
                Pertes (MGA)
            </p>
            <p class="kpi-value" style="font-size:1.5rem;">{f"{int(dashboard_views.total_pertes_medicaments):,}".replace(",", " ")}</p>
            </div>

        </div>
    """

    three_second_kpis_html = f"""
        <div class="kpi-container-secondary">
            <div class="kpi-card">
            <div style="text-align: left; position:absolute;">
            {icons.employees_icon_html}
            </div>
                <p class="kpi-title" style="font-size:1rem;">Nombre d'employés</p>
                <p class="kpi-value" style="font-size:1.5rem;">{employe_views.Nb_employers}</p>
            </div>
            <div class="kpi-card">
            <div style="text-align: left; position:absolute;">
            {icons.ventes_icon_html}
            </div>
                <p class="kpi-title" style="font-size:1rem;">Nombre de ventes</p>
                <p class="kpi-value" style="font-size:1.6rem;">{nombre_ventes_str}
            </div>
            <div class="kpi-card">
            <div style="text-align: left; position:absolute;">
            {icons.fournisseur_icon_html}
            </div>
                <p class="kpi-title" style="font-size:1rem;">Nombre de fournisseurs</p>
                <p class="kpi-value" style="font-size:1.5rem;">{pipeline_overview.nb_fournisseur}</p>
            </div>

        </div>
    """
    st.markdown(three_first_kpis_html, unsafe_allow_html=True)
    st.markdown(three_second_kpis_html, unsafe_allow_html=True)


    # 3. MEDICAMENTS --------------------------------------------
    # Renommer les colonnes
    df.rename(columns={
        "_id": "Lot",
        "nom_medicament": "Médicament",
        "date_expiration": "Date d'expiration",
        "quantite_totale_restante": "Quantité restante",
        "jours_restants": "Jours restants"
    }, inplace=True)

    # Fonction pour le statut
    def get_status(jours):
        if jours < 1:
            color = "#f44336"
            text = "Déjà expiré"
        elif jours < 50:
            color = "#ff9800"
            text = f"Dans {jours} jours"
        else:
            color = "#4caf50"
            text = f"Dans {jours} jours"
        return f"""
        <div style="
            background-color: {color};
            color: white;
            text-decoration:uppercase;
            padding: 6px 12px;
            border-radius: 12px;
            font-weight: normal;
            display: inline-block;
            min-width: 100px;
            text-align: center;
        ">{text}</div>
        """

    df["Status"] = df["Jours restants"].apply(get_status)

    # 🔍 Barre de recherche en haut
    st.markdown(style.placeholder_style, unsafe_allow_html=True)
    # Champ texte avec placeholder
    search = st.text_input("Recherche", placeholder="Rechercher un médicament déjà ou bientôt expiré", label_visibility="collapsed")

    # Filtrage selon la recherche
    if search:
        df = df[df.astype(str).apply(lambda row: row.str.contains(search, case=False), axis=1).any(axis=1)]

    # 🎨 CSS tableau stylisé
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
            text-align: center;
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

    # 🔢 Pagination : affichage tableau avec page
    # Valeurs disponibles
    rows_per_page_options = [5]
    # Valeur par défaut
    rows_per_page = st.session_state.get("rows_per_page", 5)

    # Nombre total de pages
    total_rows = len(df)
    total_pages = math.ceil(total_rows / rows_per_page)

    # Index de page courant
    current_page = st.session_state.get("current_page", 1)
    start = (current_page - 1) * rows_per_page
    end = start + rows_per_page
    df_page = df.iloc[start:end]

    # 🧾 Affichage tableau
    def render_table(df_part):
        table_html = "<div class='table-wrapper'><table class='custom-table'>"
        table_html += "<tr>" + "".join([f"<th>{col}</th>" for col in df_part.columns]) + "</tr>"
        for _, row in df_part.iterrows():
            table_html += "<tr>"
            for col in df_part.columns:
                table_html += f"<td>{row[col]}</td>"
            table_html += "</tr>"
        table_html += "</table></div>"
        st.markdown(table_html, unsafe_allow_html=True)
    if df.empty:
        st.markdown("""
        <div class='custom-card'>
            <h4>Médicaments expiré</h4>
            <p style='text-align:center; color: #888;'>Aucune Data</p>
        </div>
    """, unsafe_allow_html=True)
    else:
    # Affiche le tableau filtré et paginé
        render_table(df_page)

    # Bas de tableau : choix nombre de lignes et navigation
    col1, col2 = st.columns(2)

    with col1:
        rows_per_page = st.selectbox("Afficher par page :", rows_per_page_options, index=rows_per_page_options.index(rows_per_page))
        st.session_state["rows_per_page"] = rows_per_page
        total_pages = math.ceil(len(df) / rows_per_page)  # Recalcul après changement

    with col2:
        current_page = st.number_input(f"Page (1-{total_pages})", min_value=1, max_value=total_pages, value=current_page, step=1)
        st.session_state["current_page"] = current_page

else:
    st.error("Il est impossible de charger les données depuis la database.")


# # PREDICTION DE RUPTURE DE STOCK
# # Étape 1 : préparation des colonnes nécessaires
# overview_df = pd.DataFrame(dashboard_views.vente_docs)
# overview_df['jour_semaine'] = overview_df['date_de_vente'].dt.dayofweek  # 0 = Lundi, 6 = Dimanche
# overview_df['mois_num'] = overview_df['date_de_vente'].dt.month

# # Medicament dataframe
# medicament_df = pd.DataFrame(dashboard_views.medicament_docs)
# # Get unique id_medicament and nom
# medicament_df = medicament_df.drop_duplicates(subset=['id_medicament'])
# medicament_df = medicament_df[['id_medicament', 'nom', 'prix_unitaire', 'fournisseur', 'prix_fournisseur', 'Quantity_arrival']]
# medifcament_to_filter = medicament_df.to_dict(orient="records")

# def get_medicament_to_predict(medicament_choisi):
#     if not medicament_choisi:
#         return medifcament_to_filter[0]

#     medicament_to_predict = next((item for item in medifcament_to_filter if item["nom"] == medicament_choisi), None)
#     return medicament_to_predict

# with st.container():
#     # Title anticipation de rupture de stock
#     html("""
#     <style>
#         @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
        
#     .box {
#         color: #0A9548;
#         font-family: 'Quicksand', cursive;
#         font-weight: bold;
#         font-size: 35px;
#         margin-top:4rem;
#         margin-bottom:-7rem;
#         text-align: center;
#     }
#     </style>
#     <p class="box">Anticipation des ruptures de stock d’un médicament</p>
#     """)
    
#     col1, col2 = st.columns([1, 3])
#     with col1:
#         options = [item['nom'] for item in medifcament_to_filter]
#         medicament_choisi = st.selectbox("Choisissez un médicament", options)
#         medicament_to_predict = get_medicament_to_predict(medicament_choisi)

#         # Card
#         medicament_info = f"""
#             <div class="kpi-card">
#                 <div style="text-align: left; position:absolute;">
#                 {icons.prix_vente_icon_html}
#                 </div>
#                     <p class="kpi-title" style="font-size:1rem;">Prix Unitaire (MGA)</p>
#                     <p class="kpi-value" style="font-size:1.5rem;">{medicament_to_predict["prix_unitaire"]}</p>
#             </div>
#             <div class="kpi-card">
#                 <div style="text-align: left; position:absolute;">
#                 {icons.prix_fournisseur_icon_html}
#                 </div>
#                     <p class="kpi-title" style="font-size:1rem;">Prix Fournisseur (MGA)</p>
#                     <p class="kpi-value" style="font-size:1.5rem;">{medicament_to_predict["prix_fournisseur"]}</p>
#                 </div>
#             </div>
#         """

#         st.markdown(medicament_info, unsafe_allow_html=True)

#     # Étape 1 : préparation des colonnes nécessaires
#     overview_df['jour_semaine'] = overview_df['date_de_vente'].dt.dayofweek  # 0 = Lundi, 6 = Dimanche
#     overview_df['mois_num'] = overview_df['date_de_vente'].dt.month

#     # Étape 2 : calcul des probabilités historiques par mois et jour de semaine
#     combo_group = overview_df.groupby(['id_medicament', 'mois_num', 'jour_semaine'])['quantite']
#     combo_zero = combo_group.apply(lambda x: (x == 0).sum()).reset_index(name='nb_zero')
#     combo_total = combo_group.count().reset_index(name='total')

#     combo_stats = pd.merge(combo_zero, combo_total, on=['id_medicament', 'mois_num', 'jour_semaine'])
#     combo_stats['proba_zero'] = combo_stats['nb_zero'] / combo_stats['total']

#     # Mapper les noms des jours de la semaine pour affichage
#     jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
#     combo_stats['jour_semaine'] = combo_stats['jour_semaine'].map(dict(enumerate(jours)))

#     # Étape 3 : projection pour les 6 mois à venir
#     last_date = overview_df['date_de_vente'].max()
#     next_months = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=6, freq='MS')
#     mois_numeros = next_months.month
#     mois_annees = next_months.year

#     # Générer toutes les combinaisons possibles
#     unique_meds = combo_stats['id_medicament'].unique()
#     jours_semaine = combo_stats['jour_semaine'].unique()
#     combinations = list(product(unique_meds, zip(mois_annees, mois_numeros), jours_semaine))

#     forecast_rows = []

#     # Étape 4 : construire la table de prévision avec dégradation hebdomadaire
#     for med_id, (annee, mois), jour in combinations:
#         match = combo_stats[
#             (combo_stats['id_medicament'] == med_id) &
#             (combo_stats['mois_num'] == mois) &
#             (combo_stats['jour_semaine'] == jour)
#         ]
#         base_proba = match['proba_zero'].values[0] if not match.empty else 0.0

#         for semaine_idx in range(4):  # environ 4 semaines par mois
#             adjusted_proba = max(base_proba - 0.01 * semaine_idx, 0)
#             forecast_rows.append({
#                 'id_medicament': med_id,
#                 'annee': annee,
#                 'mois': mois,
#                 'jour_semaine': jour,
#                 'semaine_du_mois': semaine_idx + 1,
#                 'proba_zero': adjusted_proba
#             })

#     forecast_df = pd.DataFrame(forecast_rows)

#     # Choisir un médicament au hasard parmi ceux de la prévision
#     # med_random = random.choice(forecast_df['id_medicament'].unique())

#     # Filtrer les données pour ce médicament
#     med_data = forecast_df[forecast_df['id_medicament'] == medicament_to_predict["id_medicament"]].copy()

#     # Créer une date synthétique pour l'axe des x : début de chaque semaine du mois
#     med_data['date_synthetique'] = pd.to_datetime({
#         'year': med_data['annee'],
#         'month': med_data['mois'],
#         'day': 1
#     }) + pd.to_timedelta((med_data['semaine_du_mois'] - 1) * 7, unit='D')

#     # Regrouper par date synthétique en prenant la moyenne des probabilités sur tous les jours de la semaine
#     agg_data = med_data.groupby('date_synthetique')['proba_zero'].mean().reset_index()

#     with col2:
#         # Tracer avec matplotlib
#         fig_stock_prediction = px.line(
#             agg_data,
#             x="date_synthetique",
#             y="proba_zero",
#             markers=True,
#             title=f"Évolution des probabilités de rupture - {medicament_to_predict['nom']}"
#         )
#         fig_stock_prediction.update_layout(
#             xaxis_title="Date",
#             yaxis_title="Probabilité de rupture",
#             title={
#                 'y':0.95,                              
#                 'x':0.5,                               
#                 'xanchor': 'center',                   
#                 'yanchor': 'top'                      
#             }, 
#             plot_bgcolor='white',
#             xaxis=dict(showgrid=True, gridcolor='lightgrey'),
#             yaxis=dict(showgrid=True, gridcolor='lightgrey'),
#             height=315,
#             margin=dict(l=0, r=0, t=30, b=0),
#         )
#         st.plotly_chart(fig_stock_prediction, use_container_width=True)

#     # PREDICTION DE RETARD DE LIVRAISON
#     # Titre de Prédiction du risque de retard de livraison par fournisseur
#     html("""
#     <style>
#         @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
        
#     .box {
#         color: #0A9548;
#         font-family: 'Quicksand', cursive;
#         font-weight: bold;
#         font-size: 35px;
#         margin-top:4rem;
#         margin-bottom:-7rem;
#         text-align: center;
#     }
#     </style>
#     <p class="box">Prédiction du risque de retard de livraison par fournisseur</p>
#     """)
    
#     col1, col2, col3 = st.columns(3)
#     st.markdown("""
#         <style>
#         .metric-box {
#             background-color: #1e1e26;
#             border-left: 5px solid #00cc66;
#             border-radius: 12px;
#             padding: 16px 20px;
#             margin: 8px 0;
#             color: white;
#             box-shadow: 0 0 4px rgba(0,0,0,0.2);
#         }
#         .metric-label {
#             font-size: 16px;
#             font-weight: 500;
#             margin-bottom: 4px;
#         }
#         .metric-value {
#             font-size: 28px;
#             font-weight: bold;
#         }
#         </style>
#         """, unsafe_allow_html=True)
#     # Selecting features and target
#     features = ['nom', 'Quantity_arrival', 'fournisseur']
#     target = 'retard_jour'
#     df_medicament = pd.DataFrame(dashboard_views.medicament_docs)
#     # Prepare feature matrix X and target vector y
#     X = df_medicament[features].copy()
#     y = df_medicament[target]

#     # Encode categorical features
#     label_encoders = {}
#     for col in ['nom', 'fournisseur']:
#         le = LabelEncoder()
#         X[col] = le.fit_transform(X[col])
#         label_encoders[col] = le

#     # Split data into train and test sets
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#     # Initialize and train XGBoost regressor
#     model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
#     model.fit(X_train, y_train)

#     # Predict on test set and calculate RMSE
#     y_pred = model.predict(X_test)
#     rmse = mean_squared_error(y_test, y_pred)
#     rmse /= 100

#     # Fonction pour faire une prédiction à partir de nouvelles valeurs
#     def predire_retard(nom, quantity_arrival, fournisseur):
#         # Encodage des variables catégorielles avec les encodeurs précédents
#         try:
#             nom_encoded = label_encoders['nom'].transform([nom])[0]
#             fournisseur_encoded = label_encoders['fournisseur'].transform([fournisseur])[0]
#         except ValueError as e:
#             return str(e)  # retourne une erreur si la valeur n'a pas été vue pendant l'entraînement

#         # Construction du vecteur d'entrée
#         input_data = pd.DataFrame([[nom_encoded, quantity_arrival, fournisseur_encoded]],
#                                 columns=['nom', 'Quantity_arrival', 'fournisseur'])

#         # Prédiction
#         predicted_retard = model.predict(input_data)[0]
#         if predicted_retard < 0 :
#             return 0
#         return round(predicted_retard, 2)

#     # Exemple de prédiction
#     example_prediction = predire_retard(medicament_to_predict["nom"], medicament_to_predict["Quantity_arrival"], medicament_to_predict["fournisseur"])

#     with col1:
#         st.markdown(f"""
#             <div class="kpi-card">
#                 <div style="text-align: left; position:absolute;">
#                 {icons.fournisseur_icon_html}
#                 </div>
#                     <p class="kpi-title" style="font-size:1rem;">Fournisseur principal</p>
#                     <p class="kpi-value" style="font-size:1.5rem;">{medicament_to_predict["fournisseur"]}</p>
#                 </div>
#             </div>
#         """, unsafe_allow_html=True)
   
#     with col2:
#         st.markdown(f"""
#             <div class="kpi-card">
#                 <div style="text-align: left; position:absolute;">
#                     {icons.prediction_icon_html}
#                 </div>
#                 <p class="kpi-title" style="font-size:1rem;">Risque de retard de livraison (jours)</p>
#                 <p class="kpi-value" style="font-size:1.5rem;">{int(example_prediction)}</p>
#             </div>
#         """, unsafe_allow_html=True)

#     with col3:
#         st.markdown(f"""
#             <div class="kpi-card">
#                 <div style="text-align: left; position:absolute;">
#                 {icons.evaluation_rmse_icon_html}
#                 </div>
#                 <p class="kpi-title" style="font-size:1rem;">Évaluation (RMSE)</p>
#                 <p class="kpi-value" style="font-size:1.5rem;">{rmse:.2f}</p>
#             </div>
#         """, unsafe_allow_html=True)

# with st.container():
#     st.markdown("<h3>Sales forecasting</h3>", unsafe_allow_html=True)

#     # Convertir la date
#     df_vente['date_de_vente'] = pd.to_datetime(df_vente['date_de_vente'])

#     # Jointure pour obtenir les noms des médicaments
#     df_vente = df_vente.merge(df_medicament[['id_medicament', 'nom']], on='id_medicament', how='left')

#     # Agréger par jour et médicament
#     agg_df = df_vente.groupby(['date_de_vente', 'id_medicament'])['quantite'].sum().reset_index()

#     # Pivot pour série temporelle multivariée
#     pivot_df = agg_df.pivot(index='date_de_vente', columns='id_medicament', values='quantite').fillna(0)

#     # Création du dataset pour GluonTS
#     freq = "D"
#     prediction_length_extended = 30
#     all_data_list = []

#     for col in pivot_df.columns:
#         item = {
#             FieldName.START: pivot_df.index.min(),
#             FieldName.TARGET: pivot_df[col].values,
#             FieldName.ITEM_ID: str(col),
#         }
#         all_data_list.append(item)

#     all_dataset = ListDataset(all_data_list, freq=freq)

#     # Entraînement
#     estimator_full = DeepAREstimator(
#         prediction_length=prediction_length_extended,
#         freq=freq,
#         trainer=Trainer(epochs=20, ctx=mx.cpu(), learning_rate=1e-3),
#         distr_output=NegativeBinomialOutput()
#     )
#     predictor_full = estimator_full.train(all_dataset)

#     # Prévision
#     forecast_it, ts_it = make_evaluation_predictions(
#         dataset=all_dataset,
#         predictor=predictor_full,
#         num_samples=100
#     )

#     forecasts_future = list(forecast_it)
#     tss_future = list(ts_it)

#     # Dictionnaire id -> nom
#     id_to_name = df_medicament.set_index('id_medicament')['nom'].to_dict()

#     # Interface utilisateur Streamlit
#     ids = list(pivot_df.columns)
#     names = [id_to_name.get(m_id, f"ID {m_id}") for m_id in ids]
#     selected_name = st.selectbox("Choisir un médicament", names)

#     # Obtenir l’index du médicament sélectionné
#     selected_index = names.index(selected_name)
#     selected_id = ids[selected_index]

#     # Tracer
#     ts = tss_future[selected_index]
#     fcst = forecasts_future[selected_index]

#     start_ts = ts.index[-1].to_timestamp() + timedelta(1)
#     forecast_index = pd.date_range(start=start_ts, periods=prediction_length_extended, freq="D")

#     plt.figure(figsize=(12, 5))
#     plt.plot(ts.index.to_timestamp()[-100:], ts.values[-100:], label="Historique", linewidth=2)
#     plt.plot(forecast_index, fcst.mean, color='green', label="Prévision (moyenne)", linewidth=2)
#     plt.fill_between(forecast_index, fcst.quantile(0.15), fcst.quantile(0.85), color='green', alpha=0.3, label="70% IC")

#     plt.title(f"Prévision 30 jours - {selected_name}")
#     plt.xlabel("Date")
#     plt.ylabel("Quantité vendue")
#     plt.legend()
#     plt.grid()
#     st.pyplot(plt)
