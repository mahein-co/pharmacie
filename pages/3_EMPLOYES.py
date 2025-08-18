import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html
from views import employe_views, dashboard_views

from datetime import datetime

from style import style, icons









# Initialisation
st.set_page_config(page_title="EMPLOYE", layout="wide")

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
<div class="box">Employés</div>
""")

#importation html et css
st.markdown(style.custom_css, unsafe_allow_html=True)
st.markdown(style.kpis_style, unsafe_allow_html=True)

if employe_views.employe_collection:
  kpis_html = f"""
  <div class="kpi-container">
      <div class="kpi-card">
        <div style="text-align: left; position:absolute;">
          {icons.employees_icon_html}
        </div>
          <p class="kpi-title">Nombre d'employés</p>
          <p class="kpi-value" style="font-size:1.5rem;">{employe_views.Nb_employers}</p>
      </div>
      <div class="kpi-card">
        <div style="text-align: left; position:absolute;">
          {icons.salaire_icon_html}
        </div>
          <p class="kpi-title">Salaire Moyen (MGA)</p>
          <p class="kpi-value" style="font-size:1.5rem;">{employe_views.salaire_moyen}</p>
      </div>
      <div class="kpi-card">
        <div style="text-align: left; position:absolute;">
          {icons.age_icon_html}
        </div>
          <p class="kpi-title">Age moyen</p>
          <p class="kpi-value" style="font-size:1.5rem;">{round(employe_views.age_moyen)} ans</p>
      </div>
  </div>
  """
  st.markdown(kpis_html, unsafe_allow_html=True)


with st.container():
  # 2. EMPLOYEES --------------------------------------------
  employe_df = pd.DataFrame(list(dashboard_views.all_employes))
  employe_df = employe_df.drop_duplicates(subset=['id_employe'])
  employe_df = employe_df[['date_embauche', 'salaire']]
  employe_df.rename(columns={'salaire': 'Salaire'}, inplace=True)
  employe_df['date_embauche'] = pd.to_datetime(employe_df['date_embauche'], errors='coerce')

  # Calculate ancienneté in years
  today = pd.Timestamp(datetime.today())
  employe_df['Ancienneté'] = (today - employe_df['date_embauche']).dt.days / 365.25

  # Remove duplicates by keeping the most recent 'date_embauche' per 'id_employe'
  employe_df_unique = employe_df.sort_values('date_embauche')

  # Keep only relevant columns for analysis
  employe_df_analysis = employe_df_unique[['Ancienneté', 'Salaire']].dropna()
  employe_correlation = abs(employe_df_analysis.corr().loc['Ancienneté', 'Salaire'])

  # Clustering with KMeans
  employe_clustering_plot = px.scatter(
      employe_df_analysis,
      x="Ancienneté",
      y="Salaire",
      color="Salaire",
      size="Salaire",
      template="simple_white",
      title=f"Correlation: {employe_correlation:.2f}",
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
  st.plotly_chart(employe_clustering_plot, use_container_width=True)

  
with st.container():
    col1,col2 = st.columns(2)

    with col1:
      #DataFrame
      data = employe_views.effectif_par_employe_categorie
      df_eff_categorie = pd.DataFrame(data)


      # Graphique camembert avec Plotly Express
      fig = px.pie(
          df_eff_categorie,
          names='Categorie',
          values='Effectif',
          hole=0.4
      )

      # Centrage du titre avec xanchor
      fig.update_layout(
          title=dict(
              text="Répartition par catégories",
              x=0.5,
              xanchor='center',
              font=dict(size=18)
          ),
          paper_bgcolor="rgba(0,0,0,0)",  
          plot_bgcolor="rgba(0,0,0,0)",   
          margin=dict(l=20, r=20, t=40, b=20),
      )

      # Affichage dans Streamlit
      st.plotly_chart(fig, use_container_width=True)

    with col2:
      #DataFrame
      data = employe_views.effectif_par_employe_fonction
      df_eff_fonction = pd.DataFrame(data)

      # Graphique camembert avec Plotly Express
      fig = px.pie(
          df_eff_fonction,
          names='Fonction',
          values='Effectif',
          hole=0.4
      )

      # Centrage du titre avec xanchor
      fig.update_layout(
          title=dict(
              text="Répartition par Fonction",
              x=0.5,
              xanchor='center',
              font=dict(size=18)
          ),
          paper_bgcolor="rgba(0,0,0,0)",  
          plot_bgcolor="rgba(0,0,0,0)",   
          margin=dict(l=20, r=20, t=40, b=20),
      )

      # Affichage dans Streamlit
      st.plotly_chart(fig, use_container_width=True)



