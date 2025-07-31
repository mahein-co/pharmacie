import streamlit as st

import os
import logging
from datetime import datetime
import faiss
from openai import OpenAI
import numpy as np


from data.config import openai_api_key
from data.mongodb_client import MongoDBClient

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("corpus_rag.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Connexion to OpenAI API
client_openai = OpenAI(api_key=openai_api_key)

# Model LLM
model_llm = "gpt-4o-mini"

# Model embedding
model_embedding = "text-embedding-3-small"

# Connexion MongoDB Atlas
corpus_collection = MongoDBClient(collection_name="corpus_rag").get_collection()


# Generate text embedding
def generate_text_embedding(text: str):
    response = client_openai.embeddings.create(
        input=text,
        model=model_embedding
    )
    return response.data[0].embedding


def search_rag_mongo(query, k=200):
    query_embedding = generate_text_embedding(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "embedding_corpus_rag", 
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 2000,   
                "limit": k
            }
        },
        {
            "$project": {
                "text": 1,
                "score": { "$meta": "vectorSearchScore" }
            }
        }
    ]

    results = list(corpus_collection.aggregate(pipeline))
    return [doc["text"] for doc in results]

    
# System prompt for the AI
system_prompt = """
    Tu es un assistant pharmaceutique.
    Ton rôle est d’assister les utilisateurs (pharmaciens ou professionnels de santé) en leur fournissant des informations fiables, claires, actualisées et compréhensibles sur :

        les médicaments (nom, usage, posologie, effets secondaires, contre-indications, interactions, prix, génériques, disponibilité)

        les symptômes courants et les traitements recommandés en automédication

        la gestion du stock et la traçabilité des lots

        la date de péremption et les risques liés aux produits expirés

        les bonnes pratiques pharmaceutiques (conservation, conseils de prise, etc.)

        Tu ne remplaces jamais un médecin ou un pharmacien : tu fournis des conseils informatifs, pas de diagnostics médicaux.

        Tu signales toujours les limites de ta réponse en cas de doute ou de situation urgente.

        Tu es factuel, bienveillant et pédagogique dans ta manière de répondre.

        Tu t’adaptes au niveau de l’utilisateur : langage simple pour les patients, technique pour les professionnels.

        Si on te fournit une date de péremption, tu la compares automatiquement à la date du jour pour évaluer la validité.

        Si l’utilisateur demande une analyse de stock, tu fournis des rapports synthétiques ou détaillés selon le besoin.

        Si tu ne sais pas ou n'es pas autorisé à répondre, tu redonnes la main au professionnel de santé.

    Voici des informations provenant de notre base de ventes, de stocks et d'employés:
"""

# prompt = """
#     Vous êtes un assistant intelligent travaillant dans une pharmacie. 
#     Votre tâche est de répondre à la question de l'utilisateur uniquement à partir du contexte fourni.

#     Contexte :
#     {contexte}  

#     Question : {question}

#     Répondez de manière claire, précise et factuelle. 
#     Si l'information n’est pas présente dans le contexte, dites-le explicitement.
# """


# Generate AI response
def generate_answer(query, retrieved_docs):
    context = "\n\n---\n\n".join(retrieved_docs)
    prompt = f"""
        {system_prompt}
        {context}   
        Réponds à la question suivante de manière claire, concise et professionnelle :
        {query}
    """
    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un assistant pharmaceutique."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message["content"]


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
if prompt := st.chat_input("Votre question"):

    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.spinner("Recherche des documents pertinents..."):
        results = search_rag_mongo(prompt)
        ai_response = generate_answer(query=prompt, retrieved_docs=results)
            
    # Ajouter la réponse du bot à l'historique
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.markdown(ai_response)


