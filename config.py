from dotenv import load_dotenv
import os

load_dotenv()

mongo_app_name = os.getenv("MONGO_APP_NAME")
mongo_username = os.getenv("MONGO_USERNAME")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_cluster = os.getenv("MONGO_CLUSTER")


