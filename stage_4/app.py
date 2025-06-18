import os
import base64
import requests
import secrets  # Pour générer une clé aléatoire

from flask import Flask, request, render_template, redirect, url_for, session
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = "https://api.insee.fr/token"
API_SIRENE_URL = "https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}"

app = Flask(__name__)

# 🔐 Générer une nouvelle clé secrète à chaque redémarrage
app.secret_key = secrets.token_hex(16)

# Login utilisateur fictif
USERNAME = os.getenv("APP_USERNAME", "admin")
PASSWORD = os.getenv("APP_PASSWORD", "password")

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
        return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email == USERNAME and password == PASSWORD:
            session["user"] = email
            return redirect(url_for("search_company"))
        else:
            return render_template("login.html", error="Identifiants incorrects.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")

    email = request.form.get("email")
    if email != USERNAME:
        return render_template("forgot_password.html", error="Email non trouvé.")

    token = secrets.token_urlsafe(32)
    session['reset_token'] = token
    session['reset_expiration'] = True

    reset_link = url_for("reset_password", token=token, _external=True)
    print(f"[EMAIL SIMULÉ] Lien de réinitialisation : {reset_link}")

    return render_template("forgot_password.html", message="Lien envoyé. Vérifiez la console.")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token") if request.method == "GET" else request.form.get("token")

    if session.get('reset_token') != token:
        return render_template("reset_password.html", error="Token invalide ou expiré.", token=token)

    if request.method == "POST":
        new_password = request.form.get("new_password")
        if new_password:
            global PASSWORD
            PASSWORD = new_password  # mise à jour simulée du mot de passe
            session.pop('reset_token', None)
            session.pop('reset_expiration', None)
            return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)

@app.route("/", methods=["GET", "POST"])
def search_company():
    # Vérifie si l'utilisateur est connecté
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        siret = request.form.get("siret")

        if not siret or not siret.isdigit() or len(siret) != 14:
            return render_template("results.html", data=None, error="Numéro SIRET invalide.")

        token = get_access_token()

        if not token:
            return render_template("results.html", data=None, error="Erreur d'authentification.")

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        url = API_SIRENE_URL.format(siret=siret)
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_data = response.json()
                data = json_data.get("etablissement")
                return render_template("results.html", data=data)
            elif response.status_code == 404:
                return render_template("results.html", data=None, error="Établissement non trouvé.")
            else:
                return render_template("results.html", data=None, error=f"Erreur API : {response.status_code}")
        except requests.exceptions.RequestException as e:
            return render_template("results.html", data=None, error=f"Erreur de connexion : {e}")

    return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=True)
