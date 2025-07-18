import streamlit as st
from huggingface_hub import login
import os
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFaceEmbeddings

import pandas as pd
from IPython.display import display, Markdown
from data.config import hf_token
from data.mongodb_client import MongoDBClient


# ✅ Définir ta clé API HuggingFace
login(token=hf_token)

# Models LLM
model_name = "meta-llama/Llama-2-7b-chat-hf"
repo_id = "meta-llama/Llama-3.1-8B-Instruct"
repo_id2 = "microsoft/phi-4"

# Chargement du modèle d'embedding
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Connexion MongoDB Atlas
collection = MongoDBClient(collection_name="corpus_rag").get_collection()


tokenizer = AutoTokenizer.from_pretrained(repo_id)
hf_model = AutoModelForCausalLM.from_pretrained(
    repo_id,
    device_map="auto",
    load_in_4bit=False, 
    trust_remote_code=True
)

generator = pipeline(
    "text-generation",
    model=hf_model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9
)

st.set_page_config(page_title="Chatbot Simple", layout="centered")
# UI Streamlit
st.title("🧠 Assistant Pharmacie")
st.markdown("Posez une question liée aux ventes, employés ou médicaments.")

# Initialiser les messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie utilisateur
if prompt := st.chat_input("❓ Votre question"):

    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.spinner("🔍 Recherche des documents pertinents..."):
        # Étape 1 : vectoriser la question
        query_vector = embed_model.encode(prompt).tolist()

        # Étape 2 : requête vectorielle dans corpus_rag
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": query_vector,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": 4,
                    "index": "embedding_corpus_rag"
                }
            },
            {
                "$project": {
                    "texte_embedding": 1,
                    "source": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        results = list(collection.aggregate(pipeline))

        if results:
            st.subheader("📄 Contexte extrait")
            context = "\n".join([f"- {doc['texte_embedding']}" for doc in results])
            st.code(context, language="markdown")

            # Étape 3 : créer le prompt
            prompt = """
                Vous êtes un assistant intelligent travaillant dans une pharmacie. 
                Votre tâche est de répondre à la question de l'utilisateur uniquement à partir du contexte fourni.

                Contexte :
                {contexte}  

                Question : {question}

                Répondez de manière claire, précise et factuelle. 
                Si l'information n’est pas présente dans le contexte, dites-le explicitement.
            """

    
    with st.spinner("💬 Génération de la réponse..."):
        output = generator(prompt)
        reponse_finale = output[0]['generated_text'].replace(prompt, "").strip()


    # Ajouter la réponse du bot à l'historique
    st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
    with st.chat_message("assistant"):
        st.markdown(reponse_finale)
