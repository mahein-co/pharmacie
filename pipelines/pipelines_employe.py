Salaire_moyen =[{
     "$group": {
      "_id": None,
      "salaire_moyen": { "$avg": "$salaire" }
    }
}]

Age_moyen =[{
     "$addFields": {
            "age": {
                "$dateDiff": {
                    "startDate": "$date_naissance",
                    "endDate": "$$NOW",
                    "unit": "year"
                }
            }
        }
    },
    {
        "$group": {
            "_id": None,
            "age_moyen": { "$avg": "$age" }
        }
    }
]

Eff_categorie = [{
    "$group": {
                "_id": "$categorie",
                "Effectif": {"$sum": 1}
            }
}]

Eff_fonction = [{
    "$group": {
                "_id":"$fonction",
                "Effectif": {"$sum":1}
            }
}]