import streamlit as st
from streamlit_chat import message
from huggingface_hub import login
import json
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
import os

from torch import cuda, bfloat16
import transformers
# ✅ Définir ta clé API HuggingFace
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"  # Assurez-vous de définir votre clé API
login(token="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")

model_name = "meta-llama/Llama-2-7b-chat-hf"

# Check if GPU is used
device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'



# Bitsandbytes pour quantization
from transformers import BitsAndBytesConfig
config = transformers.BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=bfloat16
)


from transformers import AutoTokenizer, AutoModelForCausalLM
# Load the associated Tokenizer of LLaMA-2

tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
# Load the model
model = transformers.AutoModelForCausalLM.from_pretrained(model_name,
                                                          trust_remote_code=True,
                                                          quantization_config=config,
                                                          device_map="auto")

# Go to evaluation mode
model.eval()


# Créer le pipeline
generator = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.15,
    repetition_penalty=1.1
)



# Emballer le pipeline HuggingFace pour LangChain
llm = HuggingFacePipeline(pipeline=generator)


#1. Charger les données JSON ---------
RAW_JSON = """
[
  {"Nom_Client": "Mélodie Athéna", "Pourcentage": 10.77},
  {"Nom_Client": "Agnès Yóu",      "Pourcentage": 16.12},
  {"Nom_Client": "Félicie Anaël",  "Pourcentage": 11.46},
  {"Nom_Client": "Mélys Ruò",      "Pourcentage": 9.85}
]
"""
data = json.loads(RAW_JSON)

#2. Créer les documents LangChain ---------
documents = [
    Document(
        page_content=f"Client: {item['Nom_Client']}, Pourcentage: {item['Pourcentage']}%",
        metadata={"index": idx}
    )
    for idx, item in enumerate(data)
]



#3. Embeddings avec modèle Hugging Face ---------
embedding_model = HuggingFaceEmbeddings(model_name="bert-base-uncased")
vectorstore = FAISS.from_documents(documents, embedding_model)


# 4. Construire la chaîne QA avec ton modèle Llama2 local ---------
# ✅ Prompt personnalisé
from langchain.prompts import PromptTemplate

custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
<div style="display:none">{context} 
{question}
</div>
Répondez à la question suivante de manière concise.

Réponse :
"""
)

# ✅ QA chain (assurez-vous que llm et vectorstore sont bien définis avant)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={"prompt": custom_prompt}
)

# ✅ Interface utilisateur Streamlit
from datetime import datetime

st.set_page_config(page_title="Chat Interface", page_icon="💬", layout="wide")

# 🌙 CSS personnalisé
st.markdown("""
    <style>
    body { background-color: #121212; color: #e0e0e0; font-size: 12px; }
    .container { padding-top: 10px; padding-bottom: 10px; }
    .card {
        border-radius: 10px; border: none;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        background-color: #1c1c1c;
    }
    .card-header {
        background-color: #4CAF50;
        border-top-left-radius: 10px; border-top-right-radius: 10px;
        padding: 8px 12px; font-size: 14px;
    }
    .card-body {
        max-height: 400px; overflow-y: auto;
        padding: 8px; font-size: 12px;
    }
    .message-container { margin-bottom: 12px; display: flex; align-items: flex-start; }
    .message-left, .message-right {
        display: flex; align-items: center; width: 100%;
    }
    .message-left { flex-direction: row; justify-content: flex-start; }
    .message-right { flex-direction: row-reverse; justify-content: flex-end; }

    .message-left img, .message-right img {
        width: 35px; height: 35px; border-radius: 50%; margin: 0 8px;
    }

    .message-left .message, .message-right .message {
        border-radius: 10px; padding: 8px;
        max-width: 50%; font-size: 12px;
    }

    .message-left .message {
        background-color: #4CAF50; color: white;
    }

    .message-right .message {
        background-color: #333333; color: white;
    }
    .small { font-size: 10px; }
    .input-box {
        width: 100%; padding: 8px; border-radius: 10px;
        border: 1px solid #555555; margin-right: 8px;
        font-size: 12px; background-color: #333333;
        color: white;
    }
    .btn-send {
        background-color: #4CAF50;
        color: white; border: none;
        padding: 8px; border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 💾 Initialisation de la session
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# 📩 Fonction principale du chat
def display_chat():
    st.markdown('<div class="container">', unsafe_allow_html=True)

    # 📦 En-tête
    st.markdown("""
    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Chatbot - Aide Pharmacie</h5>
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)

    # 💬 Affichage des messages
    for msg in st.session_state['messages']:
        if isinstance(msg, dict) and msg.get("sender") == "user":
            st.markdown(f"""
            <div class="message-container message-left">
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava6-bg.webp" />
              <div class="message">
                  <p>{msg['content']}</p>
                  <div class="small text-muted">{msg['time']}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        elif isinstance(msg, dict) and msg.get("sender") == "bot":
            st.markdown(f"""
            <div class="message-container message-right">
            <div class="message">
                <p>{msg['content']}</p>
                <div class="small text-muted">{msg['time']}</div>
            </div>
            <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava5-bg.webp" />
        </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # Fin de la card-body

    # 🧾 Formulaire de saisie utilisateur
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "", key="input_text", label_visibility="collapsed",
            placeholder="Écrivez votre message..."
        )
        send_button = st.form_submit_button("Envoyer")

        if send_button and user_input.strip():
            timestamp = datetime.now().strftime("%d %b %I:%M %p")

            # Ajouter message utilisateur
            st.session_state['messages'].append({
                'sender': 'user',
                'content': user_input.strip(),
                'time': timestamp
            })

            # ✅ Obtenir la vraie réponse via LLM
            try:
                full_response = qa_chain.run(user_input).split("Réponse", 1)[-1].strip(": \n")
            except Exception as e:
                full_response = f"❌ Erreur : {str(e)}"

            # Ajouter message du bot
            st.session_state['messages'].append({
                'sender': 'bot',
                'content': full_response,
                'time': timestamp
            })
            st.rerun()
    # 🔁 Bouton reset
    if st.button("🔁 Réinitialiser la conversation"):
        st.session_state['messages'] = []
        st.rerun()
# ▶️ Lancer le chat
display_chat()





