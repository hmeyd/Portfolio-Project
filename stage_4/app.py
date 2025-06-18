import os
import base64
import requests
import sqlite3
import secrets  # Pour générer une clé aléatoire
from flask import Flask, request, render_template, redirect, url_for, session, flash

from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)            # ← Ici tu l'utilises (OK)
app.secret_key = 'dev-secret' # ← Ici tu l'utilises (OK)

conn = sqlite3.connect("users.db")

# Charger les variables d'environnement
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = "https://api.insee.fr/token"
API_SIRENE_URL = "https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}"
app = Flask(__name__)
# :closed_lock_with_key: Générer une nouvelle clé secrète à chaque redémarrage
app.secret_key = secrets.token_hex(16)


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

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user[0], password):
            session["user"] = email
            return redirect(url_for("search_company"))
        else:
            return render_template("login.html", error="Identifiants incorrects.")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email, phone, password) VALUES (?, ?, ?)", (email, phone, hashed_pw))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("Ce numéro ou email est déjà utilisé.", "error")
            return render_template("register.html")

        conn.close()
        session["user"] = phone or email
        return redirect(url_for("search_company"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/login_phone", methods=["GET", "POST"])
def login_phone():
    if request.method == "POST":
        country_code = request.form["country_code"]
        phone = request.form["phone"]
        password = request.form["password"]
        full_phone = country_code + phone

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE phone = ?", (full_phone,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user[0], password):
            session["user"] = full_phone
            return redirect(url_for("search_company"))
        else:
            flash("Numéro ou mot de passe incorrect.", "error")
            return render_template("login_phone.html")

    return render_template("login_phone.html")


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