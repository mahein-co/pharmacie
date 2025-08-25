from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def create_chatbot():
    # Modèle de chat OpenAI
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=api_key
    )

    # Prompt simple (pas de {context})
    prompt = PromptTemplate(
        input_variables=["question"],
        template="""Tu es un assistant spécialisé dans l'analyse des approvisionnements.
Réponds à la question de manière claire et précise.

QUESTION :
{question}

RÉPONSE :
"""
    )

    # ✅ Chaîne simple LLM (pas RetrievalQA)
    return LLMChain(llm=llm, prompt=prompt)