import os
import base64
import requests
from flask import Flask, request, render_template
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = "https://api.insee.fr/token"
API_SIRENE_URL = "https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}"

app = Flask(__name__)

def get_access_token():
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Erreur lors de la récupération du token :", response.status_code, response.text)
        return None

@app.route("/", methods=["GET", "POST"])
def search_company():
    if request.method == "POST":
        siret = request.form.get("siret")
        print(f"[DEBUG] SIRET saisi : {siret}")

        if not siret or not siret.isdigit() or len(siret) != 14:
            print("[DEBUG] Numéro SIRET invalide.")
            return render_template("results.html", data=None, error="Numéro SIRET invalide.")

        token = get_access_token()
        print(f"[DEBUG] Token récupéré : {token}")

        if not token:
            print("[DEBUG] Impossible d'obtenir le token.")
            return render_template("results.html", data=None, error="Erreur d'authentification.")

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        # ✅ Utilisation de l’URL corrigée
        url = API_SIRENE_URL.format(siret=siret)
        print(f"[DEBUG] URL appelée : {url}")

        try:
            response = requests.get(url, headers=headers)
            print(f"[DEBUG] Status code : {response.status_code}")
            print(f"[DEBUG] Réponse brute : {response.text}")

            if response.status_code == 200:
                json_data = response.json()
                data = json_data.get("etablissement")
                print(f"[DEBUG] Données établissement : {data}")
                return render_template("results.html", data=data)
            elif response.status_code == 404:
                print("[DEBUG] Établissement non trouvé.")
                return render_template("results.html", data=None, error="Établissement non trouvé.")
            else:
                print(f"[DEBUG] Erreur inconnue : {response.status_code}")
                return render_template("results.html", data=None, error=f"Erreur API : {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] Exception lors de la requête : {e}")
            return render_template("results.html", data=None, error=f"Erreur de connexion : {e}")

    return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=True)
