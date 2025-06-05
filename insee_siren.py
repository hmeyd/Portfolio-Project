import requests

# Ton token Bearer obtenu
token = "96b2de82-9878-3049-9dcd-e85a099714cf"
siren = "552100554"
url = f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}"

headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(url, headers=headers)
data = response.json()

unite_legale = data.get("uniteLegale", {})
periodes = unite_legale.get("periodesUniteLegale", [])

# Récupération des champs généraux
siren_val = unite_legale.get("siren")
date_creation = unite_legale.get("dateCreationUniteLegale")

# On prend la première période (la plus récente)
periode_recente = periodes[0] if periodes else {}

denomination = periode_recente.get("denominationUniteLegale")
activite = periode_recente.get("activitePrincipaleUniteLegale")
etat_admin = periode_recente.get("etatAdministratifUniteLegale")

result = {
    "siren": siren_val,
    "dateCreationUniteLegale": date_creation,
    "denominationUniteLegale": denomination,
    "activitePrincipaleUniteLegale": activite,
    "etatAdministratifUniteLegale": etat_admin,
}

print(result)
