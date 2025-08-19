import os
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

print("Loading environment variables...", Path(".streamlit/secrets.toml").exists())

if st.secrets or Path(".streamlit/secrets.toml").exists() :
    print("Pass trough the secrets -------------------------------------")
    mongo_project_id = st.secrets.get("MONGO_PROJECT_ID", os.getenv("MONGO_PROJECT_ID"))
    mongo_public_key = st.secrets.get("MONGO_PUBLIC_KEY", os.getenv("MONGO_PUBLIC_KEY"))
    mongo_private_key = st.secrets.get("MONGO_PRIVATE_KEY", os.getenv("MONGO_PRIVATE_KEY"))
    mongo_app_name = st.secrets.get("MONGO_APP_NAME", os.getenv("MONGO_APP_NAME"))
    mongo_username = st.secrets.get("MONGO_USERNAME", os.getenv("MONGO_USERNAME"))
    mongo_password = st.secrets.get("MONGO_PASSWORD", os.getenv("MONGO_PASSWORD"))
    mongo_cluster = st.secrets.get("MONGO_CLUSTER", os.getenv("MONGO_CLUSTER"))
    
    openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    embedding_index_documents = st.secrets.get("EMBEDDING_INDEX_DOCUMENTS", os.getenv("EMBEDDING_INDEX_DOCUMENTS"))

mongo_project_id = os.getenv("MONGO_PROJECT_ID")
mongo_public_key = os.getenv("MONGO_PUBLIC_KEY")
mongo_private_key = os.getenv("MONGO_PRIVATE_KEY")

mongo_app_name = os.getenv("MONGO_APP_NAME")
mongo_username = os.getenv("MONGO_USERNAME")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_cluster = os.getenv("MONGO_CLUSTER")

openai_api_key = os.getenv("OPENAI_API_KEY")

