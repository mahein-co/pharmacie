from datetime import timedelta
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit.components.v1 import html
import math

import pandas as pd
import plotly.express as px
from utils import load_data
import streamlit as st

from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.metrics import mean_squared_error

from datetime import timedelta,date

from data.mongodb_ip_manager import MongoDBIPManager
from data import mongodb_pipelines
from streamlit.components.v1 import html
from data.mongodb_client import MongoDBClient
from itertools import product
from pipelines import pipelines_ventes

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
    if st.button("Recharger les données", key="reload", help="Cliquez pour recharger les données", use_container_width=True):
        st.cache_data.clear()
    st.sidebar.image("assets/images/logoMahein.png", caption="", use_container_width=True)

# -----------------------------------------------------------------
# DASHBOARD TITLE
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
<div class="box">Dashboard</div>
""")

# importation de style CSS
st.markdown(dashboard_views.custom_css, unsafe_allow_html=True)
st.markdown(dashboard_views.table_css, unsafe_allow_html=True)
st.markdown(dashboard_views.kpis_style, unsafe_allow_html=True)


# Charger les données
data = dashboard_views.medicaments_expires
df = pd.DataFrame(data)

# I- 6 FIRST SCORECARD
if dashboard_views.employe_collection and dashboard_views.overview_collection and dashboard_views.medicament_collection:
    # 1. DAHSBOARD --------------------------------------------
    st.markdown(dashboard_views.three_first_kpis_html, unsafe_allow_html=True)

    # 2. EMPLOYEES --------------------------------------------
    st.markdown(dashboard_views.clustering_employees_style, unsafe_allow_html=True)
    employe_df = pd.DataFrame(list(employe_views.employe_documents))
    employe_df['date_embauche'] = pd.to_datetime(employe_df['date_embauche'], errors='coerce')

    # Calculate ancienneté in years
    today = pd.Timestamp(datetime.today())
    employe_df['anciennete'] = (today - employe_df['date_embauche']).dt.days / 365.25

    # Remove duplicates by keeping the most recent 'date_embauche' per 'id_employe'
    employe_df_unique = employe_df.sort_values('date_embauche').drop_duplicates(subset='id_employe', keep='last')

    # Keep only relevant columns for analysis
    employe_df_analysis = employe_df_unique[['anciennete', 'salaire']].dropna()
    employe_correlation = employe_df_analysis.corr().loc['anciennete', 'salaire']

    # Clustering with KMeans
    employe_clustering_plot = px.scatter(
        employe_df_analysis,
        x="anciennete",
        y="salaire",
        color="salaire",
        size="salaire",
        template="simple_white",
        title=f"Correlation: {employe_correlation}"
    )
    employe_clustering_plot.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  
        plot_bgcolor="rgba(0,0,0,0)",   
        margin=dict(l=0, r=0, t=30, b=0),
        height=380,
        title={
            'y':0.95,                              
            'x':0.5,                               
            'xanchor': 'center',                   
            'yanchor': 'top'                      
        },
        title_font=dict(
            size=20,            
            color='#817d7d',
            weight=400,      
            family='Arial'     
        )
    )

    col_metrics, col_clustering = st.columns([1, 3])
    with col_metrics:
        st.markdown(dashboard_views.total_all_employes_html, unsafe_allow_html=True)
    with col_clustering:    
        st.plotly_chart(employe_clustering_plot, use_container_width=True)

    # 3. MEDICAMENTS --------------------------------------------
    # Renommer les colonnes
    df.rename(columns={
        "_id": "Lots",
        "nom_medicament": "Médicament",
        "date_expiration": "Date d'expiration",
        "quantite_totale_restante": "Quantite restante",
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
    search = st.text_input("Rechercher un médicament :")

    # Filtrage selon la recherche
    if search:
        df = df[df.astype(str).apply(lambda row: row.str.contains(search, case=False), axis=1).any(axis=1)]

    # 🎨 CSS tableau stylisé
    st.markdown(
        """
        <style>
        .table-wrapper {
            border-radius: 12px;
            overflow: hidden;
            margin-top: -20px;
            margin-bottom: 10px;
        }
        .custom-table {
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
            color: black;
        }
        .custom-table th {
            background-color: #eee;
            color: #050505;
            padding: 10px;
            text-align: left;
        }
        .custom-table td {
            padding: 10px;
            color: black;
            vertical-align: middle;
        }
        .custom-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .custom-table tr:nth-child(odd) {
            background-color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # 🔢 Pagination : affichage tableau avec page
    # Valeurs disponibles
    rows_per_page_options = [5, 10]
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

    # 📊 Affiche le tableau filtré et paginé
    render_table(df_page)

    # 📄 Bas de tableau : choix nombre de lignes et navigation
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


# PREDICTION DE RUPTURE DE STOCK
# Étape 1 : préparation des colonnes nécessaires
overview_docs = dashboard_views.overview_collection.find_all_documents()
overview_df = pd.DataFrame(overview_docs)
overview_df['jour_semaine'] = overview_df['date_de_vente'].dt.dayofweek  # 0 = Lundi, 6 = Dimanche
overview_df['mois_num'] = overview_df['date_de_vente'].dt.month


with st.container():
    st.markdown("<h3>Prediction rupture de meducaments</h3>", unsafe_allow_html=True)

    # Étape 1 : préparation des colonnes nécessaires
    overview_df['jour_semaine'] = overview_df['date_de_vente'].dt.dayofweek  # 0 = Lundi, 6 = Dimanche
    overview_df['mois_num'] = overview_df['date_de_vente'].dt.month

    # Étape 2 : calcul des probabilités historiques par mois et jour de semaine
    combo_group = overview_df.groupby(['lot_id', 'mois_num', 'jour_semaine'])['quantite']
    combo_zero = combo_group.apply(lambda x: (x == 0).sum()).reset_index(name='nb_zero')
    combo_total = combo_group.count().reset_index(name='total')

    combo_stats = pd.merge(combo_zero, combo_total, on=['lot_id', 'mois_num', 'jour_semaine'])
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
    unique_meds = combo_stats['lot_id'].unique()
    jours_semaine = combo_stats['jour_semaine'].unique()
    combinations = list(product(unique_meds, zip(mois_annees, mois_numeros), jours_semaine))

    forecast_rows = []

    # Étape 4 : construire la table de prévision avec dégradation hebdomadaire
    for med_id, (annee, mois), jour in combinations:
        match = combo_stats[
            (combo_stats['lot_id'] == med_id) &
            (combo_stats['mois_num'] == mois) &
            (combo_stats['jour_semaine'] == jour)
        ]
        base_proba = match['proba_zero'].values[0] if not match.empty else 0.0

        for semaine_idx in range(4):  # environ 4 semaines par mois
            adjusted_proba = max(base_proba - 0.01 * semaine_idx, 0)
            forecast_rows.append({
                'lot_id': med_id,
                'annee': annee,
                'mois': mois,
                'jour_semaine': jour,
                'semaine_du_mois': semaine_idx + 1,
                'proba_zero': adjusted_proba
            })

    forecast_df = pd.DataFrame(forecast_rows)

    
    # Fusionner noms des médicaments
    df_meds = overview_df[['lot_id', 'nom_medicament']].drop_duplicates()
    forecast_df = forecast_df.merge(df_meds, on='lot_id', how='left')

    # Interface utilisateur
    medicament_choisi = st.selectbox("Choisir un médicament", forecast_df['nom_medicament'].unique())

    # Filtrer les données
    med_data = forecast_df[forecast_df['nom_medicament'] == medicament_choisi].copy()

    # Création de la date synthétique
    med_data['date_synthetique'] = pd.to_datetime({
        'year': med_data['annee'],
        'month': med_data['mois'],
        'day': 1
    }) + pd.to_timedelta((med_data['semaine_du_mois'] - 1) * 7, unit='D')

    # Agrégation
    agg_data = med_data.groupby('date_synthetique')['proba_zero'].mean().reset_index()

    # Tracer avec matplotlib
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(agg_data['date_synthetique'], agg_data['proba_zero'], marker='o')
    ax.set_title(f"Évolution des probabilités de rupture - {medicament_choisi}")
    ax.set_xlabel("Date (approx. début de semaine)")
    ax.set_ylabel("Probabilité de rupture")
    ax.grid(True)
    st.pyplot(fig)


# with st.container():
#     st.markdown("<h3>Prediction fournisseurs</h3>", unsafe_allow_html=True)
#     col1,col2 = st.columns(2)
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
#         return round(predicted_retard, 2)

#     # Exemple de prédiction
#     example_prediction = predire_retard("Paracétamol", 700, "PharmaPlus")

#     with col1:
#         st.markdown(f"""
#             <div class="kpi-card">
#                 <div class="kpi-title" style="font-size:1.2rem;">rmse</div>
#                 <div class="kpi-value" style="font-size:2rem;">{rmse:.2f}</div>
#             </div>
#         """, unsafe_allow_html=True)

#     with col2:
#         st.markdown(f"""
#             <div class="kpi-card">
#                 <div class="kpi-title" style="font-size:1.2rem;">prediction</div>
#                 <div class="kpi-value" style="font-size:2rem;">{example_prediction:.2f}</div>
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
