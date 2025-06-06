import requests

API_SIRENE_URL = "https://api.insee.fr/entreprises/sirene/V3.11/siren/{348991555}"
API_KEY = "214c0e62-bc3c-4fd6-959f-67e5400bdd41"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

siren_test = "348991555"  # Remplace par un vrai SIREN valide
response = requests.get(f"{API_SIRENE_URL}{siren_test}", headers=headers)

print("Statut HTTP :", response.status_code)
print("Réponse API :", response.text)