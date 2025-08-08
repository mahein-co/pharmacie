import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# IMAGES -------------------------------------------
# finance
finance_icon_b64 = get_base64_image("assets/icons/money.png")
finance_icon_html = f'<img src="data:image/png;base64,{finance_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# vente
ventes_icon_b64 = get_base64_image("assets/icons/vente.png")
ventes_icon_html = f'<img src="data:image/png;base64,{ventes_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# stock
stock_icon_b64 = get_base64_image("assets/icons/stock.png")
stock_icon_html = f'<img src="data:image/png;base64,{stock_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# perte
perte_icon_b64 = get_base64_image("assets/icons/perte.png")
perte_icon_html = f'<img src="data:image/png;base64,{perte_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# employees
employees_icon_b64 = get_base64_image("assets/icons/employees.png")
employees_icon_html = f'<img src="data:image/png;base64,{employees_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# salaire
salaire_icon_b64 = get_base64_image("assets/icons/salaire.png")
salaire_icon_html = f'<img src="data:image/png;base64,{salaire_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'
# age
age_icon_b64 = get_base64_image("assets/icons/age.png")
age_icon_html = f'<img src="data:image/png;base64,{age_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# panier
panier_icon_b64 = get_base64_image("assets/icons/basket.png")
panier_icon_html = f'<img src="data:image/png;base64,{panier_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# calendar
calendar_icon_b64 = get_base64_image("assets/icons/profit.png")
calendar_icon_html = f'<img src="data:image/png;base64,{calendar_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# medicament
medicament_icon_b64 = get_base64_image("assets/icons/capsule.png")
medicament_icon_html = f'<img src="data:image/png;base64,{medicament_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# medicament en critique
medicament_critique_icon_b64 = get_base64_image("assets/icons/sold-out.png")
medicament_critique_icon_html = f'<img src="data:image/png;base64,{medicament_critique_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# medicament en surplus
medicament_surplus_icon_b64 = get_base64_image("assets/icons/out-of-stock.png")
medicament_surplus_icon_html = f'<img src="data:image/png;base64,{medicament_surplus_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# approvisionnement
approvisionnement_icon_b64 = get_base64_image("assets/icons/approvisionnement.png")
approvisionnement_icon_html = f'<img src="data:image/png;base64,{approvisionnement_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# fournisseur
fournisseur_icon_b64 = get_base64_image("assets/icons/fournisseur.png")
fournisseur_icon_html = f'<img src="data:image/png;base64,{fournisseur_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# commande
commande_icon_b64 = get_base64_image("assets/icons/vitamin.png")
commande_icon_html = f'<img src="data:image/png;base64,{commande_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# Prix de vente
prix_vente_icon_b64 = get_base64_image("assets/icons/ventes-flash.png")
prix_vente_icon_html = f'<img src="data:image/png;base64,{prix_vente_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# Prix fournisseur
prix_fournisseur_icon_b64 = get_base64_image("assets/icons/budgeting.png")
prix_fournisseur_icon_html = f'<img src="data:image/png;base64,{prix_fournisseur_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# Evaluation - rmse
evaluation_rmse_icon_b64 = get_base64_image("assets/icons/settings.png")
evaluation_rmse_icon_html = f'<img src="data:image/png;base64,{evaluation_rmse_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'

# Prediction
prediction_icon_b64 = get_base64_image("assets/icons/predictive.png")
prediction_icon_html = f'<img src="data:image/png;base64,{prediction_icon_b64}"  style="position: relative; top: 0; left: -7px; width:70px;">'


