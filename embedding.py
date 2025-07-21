from sentence_transformers import SentenceTransformer
from data.mongodb_client import MongoDBClient
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from datetime import datetime


model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer('all-MiniLM-L6-v2') 

vente_collection = MongoDBClient(collection_name="vente")
ventes = vente_collection.find_all_documents()
medicaments = MongoDBClient(collection_name="medicament").find_all_documents()
employees = MongoDBClient(collection_name="employe").find_all_documents()

def embed_docs(docs):
    for doc in docs:
        doc['embedding'] = model.encode(doc['content']).tolist()


def embed_vente(docs, collection):
    for doc in docs:
        # Construction du texte à partir des champs
        date_str = doc.get("date_de_vente")
        date_fmt = datetime.strftime(date_str, "%d/%m/%Y") if date_str else "date inconnue"
        medecin = doc.get("medecin", "inconnu")
        quantite = doc.get("quantite", 0)
        id_medoc = doc.get("id_medicament", "???")

        texte = f"Le {date_fmt}, le médecin {medecin} a vendu {quantite} unités du médicament {id_medoc}."

        # Embedding
        vecteur = model.encode(texte).tolist()

        # Mise à jour MongoDB
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {
                "embedding": vecteur,
                "texte_embedding": texte  # facultatif mais utile pour debug ou trace
            }}
        )



if __name__ == "__main__":

    collection = vente_collection.get_collection()

    embed_vente(ventes, collection)
    # embed_docs(medicaments)
    # embed_docs(employees)

    # Save the embeddings back to MongoDB
    # MongoDBClient(collection_name="vente").insert_document(ventes)
    # MongoDBClient(collection_name="medicament").insert_document(medicaments)
    # MongoDBClient(collection_name="employe").insert_document(employees)

    # print("Embeddings have been successfully generated and saved to MongoDB.")





