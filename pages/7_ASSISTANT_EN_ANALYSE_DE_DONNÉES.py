import streamlit as st
from streamlit.components.v1 import html
from datetime import datetime

import logging
from openai import OpenAI


from data.config import openai_api_key
from data.mongodb_client import MongoDBClient
from views import dashboard_views, employe_views

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

# DATE TODAY
TODAY = datetime.now().strftime("%Y-%m-%d")

# Model LLM
model_llm = "gpt-4o-mini"

# Model embedding
model_embedding = "text-embedding-3-small"

# Connexion MongoDB Atlas
corpus_collection = MongoDBClient(collection_name="corpus_rag").get_collection()

perte_total_medicaments = f"{dashboard_views.total_pertes_medicaments}".replace(",", " ")
valeur_stock_restant = f"{dashboard_views.valeur_totale_stock}".replace(",", " ")

# Generate text embedding
def generate_text_embedding(text: str):
    response = client_openai.embeddings.create(
        input=text,
        model=model_embedding
    )
    return response.data[0].embedding


def search_rag_mongo(query, k=400):
    query_embedding = generate_text_embedding(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "embedding_corpus_rag", 
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 7000,   
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

def get_last_user_question():
    messages = [m for m in st.session_state.data_analyste_messages if m["role"] == "user"]
    return messages[-2]["content"] if len(messages) >= 2 else None

    
# System prompt for the AI
system_prompt = f"""
    Tu es un assistant en analyse de données pharmaceutiques.
    Ton rôle est d’assister les utilisateurs (pharmaciens ou professionnels de santé) en leur fournissant des informations fiables, claires, actualisées et compréhensibles sur :
        les médicaments (nom, usage, posologie, effets secondaires, contre-indications, interactions, prix, génériques, disponibilité)
        les symptômes courants et les traitements recommandés en automédication
        la gestion du stock et la traçabilité des lots
        la date de péremption et les risques liés aux produits expirés et que tu réfères toujours à la date aujourd'hui {TODAY}
        les bonnes pratiques pharmaceutiques (conservation, conseils de prise, etc.)
        Si on te pose une question qui est liée à une date, réfères-toi s'il le faut à la date d'aujourd'hui {TODAY}; 
        Tu ne remplaces jamais un médecin ou un pharmacien : tu fournis des conseils informatifs, pas de diagnostics médicaux.
        Tu signales toujours les limites de ta réponse en cas de doute ou de situation urgente.
        Tu es factuel, bienveillant et pédagogique dans ta manière de répondre.
        Tu t’adaptes au niveau de l’utilisateur : langage simple pour les patients, technique pour les professionnels.
        Si on te fournit une date de péremption, tu la compares automatiquement à la date du jour pour évaluer la validité.
        Si l’utilisateur demande une analyse de stock, tu fournis des rapports synthétiques ou détaillés selon le besoin.
        Si tu ne sais pas ou n'es pas autorisé à répondre, tu redonnes la main au professionnel de santé.
        Si on te demande le chiffre d'affaire, te voici le chiffre d'affaire de la pharmacie : {dashboard_views.total_chiffre_affaire_str} MGA.
        Si on te demande le chiffre d'affaire d'un certain temps, tu calcules la somme de tous les produits de quantite vendue et prix unitaire des ventes de ce temps en donnant le nom de médicament vendu et son fournisseur.

        Si on te demande la perte due aux médicaments invendus, te voici la perte: {perte_total_medicaments} MGA.
        Si on te demande la valeur totale de stock restant des médicaments, te voici la valeur totale de stock des médicaments: {valeur_stock_restant} ventes.
        Si on te demande le nombre d'employés, te voici le nombre d'employés de la pharmacie: {employe_views.Nb_employers} employés.

    Voici des informations provenant de notre base de ventes, de stocks et d'employés:
"""

# Generate AI response
def generate_answer(query, retrieved_docs):
    # last_question = get_last_user_question()
    context = "\n\n---\n\n".join(retrieved_docs)
    # conversation_context = f"Dernière question de l'utilisateur : {last_question}\n" if last_question else ""
    conversation = [{"role": m["role"], "content": m["content"]} for m in st.session_state.data_analyste_messages]

    prompt = f"""
        {context}   
        {conversation}
        Réponds à la question suivante de manière claire, concise et professionnelle :
        {query}
    """
    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

st.set_page_config(page_title="Chatbot Simple", layout="centered")
# UI Streamlit
html("""
<style>
    @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
    
  .box {
    color: #0A9548;
    text-align: center;
    font-family: 'Quicksand', cursive;
    font-size: 2.5rem;
  }
    .subtitle {
    text-align: center;
    color: #48494B;
    font-family: 'Quicksand', cursive;
    font-size: 1.2rem;
  }
</style>
<h1 class="box">Assistant en analyse de données</h1>
<h4 class="subtitle">Posez une question sur vos ventes, vos employés ou vos stocks.</h4>
""")

# Initialiser les messages
if "data_analyste_messages" not in st.session_state:
    st.session_state.data_analyste_messages = []

# Afficher l'historique des data_analyste_messages
for message in st.session_state.data_analyste_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie utilisateur
if prompt := st.chat_input("Posez votre question ici..."):

    # Ajouter le message utilisateur à l'historique
    st.session_state.data_analyste_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.spinner("Recherche des documents pertinents..."):
        results = search_rag_mongo(prompt)
        ai_response = generate_answer(query=prompt, retrieved_docs=results)
            
    st.session_state.data_analyste_messages.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.markdown(ai_response)


