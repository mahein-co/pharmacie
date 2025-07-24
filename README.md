# pharmaco

# Creation et activation de variable d'environnement

python -m venv .venv

<!-- Sur Windows -->

source .venv/bin/activate

<!-- Sur linux -->

.venv\Scripts\activate

# Installation de librairies

pip install -r requirements.txt

# Creation de secrets key dans fichier .env

HUGGINGFACEHUB_API_TOKEN
OPENAI_API_KEY

MONGO_USERNAME
MONGO_PASSWORD
MONGO_APP_NAME
MONGO_CLUSTER
MONGO_PROJECT_ID
MONGO_PUBLIC_KEY
MONGO_PRIVATE_KEY

# Lancer l'appilcation

streamlit run 1_DASHBOARD.py
