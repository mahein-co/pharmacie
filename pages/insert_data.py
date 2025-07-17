import streamlit as st
import pandas as pd
from data.mongodb_client import MongoDBClient



st.markdown("""
    <h1 style='font-size: 32px; color: #4CAF50; margin-bottom: 0;'>IMPORTATION DE DONNÉES</h1>
    <p style='font-size: 16px; color: gray;'>Upload d'un fichier Excel vers la base données</p>
    <hr style='margin-top: 10px; margin-bottom: 20px;' />
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Téléversez un fichier Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    st.success("Fichier reçu. Lecture des feuilles Excel...")

    # Lecture de toutes les feuilles
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)

    mongo = MongoDBClient(db_name="pharmacie")  # base MongoDB
    st.info(f"{len(all_sheets)} feuille(s) détectée(s)")

    for sheet_name, df in all_sheets.items():
        st.subheader(f"Feuille : {sheet_name}")
        st.dataframe(df)

        if st.button(f"Inserer les données de la feuille '{sheet_name}'"):
            # Convertir chaque ligne du DataFrame en dict
            records = df.fillna("").to_dict(orient="records")  # éviter les NaN
            # Utiliser le nom de la feuille comme nom de collection
            mongo.set_collection(sheet_name)
            for record in records:
                mongo.insert_document(record)
            st.success(f"{len(records)} documents insérés dans la collection '{sheet_name}' ✅")

