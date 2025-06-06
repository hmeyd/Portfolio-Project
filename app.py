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
API_SIRENE_URL = "https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}"
API_ETABLISSEMENT_URL = "https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}"

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

def get_adresse_etablissement(siret, token):
    url = API_ETABLISSEMENT_URL.format(siret=siret)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("etablissement", {}).get("adresseEtablissement")
    else:
        print("Erreur récupération adresse :", response.status_code, response.text)
        return None

@app.route("/", methods=["GET", "POST"])
def search_company():
    if request.method == "POST":
        siren = request.form.get("siren")

        if not siren or not siren.isdigit() or len(siren) != 9:
            return render_template("results.html", data=None, adresse=None, error="Numéro SIREN invalide.")

        token = get_access_token()
        if not token:
            return render_template("results.html", data=None, adresse=None, error="Impossible de récupérer le jeton.")

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        url = API_SIRENE_URL.format(siren=siren)
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_data = response.json()
                data = json_data.get("uniteLegale")
                siret_siege = json_data.get("header", {}).get("siretSiegeUniteLegale")
                adresse = get_adresse_etablissement(siret_siege, token) if siret_siege else None

                return render_template("results.html", data=data, adresse=adresse)
            elif response.status_code == 404:
                return render_template("results.html", data=None, adresse=None, error="Entreprise non trouvée.")
            else:
                return render_template("results.html", data=None, adresse=None, error=f"Erreur : {response.status_code}")
        except requests.exceptions.RequestException as e:
            return render_template("results.html", data=None, adresse=None, error=f"Erreur de connexion : {e}")

    return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=True)