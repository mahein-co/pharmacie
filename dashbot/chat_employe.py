# from langchain.chains import RetrievalQA
# from langchain_community.chat_models import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from dashbot.recherche_employe import load_retriever_local  
# from dotenv import load_dotenv
# import os

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")

# def create_chatbot():
#     # ✅ Utilisation du retriever local
#     retriever = load_retriever_local()

#     # Modèle de chat OpenAI
#     llm = ChatOpenAI(
#         model="gpt-4o-mini",
#         temperature=0,
#         openai_api_key=api_key
#     )

#     # Prompt d’instruction
#     prompt = PromptTemplate(
#         input_variables=["context", "question"],
#         template="""
#         Tu es un assistant spécialisé dans l'analyse des employés.
#         Utilise uniquement le contexte suivant pour répondre à la question.
#         CONTEXTE:
#         {context}
        
#         QUESTION:
#         {question}
#         Réponse:
#         """
#     )

#     # Création de la chaîne RetrievalQA
#     return RetrievalQA.from_chain_type(
#         llm=llm,
#         retriever=retriever,
#         chain_type_kwargs={"prompt": prompt}
#     )


# dashbot/chat_employe.py

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
        template="""Tu es un assistant spécialisé dans l'analyse des employés.
Réponds à la question de manière claire et précise.

QUESTION :
{question}

RÉPONSE :
"""
    )

    # ✅ Chaîne simple LLM (pas RetrievalQA)
    return LLMChain(llm=llm, prompt=prompt)
