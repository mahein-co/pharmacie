from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi

from config import mongo_username, mongo_password, mongo_app_name, mongo_cluster

uri = f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_cluster}.sdly3uh.mongodb.net/?retryWrites=true&w=majority&appName={mongo_app_name}"

client = MongoClient(uri, server_api=ServerApi('1'), tls=True, tlsCAFile=certifi.where())


db = client["pharmacie"]
collection = db["client"]

# Ajout d'un document
collection.insert_one({"ID_Client":1, "Nom": "Jean", "Prenom":"Luc", "Historique_Achat": "Acheté Doliprane et Ibuprofène"})

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
