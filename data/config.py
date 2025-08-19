import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


if st.secrets:
    mongo_project_id = os.getenv("MONGO_PROJECT_ID")
    mongo_public_key = os.getenv("MONGO_PUBLIC_KEY")
    mongo_private_key = os.getenv("MONGO_PRIVATE_KEY")
    mongo_app_name = os.getenv("MONGO_APP_NAME")
    mongo_username = os.getenv("MONGO_USERNAME")
    mongo_password = os.getenv("MONGO_PASSWORD")
    mongo_cluster = os.getenv("MONGO_CLUSTER")
    
    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    embedding_index_documents = os.getenv("EMBEDDING_INDEX_DOCUMENTS")

mongo_project_id = os.getenv("MONGO_PROJECT_ID")
mongo_public_key = os.getenv("MONGO_PUBLIC_KEY")
mongo_private_key = os.getenv("MONGO_PRIVATE_KEY")

mongo_app_name = os.getenv("MONGO_APP_NAME")
mongo_username = os.getenv("MONGO_USERNAME")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_cluster = os.getenv("MONGO_CLUSTER")

hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

