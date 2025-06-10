import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_token():
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post("https://api.insee.fr/token", headers=headers, data=data)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ Token obtenu :", token)
        return token
    else:
        print("❌ Erreur récupération token:", response.status_code, response.text)
        return None

def fetch_etablissement(siret):
    token = get_token()
    if not token:
        print("Impossible d’obtenir le token, arrêt du test.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    url = f"https://api.insee.fr/entreprises/sirene/V3/siret/{siret}"
    print("🔎 URL appelée :", url)

    response = requests.get(url, headers=headers)
    print("📦 Status code :", response.status_code)
    print("📝 Réponse brute :", response.text)

if __name__ == "__main__":
    siret_test = "73282932000074"  # <-- numéro SIRET valide à tester
    fetch_etablissement(siret_test)