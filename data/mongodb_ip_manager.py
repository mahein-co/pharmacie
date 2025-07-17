import requests
import datetime
import os
import logging
from requests.auth import HTTPDigestAuth

from data.config import mongo_project_id, mongo_private_key, mongo_public_key


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mongodb_ip.log"),   
        logging.StreamHandler()                      
    ]
)


class MongoDBIPManager:
    def __init__(self):
        self.public_key = mongo_public_key
        self.private_key = mongo_private_key
        self.project_id = mongo_project_id
        self.base_url = f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{self.project_id}/accessList"
        self.auth = HTTPDigestAuth(self.public_key, self.private_key)

    def get_current_ip(self):
        try:
            ip = requests.get("https://api.ipify.org").text
            logging.info(f"📡 IP publique détectée : {ip}")
            return ip
        except Exception as e:
            logging.error(f"❌ Impossible de récupérer l'adresse IP : {e}")
            return None

    def ip_exists(self, ip):
        """
        Vérifie si une IP est déjà présente dans la liste d'accès MongoDB Atlas.
        """
        try:
            response = requests.get(self.base_url, auth=self.auth)
            if response.status_code == 200:
                ip_list = response.json().get("results", [])
                exists = any(entry["ipAddress"] == ip for entry in ip_list)
                if exists:
                    logging.info(f"🔍 IP {ip} est déjà présente dans la liste.")
                else:
                    logging.info(f"🔍 IP {ip} n'est PAS dans la liste.")
                return exists
            else:
                logging.error(f"❌ Erreur {response.status_code} lors de la récupération de la liste IP : {response.text}")
                return False
        except Exception as e:
            logging.error(f"❌ Une erreur est survenue pendant la vérification de l'IP : {e}")
            return False

    def add_ip(self, ip=None, comment="Ajout automatique par script Python"):
        if ip is None:
            ip = self.get_current_ip()
            if ip is None:
                return

        if self.ip_exists(ip):
            logging.info(f"✅ IP {ip} existe déjà, ajout non nécessaire.")
            return

        payload = [{
            "ipAddress": ip,
            "comment": comment
        }]

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                auth=self.auth
            )

            if response.status_code == 201:
                logging.info(f"✅ IP {ip} ajoutée avec succès à MongoDB Atlas.")
            elif response.status_code == 409:
                logging.info(f"ℹ️ IP {ip} est déjà présente dans la liste.")
            else:
                logging.error(f"❌ Erreur {response.status_code} : {response.text}")
        except Exception as e:
            logging.error(f"❌ Une erreur s'est produite pendant l'ajout : {e}")

    def remove_ip(self, ip):
        url = f"{self.base_url}/{ip}"

        try:
            response = requests.delete(url, auth=self.auth)

            if response.status_code == 200:
                logging.info(f"🗑️ IP {ip} supprimée avec succès de MongoDB Atlas.")
            elif response.status_code == 404:
                logging.warning(f"❗ IP {ip} introuvable dans la liste d'accès.")
            else:
                logging.error(f"❌ Erreur {response.status_code} : {response.text}")
        except Exception as e:
            logging.error(f"❌ Une erreur s'est produite pendant la suppression : {e}")


