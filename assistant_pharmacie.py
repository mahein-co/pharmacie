import streamlit as st
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import ollama

from data.mongodb_client import MongoDBClient

# Models LLM
model_name = "meta-llama/Llama-2-7b-chat-hf"
repo_id = "meta-llama/Llama-3.1-8B-Instruct"
repo_id2 = "microsoft/phi-4"

# Chargement du modèle d'embedding
embed_model = SentenceTransformer("all-MiniLM-L6-v2")


# Connexion MongoDB Atlas
collection = MongoDBClient(collection_name="corpus_rag").get_collection()


# UI Streamlit
st.title("🧠 Assistant Pharmacie")
st.markdown("Posez une question liée aux ventes, employés ou médicaments.")

question = st.text_input("❓ Votre question")

if question:
    with st.spinner("🔍 Recherche des documents pertinents..."):
        # Étape 1 : vectoriser la question
        query_vector = embed_model.encode(question).tolist()

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
        prompt = (
            f"Contexte :\n{context}\n\n"
            f"Question : {question}\n"
            f"Réponds de manière claire, concise et factuelle."
        )

        with st.spinner("💬 Génération de la réponse par le LLM..."):
            response = ollama.chat(
                model="llama3",  # ou "mistral" ou autre modèle local
                messages=[{"role": "user", "content": prompt}]
            )
            reponse_finale = response['message']['content']

        # Affichage final
        st.subheader("🧠 Réponse de l'assistant :")
        st.write(reponse_finale)

        st.markdown("---")
        with st.expander("📚 Sources utilisées"):
            for doc in results:
                st.markdown(f"- **[{doc['source']}]** {doc['texte_embedding']}")
    else:
        st.warning("Aucun document pertinent trouvé.")
