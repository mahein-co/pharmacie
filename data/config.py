import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

mongo_project_id = os.getenv("MONGO_PROJECT_ID")
mongo_public_key = os.getenv("MONGO_PUBLIC_KEY")
mongo_private_key = os.getenv("MONGO_PRIVATE_KEY")

mongo_app_name = os.getenv("MONGO_APP_NAME")
mongo_username = os.getenv("MONGO_USERNAME")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_cluster = os.getenv("MONGO_CLUSTER")

hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
# if st.secrets:
    # mongo_project_id = st.secrets["MONGO_PROJECT_ID"]
    # mongo_public_key = st.secrets["MONGO_PUBLIC_KEY"]
    # mongo_private_key = st.secrets["MONGO_PRIVATE_KEY"]

    # mongo_app_name = st.secrets["MONGO_APP_NAME"]
    # mongo_username = st.secrets["MONGO_USERNAME"]
    # mongo_password = st.secrets["MONGO_PASSWORD"]
    # mongo_cluster = st.secrets["MONGO_CLUSTER"]

    # hf_token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
    

