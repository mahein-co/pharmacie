from datetime import timedelta
import streamlit as st
from streamlit.components.v1 import html

import pandas as pd
import plotly.express as px
import duckdb
from utils import load_data
from db import init_duckdb
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

from datetime import timedelta
# from gluonts.dataset.common import ListDataset
# from gluonts.dataset.field_names import FieldName
# from gluonts.mx import DeepAREstimator
# from gluonts.mx.trainer import Trainer
# from gluonts.mx.distribution.neg_binomial import NegativeBinomialOutput
# import mxnet as mx
# from gluonts.evaluation.backtest import make_evaluation_predictions


from data.mongodb_ip_manager import MongoDBIPManager
from data import mongodb_pipelines
from streamlit.components.v1 import html
from data.mongodb_client import MongoDBClient
from itertools import product
from pipelines import pipelines_ventes

# views
from views import dashboard_views 

# Initialisation
st.set_page_config(page_title="Dashboard Pharmacie", layout="wide")
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">', unsafe_allow_html=True)


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


# Chargement des données
df = load_data()

# Sidebar
with st.sidebar:
    if st.button("Recharger les données", key="reload", help="Cliquez pour recharger les données", use_container_width=True):
        st.cache_data.clear()
    st.sidebar.image("images/logoMahein.png", caption="", use_container_width=True)

# -----------------------------------------------------------------
# TITLE
html("""
<style>
    @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
    
  .box {
    color: #eee;
    padding: 20px;
    font-family: 'Dancing Script', cursive;
    border-radius: 10px;
    font-size: 74px;
  }
</style>
<div class="box">Dashboard</div>
""")

# importation de style CSS
# st.markdown(dashboard_views.custom_css, unsafe_allow_html=True)
st.markdown(dashboard_views.kpis_style, unsafe_allow_html=True)


# I- FIRST LINE OF SCORECARD
if dashboard_views.vente_collection and dashboard_views.medicament_collection:
    st.markdown(dashboard_views.kpis_html, unsafe_allow_html=True)

else:
    st.error("Il est impossible de charger les données depuis la database.")


# # II- SECOND LINE OF SCORECARD
# if dashboard_views.medicament_collection and dashboard_views.employe_collection:
#     rows_html = ""
#     for row_medicament in dashboard_views.medicaments_expires[:7]:
#         rows_html += f"""
#         <tr>
#             <td>{row_medicament['nom']}</td>
#             <td>{row_medicament['arrival_date'].strftime('%d-%m-%Y')}</td>
#             <td style="color:red;">{row_medicament['date_expiration'].strftime('%d-%m-%Y')}</td>
#             <td>{row_medicament['prix_unitaire']} Ar</td>
#             <td>{row_medicament['Quantity_arrival']}</td>
#         </tr>
#         """


#     try:
#         # Statistiques générales

#         # AFFICHAGE DESIGN
#         with st.container():

#             col1,col2,col4 = st.columns(3)
#             col1.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-title" style="font-size:1.2rem;">Total Médicaments</div>
#                     <div class="kpi-value" style="font-size:2rem;">{dashboard_views.nb_total_medicaments}</div>
#                 </div>
#             """, unsafe_allow_html=True)


#             col2.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-title" style="font-size:1.2rem;">
#                         Total Pertes
#                         <span style="font-size:0.9rem;">(Médicaments invendus)</span>
#                     </div>
#                     <div class="kpi-value" style="font-size:2rem;">{f"{dashboard_views.total_pertes_medicaments:,}".replace(",", " ")} &nbsp;MGA</div>
#                 </div>
#             """, unsafe_allow_html=True)


#             col4.markdown(f"""
#                 <div class="kpi-card">
#                     <div class="kpi-title" style="font-size:1.2rem;">Total Fournisseurs</div>
#                     <div class="kpi-value" style="font-size:2rem;">{dashboard_views.nb_total_fournisseurs}</div>
#                 </div>
#             """, unsafe_allow_html=True)
        

#         #Médicaments expirés ou bientôt expirés (alerte)
#         st.markdown(dashboard_views.table_html, unsafe_allow_html=True)

#         # CSS personnalisé
#         st.markdown("Médicaments expirés ou bientôt expirés")
#         st.markdown("""
#             <style>
#                     /* Fond noir général */
#                     body, .stApp {
#                     background-color: #0e0e0e;
#                     color: white;
#                 }
#                     /* Style du tableau */
#                 table {
#                     width: 100%;
#                     border-collapse: collapse;
#                     margin-top: 20px;
#                     background-color: #0e0e0e;
#                 }

#                 thead tr {
#                     background-color: #28a745; /* Vert pharmacie */
#                     color: white;
#                     font-weight: bold;
#                 }

#                 tbody tr {
#                     background-color: #0e0e0e;
#                     color: white;
#                 }

#                 td, th {
#                     padding: 10px;
#                     text-align: left;
#                 }

#                 tbody tr:hover {
#                     background-color: #e0f0e0;
#                     color: #0e0e0e;
#                 }
#             </style>
#         """, unsafe_allow_html=True)

#         # Contenu HTML du tableau
#         html_table = f"""
#             <table>
#                 <thead>
#                     <tr>
#                         <th>Nom</th>
#                         <th>Date d'arrivée</th>
#                         <th>Date d'expiration</th>
#                         <th>Prix unitaire</th>
#                         <th>Quantité restante</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#                 {rows_html}
#                 </tbody>
#             </table>
#         """

#         # Affichage HTML personnalisé
#         # st.markdown(html_table, unsafe_allow_html=True)



#     except Exception as e:
#         st.error(f"❌ Erreur lors du calcul des statistiques : {e}")
# else:
#     st.error("❌ Les données 'medicament', 'stock' et 'detailVente' ne sont pas présentes dans le DataFrame.")


# st.markdown("Vendeur non habilité")
# # CSS personnalisé
# st.markdown("""
#             <style>
#                     /* Fond noir général */
#                     body, .stApp {
#                     background-color: #0e0e0e;
#                     color: white;
#                 }
#                     /* Style du tableau */
#                 table {
#                     width: 100%;
#                     border-collapse: collapse;
#                     margin-top: 20px;
#                     background-color: #0e0e0e;
#                 }

#                 thead tr {
#                     background-color: #28a745; /* Vert pharmacie */
#                     color: white;
#                     font-weight: bold;
#                 }

#                 tbody tr {
#                     background-color: #0e0e0e;
#                     color: white;
#                 }

#                 td, th {
#                     padding: 10px;
#                     text-align: left;
#                 }

#                 tbody tr:hover {
#                     background-color: #e0f0e0;
#                     color: #0e0e0e;
#                 }
#             </style>
#         """, unsafe_allow_html=True)

#         # Contenu HTML du tableau

# html_table = """
#             <table>
#                 <thead>
#                     <tr>
#                         <th>Rank</th>
#                         <th>Name</th>
#                         <th>Points</th>
#                         <th>Team</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#                     <tr>
#                         <td>1</td>
#                         <td>Domenic</td>
#                         <td>88,110</td>
#                         <td>dcode</td>
#                     </tr>
#                     <tr>
#                         <td>2</td>
#                         <td>Sally</td>
#                         <td>72,400</td>
#                         <td>Students</td>
#                     </tr>
#                     <tr>
#                         <td>3</td>
#                         <td>Nick</td>
#                         <td>52,300</td>
#                         <td>dcode</td>
#                     </tr>
#                 </tbody>
#             </table>
#         """

#         # Affichage HTML personnalisé
# st.markdown(html_table, unsafe_allow_html=True)

# try:

#     except Exception as e:
#         st.error(f"❌ Erreur lors du calcul des statistiques : {e}")
# else:
#     st.error("❌ Les données 'medicament', 'stock' et 'detailVente' ne sont pas présentes dans le DataFrame.")


#  # Import et récupération depuis MongoDB
# employe_collection = MongoDBClient(collection_name="employe")
# # overview_collection = MongoDBClient(collection_name="overview")
# medicament_collection = MongoDBClient(collection_name="medicament")
# vente_collection = MongoDBClient(collection_name="vente")

# medicament_documents = medicament_collection.find_all_documents()
# employe_documents = employe_collection.find_all_documents()
# vente_documents = vente_collection.find_all_documents()
# # overview_documents = overview_collection.find_all_documents()
# vente_medicament_requete = vente_collection.make_specific_pipeline(
#     pipeline=pipelines_ventes.pipeline_overview_medicament_vente,
#     title="Overview entre vente et médicament"
# ) 


# df_employe = pd.DataFrame(list(employe_documents))
# df_overview = pd.DataFrame(list(vente_medicament_requete))
# df_medicament = pd.DataFrame(list(medicament_documents))
# df_vente = pd.DataFrame(list(vente_documents))

# with st.container():
#     st.markdown("<h3>Clustering employés</h3>", unsafe_allow_html=True)

#     col1, col2 = st.columns([1, 3])

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

#     # Traitement des dates et calcul ancienneté
#     df_employe['date_embauche'] = pd.to_datetime(df_employe['date_embauche'], errors='coerce')
#     today = pd.Timestamp(datetime.today())
#     df_employe['anciennete'] = (today - df_employe['date_embauche']).dt.days / 365.25

#     # Nettoyage
#     df_unique = df_employe.sort_values('date_embauche').drop_duplicates(subset='id_employe', keep='last')
#     df_analysis = df_unique[['anciennete', 'salaire']].dropna()

#     # Colonne 1 : Corrélation
#     with col1:
#         correlation = df_analysis.corr().loc['anciennete', 'salaire']
#         st.markdown(f"""
#             <div class="kpi-card">
#                 <p class="kpi-title" style="font-size:1.2rem;">Corrélation ancienneté / salaire</p>
#                 <p class="kpi-value" style="font-size:2rem;">{correlation:.2f}</p>
#             </div>
#         """, unsafe_allow_html=True)

#     # Colonne 2 : Nuage de points
#     with col2:
#         fig, ax = plt.subplots(figsize=(6, 4))
#         sns.scatterplot(data=df_analysis, x='anciennete', y='salaire', ax=ax)
#         ax.set_title('Ancienneté vs Salaire')
#         ax.set_xlabel("Ancienneté (années)")
#         ax.set_ylabel("Salaire")
#         ax.grid(True)
#         st.pyplot(fig)


# with st.container():
#     st.markdown("<h3>K-Means Clustering interactif</h3>", unsafe_allow_html=True)



#     # Fusionner les données nécessaires
#     df_interactive = df_unique[['id_employe', 'nom', 'fonction', 'categorie']].merge(
#         df_analysis, left_index=True, right_index=True
#     )

#     # Scatter plot avec clusters
#     fig = px.scatter(
#         df_interactive,
#         x='anciennete',
#         y='salaire',
#         color='anciennete',  # Affiche les clusters en couleur
#         color_continuous_scale='plasma',  # Colormap vive et contrastée
#         hover_data=['nom', 'fonction', 'categorie', 'anciennete', 'salaire'],
#         title='K-Means Clustering interactif : Ancienneté vs Salaire'
#     )

#     # Style clair (fond blanc)
#     fig.update_layout(
#         template='plotly_dark',
#         xaxis_title="Ancienneté (années)",
#         yaxis_title="Salaire"
#     )

#     # Affichage Streamlit
#     st.plotly_chart(fig)

# with st.container():
#     st.markdown("<h3>Prediction rupture de meducaments</h3>", unsafe_allow_html=True)

#     # Étape 1 : préparation des colonnes nécessaires
#     df_overview['jour_semaine'] = df_overview['date_de_vente'].dt.dayofweek  # 0 = Lundi, 6 = Dimanche
#     df_overview['mois_num'] = df_overview['date_de_vente'].dt.month

#     # Étape 2 : calcul des probabilités historiques par mois et jour de semaine
#     combo_group = df_overview.groupby(['id_medicament', 'mois_num', 'jour_semaine'])['quantite']
#     combo_zero = combo_group.apply(lambda x: (x == 0).sum()).reset_index(name='nb_zero')
#     combo_total = combo_group.count().reset_index(name='total')

#     combo_stats = pd.merge(combo_zero, combo_total, on=['id_medicament', 'mois_num', 'jour_semaine'])
#     combo_stats['proba_zero'] = combo_stats['nb_zero'] / combo_stats['total']

#     # Mapper les noms des jours de la semaine pour affichage
#     jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
#     combo_stats['jour_semaine'] = combo_stats['jour_semaine'].map(dict(enumerate(jours)))

#     # Étape 3 : projection pour les 6 mois à venir
#     last_date = df_overview['date_de_vente'].max()
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

    
#     # Fusionner noms des médicaments
#     df_meds = df_overview[['id_medicament', 'nom_medicament']].drop_duplicates()
#     forecast_df = forecast_df.merge(df_meds, on='id_medicament', how='left')

#     # Interface utilisateur
#     medicament_choisi = st.selectbox("Choisir un médicament", forecast_df['nom_medicament'].unique())

#     # Filtrer les données
#     med_data = forecast_df[forecast_df['nom_medicament'] == medicament_choisi].copy()

#     # Création de la date synthétique
#     med_data['date_synthetique'] = pd.to_datetime({
#         'year': med_data['annee'],
#         'month': med_data['mois'],
#         'day': 1
#     }) + pd.to_timedelta((med_data['semaine_du_mois'] - 1) * 7, unit='D')

#     # Agrégation
#     agg_data = med_data.groupby('date_synthetique')['proba_zero'].mean().reset_index()

#     # Tracer avec matplotlib
#     import matplotlib.pyplot as plt
#     fig, ax = plt.subplots(figsize=(10, 5))
#     ax.plot(agg_data['date_synthetique'], agg_data['proba_zero'], marker='o')
#     ax.set_title(f"Évolution des probabilités de rupture - {medicament_choisi}")
#     ax.set_xlabel("Date (approx. début de semaine)")
#     ax.set_ylabel("Probabilité de rupture")
#     ax.grid(True)
#     st.pyplot(fig)


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
