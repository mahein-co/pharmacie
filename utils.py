import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    try:
        return pd.read_excel("data/dataPharmacie.xlsx",sheet_name=None)
    except Exception as e:
        st.error(f"❌ Erreur de chargement : {e}")
        return None
