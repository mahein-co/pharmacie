import streamlit as st
from huggingface_hub import login
import os

# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFaceEmbeddings

# from sentence_transformers import SentenceTransformer
import pandas as pd
from IPython.display import display, Markdown
from data.config import hf_token


# ✅ Définir ta clé API HuggingFace
login(token=hf_token)

model_name = "meta-llama/Llama-2-7b-chat-hf"
repo_id = "meta-llama/Llama-3.1-8B-Instruct"
repo_id2 = "microsoft/phi-4"

st.set_page_config(page_title="Chatbot Simple", layout="centered")
st.title("🤖 Pharma bot")

# Initialiser les messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie utilisateur
if prompt := st.chat_input("Écrivez votre message ici..."):

    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, '../data', 'dataPharmacie.xlsx')

    loader = UnstructuredExcelLoader(file_path, mode="elements")
    docs = loader.load()

    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names

    all_docs = []
    for sheet in sheet_names:
        loader = UnstructuredExcelLoader(file_path=file_path, mode="elements", sheet=sheet)
        docs = loader.load()
        all_docs.extend(docs)

    # Split the documents into chuncks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(all_docs)

    texts = [chunk.page_content for chunk in chunks]

    # model name
    model_name="sentence-transformers/all-MiniLM-L6-v2"

    # Créer des Documents à partir des textes
    documents = [Document(page_content=text) for text in texts]

    # Adaptateur d'embedding LangChain pour HuggingFace
    embedding_function = HuggingFaceEmbeddings(model_name=model_name)

    # Créer l'index FAISS
    db_faiss = FAISS.from_documents(documents, embedding_function)

    # Recherche vectorielle (top 50)
    query = prompt
    docs_faiss = db_faiss.similarity_search_with_score(query, k=30)

    context = "\n\n".join([doc.page_content for doc, _score in docs_faiss])

    # Prompt for RAG system
    prompt = f"""
    Utilise les éléments de contexte suivants {context} pour répondre à la question {query} à la fin.
    Tes réponses seront toujours en français.
    Si on te demande une date, ta réponse devra toujours être en long format.

    Si on te demande la date d'expiration ou peremption ou permiction d'un médicament,
    tu devras toujours analyser bien la date et la comparer à la date d'aujourd'hui.

    Resumes toujours ta réponse si on ne te demande pas de la détailler.

    En aucun cas, tu ne fourniras jamais comme une réponse un identifiant ou l'ID d'une entité.

    Si tu ne connais pas la réponse, dis simplement que tu ne sais pas."""

    # Model LLM
    llm = HuggingFaceEndpoint(
        repo_id = repo_id,
        task="text-generation",
        max_new_tokens=150,
        temperature=0.7,
        top_k=50,
        top_p=0.9,
        repetition_penalty=1.2,
        do_sample=True
    )

    chat_model = ChatHuggingFace(llm=llm)

    response = chat_model.invoke(prompt)
    reponse_finaly = display(Markdown(response.content))
    
    # Réponse du bot (ici réponse simple)
    # response = f"Tu as dit : **{prompt}**"

    # Ajouter la réponse du bot à l'historique
    st.session_state.messages.append({"role": "assistant", "content": reponse_finaly})
    with st.chat_message("assistant"):
        st.markdown(reponse_finaly)
