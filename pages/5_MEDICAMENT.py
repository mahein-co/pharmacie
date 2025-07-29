import streamlit as st
import pandas as pd
import numpy as np
from streamlit.components.v1 import html
from views import medicament_views
from data.mongodb_client import MongoDBClient




# Initialisation
st.set_page_config(page_title="MEDICAMENT", layout="wide")

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
<div class="box">Médicament</div>
""")