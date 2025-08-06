import random
from data.mongodb_client import MongoDBClient

overview_collection = MongoDBClient(collection_name="overview")
overview_collection = overview_collection.get_collection()

medecins = ['Rakoto', 'Andrianina', 'Rasoanaivo', 'Razafindrakoto', "",
       'Rakotondrabe', 'Andriambelo', 'Rasoloarison', 'Rakotobe',
       'Ramaroson', 'Rafanomezantsoa', 'Randriambololona', 'Rakotomalala',
       'Andriamanjato', 'Razafinjatovo', 'Rabemanantsoa', 'Ralison',
       'Andrianarisoa', 'Rabetokotany', 'Andriatsitohaina',
       'Rakotonirina', 'Ravelomanana', 'Andriamanisa', 'Rabary',
       'Ramiandrisoa', 'Andriamifidy', 'Raveloson', 'Andrianantenaina',
       'Razanajatovo', 'Rabefarihy', 'Rabemananjara', 'Andrianasy',
       'Randriamanantena', 'Ralainirina', 'Razafindraibe',
       'Ramiaramanana', 'Randrianarivony', 'Andriantseheno', 'Rakotozafy',
       'Rabenandrasana', 'Ramiandrasoa', 'Rabemananoro', 'Rakotondrazaka',
       'Ramaromanana', 'Razafintsalama', 'Andriamamonjy',
       'Rakotonindrina', 'Rabemila', 'Rabarison', 'Andrianjatovo',
       'Rakotomanga', 'Rasamimanana', 'Ramiaramampionona',
       'Andriambololona', 'Razafimahatratra', 'Rakotozandriny',
       'Ramamonjisoa', 'Ravelonarivo', 'Randrianarisoa', 'Raharisoa',
       'Ramilison', 'Ravoahangy', 'Randriamahefa', 'Rasolonjatovo',
       'Rabezandrina', 'Ravoajanahary', 'Andriamampionona', 'Rafidison',
       'Andrianomenjanahary', 'Rakotoniaina', 'Ramasimanana',
       'Rakotoniarivo', 'Raharimalala', 'Rabeharisoa', 'Andriamasy',
       'Ramarokoto', 'Razafindrazaka', 'Andriamahitsy',
       'Raherinandrasana', 'Rakotovao', 'Andriantsalama',
       'Randriamampionona', 'Rakotondravao', 'Rakotomavo', 'Andrianjafy',
       'Rasolonirina', 'Rakotomandimby', 'Rasoazanany', 'Ravelomanantsoa',
       'Rakotondramanana', 'Andriamboavonjy']

def add_medecin(docs):
    for i, doc in enumerate(docs[26046:], start=26046):
        random_client = random.choice(medecins)
        overview_collection.update_one(
            {"_id": doc["_id"]},            
            {"$set": {"medecin": random_client}} 
        )
        print(f"Updated document[{i}] with medecin: {random_client}")

def update_date():
    overview_collection.update_many(
        { "date_expiration": { "$type": "string" } },  # On cible les chaînes
        [
            {
                "$set": {
                    "date_expiration": {
                        "$dateFromString": {
                            "dateString": "$date_expiration",
                            "format": "%Y-%m-%d"  # Adapte si ton format est différent
                        }
                    }
                }
            }
        ]
    )


if __name__ == "__main__":
    docs = overview_collection.find()
    add_medecin(docs)
    # update_date()
    print("Dates updated successfully.")