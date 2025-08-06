import os
import logging
from datetime import datetime

import numpy as np
import faiss
from openai import OpenAI

from data.mongodb_client import MongoDBClient
from data.config import openai_api_key

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


# Connect into OpenAI API
client_openai = OpenAI(api_key=openai_api_key)


# Collection sources
overview_collection = MongoDBClient(collection_name="overview").get_collection()

# Collection cible unifiée
corpus_collection = MongoDBClient(collection_name="corpus_rag").get_collection()

# Generate overview text
def generate_overview_text(doc):
    def convert_mongo_date(value):
        if isinstance(value, dict) and "$date" in value:
            timestamp = int(value["$date"]["$numberLong"]) / 1000
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        return value  # déjà une string ou None

    # Médicament
    nom_medicament = doc.get("nom_medicament", "Nom inconnu")
    categorie = doc.get("medicament_categorie", "Catégorie inconnue")
    lot = doc.get("lot_id", "Lot inconnu")
    fournisseur = doc.get("fournisseur", "Fournisseur inconnu")
    prix_unitaire = doc.get("prix_unitaire", "N/A")
    prix_fournisseur = doc.get("prix_fournisseur", "N/A")
    quantite_arrivee = doc.get("quantity_arrival", "Inconnue")
    quantite_restante = doc.get("quantite_restante", "Inconnue")
    marge = doc.get("marge_prix", "N/A")
    valeur_stock = doc.get("valeur_stock", "N/A")

    # Médecin
    medecin = doc.get("medecin", "Médecin inconnu")

    # Dates
    date_exp = convert_mongo_date(doc.get("date_expiration"))
    date_arrival = convert_mongo_date(doc.get("arrival_date"))
    date_vente = convert_mongo_date(doc.get("date_de_vente"))
    date_embauche = convert_mongo_date(doc.get("date_embauche"))
    date_naissance = convert_mongo_date(doc.get("date_naissance"))

    # Vente
    quantite_vendue = doc.get("quantite", "Inconnue")
    prix_vente = doc.get("prix_vente", "N/A")

    # Employé
    nom_employe = doc.get("nom_employe", "Nom inconnu")
    prenom_employe = doc.get("prenom_employe", "Prénom inconnu")
    fonction = doc.get("fonction", "Fonction inconnue")
    categorie_emp = doc.get("employe_categorie", "Catégorie inconnue")
    sexe = doc.get("sex", "Inconnu")
    salaire = doc.get("salaire", "N/A")

    # Retard et manquant
    retard = doc.get("retard_jour", 0)
    quantite_manquante = doc.get("quantite_manquante", 0)
    manque_gagner = doc.get("manque_gagner", 0)

    return f"""
        Le médicament **{nom_medicament}** ({categorie}), lot **{lot}**, reçu le **{date_arrival}** 
        de **{fournisseur}**, en **{quantite_arrivee} unités**, est vendu à **{prix_unitaire} MGA** 
        (prix fournisseur : {prix_fournisseur} MGA, marge : {marge} MGA). 
        La date d’expiration est fixée au **{date_exp}**.
        {'Le médecin prescripteur (client) est ' + str(medecin) if medecin else ''} 
        Le stock restant est de **{quantite_restante} unités**, pour une valeur totale de **{valeur_stock} MGA**.\n\n
        Lors de la vente du **{date_vente}**, le vendeur est l’employé **{prenom_employe} {nom_employe}** "
        ({sexe}, {fonction}, {categorie_emp}, embauché(e) le {date_embauche}, né(e) le {date_naissance}), 
        ayant un salaire de {salaire} MGA, a vendu **{quantite_vendue} unités** au prix de **{prix_vente} MGA**.\n\n
        {'La livraison de ce médicament a été en retard de ' + str(retard) + ' jour(s). ' if retard > 0 else ''} "
        {"Le besoin de client n'est pas satisfait car il reste "  + str(quantite_manquante) + ' unités manquent, ce qui représente une perte (manque à gagner) de ' + str(manque_gagner) + ' MGA.' if quantite_manquante > 0 else ''}"
    """
    

# Generate embedding text
def embed_text(text: str):
    """Génère un embedding OpenAI pour un texte donné."""
    response = client_openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


FAISS_INDEX_FILE = "faiss_index.bin"
texts = []
embeddings = []

if os.path.exists(FAISS_INDEX_FILE):
    print("Chargement de l'index FAISS existant...")
    index = faiss.read_index(FAISS_INDEX_FILE)
    texts = [doc["text"] for doc in corpus_collection.find()]
    print(f"Index FAISS chargé ({index.ntotal} vecteurs)")
else:
    print("Création d'un nouvel index FAISS...")
    docs = list(overview_collection.find())
    for i, doc in enumerate(docs[12620:15000], start=12620):
        print(f"Traitement du document[{i}] / {len(docs)}")
        text = generate_overview_text(doc)
        embedding = embed_text(text)

        texts.append(text)
        embeddings.append(embedding)

        # Sauvegarde dans MongoDB
        corpus_collection.insert_one({
            "text": text,
            "embedding": embedding,
            "source_id": str(doc["_id"]),
            "created_at": datetime.now()
        })

    embeddings_np = np.array(embeddings, dtype="float32")
    dimension = embeddings_np.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    faiss.write_index(index, FAISS_INDEX_FILE)
    logger.info(f"✅ Nouvel index FAISS créé avec {index.ntotal} vecteurs et sauvegardé")


def search_rag(query, k=70):
    """Recherche des documents pertinents pour une requête utilisateur."""
    logger.info(f"🔍 Recherche pour la requête : {query}")

    query_embedding = embed_text(query)
    query_np = np.array([query_embedding], dtype="float32")

    distances, indices = index.search(query_np, k)

    results = []
    for idx in indices[0]:
        if idx == -1:
            continue
        result_doc = corpus_collection.find_one({"text": texts[idx]})
        results.append(result_doc["text"])
    
    logger.info(f"✅ {len(results)} résultats trouvés")
    return results


if __name__ == "__main__":
    print("Longueur de corpus insere: ", corpus_collection.count_documents({}))
    # query = "Quels médicaments sont en retard de livraison ?"
    # results = search_rag(query)

    # for i, r in enumerate(results, 1):
        # print(f"\n--- Résultat {i} ---\n{r[:500]}...")


# INDEXATION 
# {
#   "mappings": {
#     "dynamic": true,
#     "fields": {
#       "embedding": {
#         "dimensions": 1536,
#         "similarity": "cosine",
#         "type": "knnVector"
#       }
#     }
#   }
# }