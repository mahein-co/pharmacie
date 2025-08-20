import logging
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from data.config import mongo_username, mongo_password, mongo_app_name, mongo_cluster

# Logger
logging.basicConfig(
    filename='mongodb.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MongoDBClient:
    def __init__(self, db_name="pharmacie", collection_name="vente"):
        try:
            uri = (
                f"mongodb+srv://{mongo_username}:{mongo_password}"
                f"@{mongo_cluster}.sdly3uh.mongodb.net/?retryWrites=true"
                f"&w=majority&appName={mongo_app_name}"
            )

            self.client = MongoClient(
                uri,
                server_api=ServerApi('1'),
                tls=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=30000
            )
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            self.ping()
        except Exception as e:
            logger.exception("Erreur d'initialisation de la connexion MongoDB.")

    def ping(self):
        try:
            self.client.admin.command('ping')
            logger.info("Connexion MongoDB établie avec succès.")
        except Exception as e:
            logger.error(f"Échec du ping MongoDB: {e}")
            raise
    
    def make_specific_pipeline(self, pipeline:list, title:str)-> list:
        try:
            result = list(self.collection.aggregate(pipeline,  allowDiskUse=True, maxTimeMS=180000))
            if result:
                logger.info(f"Pipeline de {title.upper()} a bien réussi.")
                return result
            else:
                return []

        except Exception as e:
            logger.exception(f"Erreur lors de {title.upper()} avec l'erreur {e}.")
            return []
        
    def get_collection(self):
        return self.collection

    def count_distinct_agg(self, field_name: str) -> int:
        """Version performante via agrégation pour compter les valeurs distinctes."""
        try:
            pipeline = [
                {"$group": {"_id": f"${field_name}"}},
                {"$count": "distinct_count"}
            ]
            result = list(self.collection.aggregate(pipeline))
            count = result[0]["distinct_count"] if result else 0
            logger.info(f"{count} valeurs distinctes trouvées (via aggregation) pour '{field_name}'.")
            return count
        except Exception as e:
            logger.exception(f"Erreur dans l'agrégation distincte pour '{field_name}'.")
            return 0
        
    def ventes_completes(self, pipeline:list) -> list:
        try:
            result = list(self.collection.aggregate(pipeline))
            logger.info(f"{len(result)} ventes complètes récupérées.")
            return result
        except Exception as e:
            logger.exception("Erreur lors de la récupération des ventes complètes.")
            return []

    def find_all_documents(self):
        try:
            documents = list(self.collection.find())
            logger.info(f"{len(documents)} documents récupérés depuis la collection.")
            return documents
        except Exception as e:
            logger.exception("Erreur lors de la lecture des documents.")
            return []
        
        