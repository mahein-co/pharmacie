from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from datetime import datetime
from data.mongodb_client import MongoDBClient


# Chargement du modèle d'embedding
model = SentenceTransformer("all-MiniLM-L6-v2")


# Liste des collections à fusionner
sources = {
    "employe": MongoDBClient(collection_name="employe").get_collection(),
    "medicament": MongoDBClient(collection_name="medicament").get_collection(),
    "vente": MongoDBClient(collection_name="vente").get_collection(),
}

# Collection cible unifiée
target_collection = MongoDBClient(collection_name="corpus_rag").get_collection()

# Nettoyage initial (optionnel si tu veux repartir de 0)
target_collection.delete_many({})

def generate_text_vente(doc):
    date = doc.get("date_de_vente")
    date_str = datetime.strftime(date, "%d/%m/%Y") if date else "date inconnue"
    medecin = doc.get("medecin", "inconnu")
    quantite = doc.get("quantite", "X")
    id_med = doc.get("id_medicament", "???")
    return f"Le {date_str}, le médecin {medecin} a vendu {quantite} unités du médicament {id_med}."

def generate_text_employe(doc):
    prenom = doc.get("prenom", "")
    nom = doc.get("nom", "")
    fonction = doc.get("fonction", "inconnue")
    categorie = doc.get("categorie", "")
    salaire = doc.get("salaire", "N/A")
    
    date_naissance = doc.get("date_naissance")
    naissance_str = datetime.strftime(date_naissance, "%d/%m/%Y") if date_naissance else "inconnue"
    
    date_embauche = doc.get("date_embauche")
    embauche_str = datetime.strftime(date_embauche, "%d/%m/%Y") if date_embauche else "inconnue"
    
    return (
        f"{nom} {prenom}, né le {naissance_str}, "
        f"travaille comme {fonction} ({categorie}) depuis le {embauche_str} "
        f"avec un salaire de {salaire:,} MGA."
    )

def generate_text_medicament(doc):
    nom = doc.get("nom", "Nom inconnu")
    categorie = doc.get("categorie", "catégorie inconnue")
    prix_unitaire = doc.get("prix_unitaire", "N/A")
    lot = doc.get("lot_ID", "lot inconnu")
    qte = doc.get("Quantity_arrival", "quantité inconnue")
    fournisseur = doc.get("fournisseur", "fournisseur inconnu")
    prix_fournisseur = doc.get("prix_fournisseur", "N/A")

    date_arrival = doc.get("arrival_date")
    date_arrival_str = date_arrival.strftime("%d/%m/%Y") if date_arrival else "date d'arrivée inconnue"

    date_exp = doc.get("date_expiration")
    date_exp_str = date_exp.strftime("%d/%m/%Y") if date_exp else "date d'expiration inconnue"

    return (
        f"{nom} ({categorie}), reçu le {date_arrival_str} (lot {lot}), "
        f"en quantité de {qte} unités, à un prix fournisseur de {prix_fournisseur} MGA. "
        f"Date d'expiration prévue : {date_exp_str}. Fournisseur : {fournisseur}. "
        f"Prix de vente unitaire : {prix_unitaire} MGA."
    )

# Générateur de texte par collection
text_generators = {
    "employe": generate_text_employe,
    "medicament": generate_text_medicament,
    "vente": generate_text_vente,
}

# Parcours des documents et insertion dans corpus_rag
for source_name, collection in sources.items():
    generator = text_generators[source_name]
    docs = list(collection.find({}))

    print(f"Traitement de {len(docs)} documents de la collection '{source_name}'...")

    for doc in docs:
        texte = generator(doc)
        if not texte.strip():
            continue  # on saute les vides
        vecteur = model.encode(texte).tolist()

        target_collection.insert_one({
            "texte_embedding": texte,
            "embedding": vecteur,
            "source": source_name,
            "id_origine": doc["_id"]
        })

print("✅ Corpus RAG généré avec succès !")
