import streamlit as st
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from streamlit.components.v1 import html


# LangChain components
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# from langchain.prompts import PromptTemplate
# from langchain_community.vectorstores import MongoDBAtlasVectorSearch
# from langchain_core.documents import Document
# from langchain_community.callbacks import StreamlitCallbackHandler # For streaming answers
# from langchain_core.messages import HumanMessage, AIMessage # For LangChain chat history format
from openai import OpenAI

from data.mongodb_client import MongoDBClient

from data.config import openai_api_key, mongo_username, mongo_password, mongo_app_name, mongo_cluster, embedding_index_documents


# Load environment variables (for local development)
load_dotenv()

# --- 1. Streamlit Page Configuration (MUST be the first Streamlit command) ---
st.set_page_config(
    page_title="Pharmacie AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)



client_openai = OpenAI(api_key=openai_api_key)
model_embedding = "text-embedding-3-small"

pharm_document_collection = MongoDBClient(collection_name="pharm_documents").get_collection()

# --- 2. Configuration and Secrets Management ---
# Connexion to OpenAI API
# Prioritize Streamlit secrets for deployment, fall back to .env for local
OPENAI_API_KEY = openai_api_key
MONGO_URI = f"""
    mongodb+srv://{mongo_username}:{mongo_password}
    @{mongo_cluster}.sdly3uh.mongodb.net/?retryWrites=true
    &w=majority&appName={mongo_app_name}
"""
ATLAS_VECTOR_SEARCH_INDEX_NAME = embedding_index_documents

# Display errors and stop if critical secrets are missing
# if not OPENAI_API_KEY:
#     st.error("OpenAI API key not found. Please set it in your environment variables or Streamlit secrets.")
#     st.stop()
# if not MONGO_URI:
#     st.error("MongoDB URI not found. Please set it in your environment variables or Streamlit secrets.")
#     st.stop()
# if not ATLAS_VECTOR_SEARCH_INDEX_NAME:
#     st.error("Atlas Vector Search Index Name not found. Please set it in your environment variables or Streamlit secrets.")
#     st.stop()

system_prompt = """
Vous êtes un assistant pharmacien pour la Pharmacie de Madagascar.
Fournissez des réponses précises, professionnelles et scientifiques en vous basant uniquement sur le contexte fourni.
Si vous n'êtes pas sûr(e) de la réponse, orientez l'utilisateur vers le pharmacien en service.
vous pouvez repondre à des salutations et des remerciements tout simplement.

Veuillez répondre de manière professionnelle, scientifiquement rigoureux et utile :
"""
# --- 3. Pharmacie Prompt in French ---
PHARM_PROMPT_TEMPLATE = """
Vous êtes un assistant pharmacien pour la Pharmacie de Madagascar.
Fournissez des réponses précises, professionnelles et scientifiques en vous basant uniquement sur le contexte fourni.
Si vous n'êtes pas sûr(e) de la réponse, orientez l'utilisateur vers le pharmacien en service.
vous pouvez repondre à des salutations et des remerciements tout simplement.

Contexte : {context}

Question : {question}
Veuillez répondre de manière professionnelle, scientifiquement rigoureux et utile :
"""

# PHARM_PROMPT = PromptTemplate(
#     template=PHARM_PROMPT_TEMPLATE,
#     input_variables=["context", "question"]
# )

# Generate text embedding
def generate_text_embedding(text: str):
    response = client_openai.embeddings.create(
        input=text,
        model=model_embedding
    )
    return response.data[0].embedding

# Search function for RAG (Retrieval-Augmented Generation)
def search_rag_mongo(query, k=200):
    query_embedding = generate_text_embedding(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "embedding_index_documents", 
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

    results = list(pharm_document_collection.aggregate(pipeline))
    return [doc["text"] for doc in results]

def get_last_user_question():
    messages = [m for m in st.session_state.messages if m["role"] == "user"]
    return messages[-2]["content"] if len(messages) >= 2 else None

# Generate AI response
def generate_answer(query, retrieved_docs, system_prompt=system_prompt):
    # last_question = get_last_user_question()
    context = "\n\n---\n\n".join(retrieved_docs)
    # conversation_context = f"Dernière question de l'utilisateur : {last_question}\n" if last_question else ""
    conversation = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    prompt = f"""
        {context}   
        {conversation}
        Réponds à la question suivante de manière claire, concise et professionnelle :
        {query}
    """
    response = client_openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content


# --- 4. Initialize MongoDB Atlas Vector Store and Embeddings (Cached) ---
# @st.cache_resource ensures this function runs only once across reruns
# @st.cache_resource
# def get_qa_chain(openai_api_key, index_name):
    try:
        collection = MongoDBClient(collection_name="pharm_documents").get_collection()

        embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_api_key)

        vectorstore = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embedding_model,
            index_name=index_name,
            text_key="text",
            embedding_key="embedding"
        )

        # Initialize LLM with streaming=True for token-by-token output
        llm = ChatOpenAI(model_name="gpt-4o", temperature=0.2, openai_api_key=openai_api_key, streaming=True)

        # ConversationBufferMemory for LangChain's internal chat history management
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key='answer'
        )

        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            ),
            memory=memory, # Pass memory for internal LangChain history
            combine_docs_chain_kwargs={
                "prompt": PHARM_PROMPT.partial(company_name="Pharmacie de Madagascar")
            },
            return_source_documents=True # Still retrieve and return source documents
        )

        return qa_chain
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        st.stop()

# Get the RAG chain instance
# qa_chain = get_qa_chain(OPENAI_API_KEY, ATLAS_VECTOR_SEARCH_INDEX_NAME)


# --- 5. Streamlit App Interface (Chat-based UX) ---
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
<h1 class="box">Pharmacie de Madagascar AI assistant</h1>
<h4 class="subtitle">Bienvenue dans votre assistant pharmacien intelligent !</h4>
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display previous chat messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
#         # If it's an assistant message and has sources, display them in a collapsed expander
#         if message["role"] == "assistant" and message.get("sources"):
#             with st.expander("🔎 Voir les documents sources"): # This expander is for sources ONLY, defaults to collapsed
#                 st.markdown("Ces informations sont basées sur les documents suivants :")
#                 for i, doc in enumerate(message["sources"]):
#                     st.markdown(f"**Source Document {i+1}:**")
#                     st.write(f"- Fichier: `{doc.metadata.get('source', 'Inconnue')}`")
#                     st.write(f"- Page/Ligne: {doc.metadata.get('page', 'N/A')}")
#                     st.write(f"- Type: `{doc.metadata.get('document_type', 'N/A')}`")
#                     # Display a snippet of the document content
#                     st.markdown(f"```text\n{doc.page_content[:400]}...\n```")
#                     st.markdown("---")

# Zone de saisie utilisateur
if prompt := st.chat_input("Posez votre question"):

    # Ajouter le message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.spinner("Recherche des documents pertinents..."):
        results = search_rag_mongo(prompt)
        ai_response = generate_answer(query=prompt, retrieved_docs=results)
            
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.markdown(ai_response)


# --------------------------------------------------------------
# # Use st.chat_input for new user messages – it automatically clears after submission
# if user_question := st.chat_input("Posez votre question ici :"):
#     # Add user message to the session's chat history for display
#     st.session_state.messages.append({"role": "user", "content": user_question})

#     # Display the user's message immediately in the chat UI
#     with st.chat_message("user"):
#         st.markdown(user_question)

#     # Prepare chat history for LangChain (it expects HumanMessage/AIMessage objects)
#     langchain_chat_history = []
#     for msg in st.session_state.messages[:-1]: # Exclude the very last user message
#         if msg["role"] == "user":
#             langchain_chat_history.append(HumanMessage(content=msg["content"]))
#         elif msg["role"] == "assistant":
#             langchain_chat_history.append(AIMessage(content=msg["content"]))

#     # Prepare for assistant's streaming response
#     with st.chat_message("assistant"):
#         # This message_placeholder will stream the answer directly. NO expander here.
#         message_placeholder = st.empty()
#         full_response_content = ""
#         sources = []

#         with st.spinner("Recherche et génération de réponse..."):
#             try:
#                 # Initialize StreamlitCallbackHandler to stream output to the placeholder
#                 st_callback = StreamlitCallbackHandler(message_placeholder)

#                 result = qa_chain.invoke(
#                     {"question": user_question, "chat_history": langchain_chat_history},
#                     config={"callbacks": [st_callback]} # Pass the callback here
#                 )
#                 full_response_content = result["answer"]
#                 sources = result["source_documents"]

#             except Exception as e:
#                 full_response_content = f"Désolé, une erreur est survenue lors de la génération de la réponse : {e}"
#                 st.error(full_response_content)

#         # --- FIX: Ensure final content is displayed after spinner ---
#         # Explicitly update the placeholder with the final, full content
#         # after the spinner is gone and result is complete.
#         message_placeholder.markdown(full_response_content)
#         # --- END FIX ---

#         # After streaming is complete, add the full response and sources to session state
#         st.session_state.messages.append({"role": "assistant", "content": full_response_content, "sources": sources})

#         # Display source documents in an expander below the streamed answer
#         # This expander is now only for the sources and is collapsed by default.
#         if sources:
#             with st.expander("🔎 Voir les documents sources"): # Defaults to collapsed (expanded=False)
#                 st.markdown("Ces informations sont basées sur les documents suivants :")
#                 for i, doc in enumerate(sources):
#                     st.markdown(f"**Source Document {i+1}:**")
#                     st.write(f"- Fichier: `{doc.metadata.get('source', 'Inconnue')}`")
#                     st.write(f"- Page/Ligne: {doc.metadata.get('page', 'N/A')}")
#                     st.write(f"- Type: `{doc.metadata.get('document_type', 'N/A')}`")
#                     st.markdown(f"```text\n{doc.page_content[:400]}...\n```")
#                     st.markdown("---")


# # --- Sidebar for additional info ---
with st.sidebar:
    # Use columns to center the image
    col1_sb, col2_sb, col3_sb = st.columns([1, 2, 1])
    st.header("À propos de l'Assistant")
    st.markdown("""
    Cet assistant est un outil basé sur l'IA, conçu spécifiquement pour
    les employés de la Pharmacie de Madagascar.

    *Powered by Pharmacie de Madagascar AI.*
    """)
    st.markdown("---")
    st.markdown("Pour toute question complexe ou spécifique à votre situation, veuillez contacter directement les personnes concernées.")