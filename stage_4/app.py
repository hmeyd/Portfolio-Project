import os
import base64
import requests
import sqlite3
import secrets
import json
from flask import Flask, request, render_template, redirect, url_for, session, flash
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = secrets.token_hex(16)

# Variables d'environnement
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = "https://api.insee.fr/token"
API_SIRENE_URL = "https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}"

BODACC_API_URL = "https://bodacc-datadila.opendatasoft.com/api/records/1.0/search/?dataset=annonces-commerciales&q="


# Configuration Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")
mail = Mail(app)


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


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()
        if not user:
            return render_template("forgot_password.html", error="Email introuvable.")

        token = secrets.token_urlsafe(32)
        session['reset_token'] = token
        session['reset_email'] = email
        reset_link = url_for("reset_password", token=token, _external=True)

        msg = Message("Réinitialisation de votre mot de passe", recipients=[email])
        msg.body = f"Bonjour,\n\nVoici votre lien pour réinitialiser le mot de passe : {reset_link}\n\nCe lien est temporaire."
        try:
            mail.send(msg)
            return render_template("forgot_password.html", message="Un lien a été envoyé à votre adresse email.")
        except Exception as e:
            print("Erreur d'envoi d'email :", e)
            return render_template("forgot_password.html", error="Erreur lors de l'envoi du mail.")
    return render_template("forgot_password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token") if request.method == "GET" else request.form.get("token")
    if session.get('reset_token') != token:
        return render_template("reset_password.html", error="Token invalide ou expiré.", token=token)

    if request.method == "POST":
        new_password = request.form.get("new_password")
        if new_password:
            hashed_pw = bcrypt.generate_password_hash(new_password).decode("utf-8")
            email = session.get('reset_email')
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pw, email))
            conn.commit()
            conn.close()
            session.pop('reset_token', None)
            session.pop('reset_email', None)
            flash("Mot de passe modifié avec succès.")
            return redirect(url_for("login"))
    return render_template("reset_password.html", token=token)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def search_company():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        siret = request.form.get("siret")

        if not siret or not siret.isdigit() or len(siret) != 14:
            return render_template("results.html", data=None, error="Numéro SIRET invalide. Il doit contenir 14 chiffres.")

        token = get_access_token()
        if not token:
            return render_template("results.html", data=None, error="Erreur d'authentification à l'API INSEE.")

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        url = API_SIRENE_URL.format(siret=siret)
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json().get("etablissement")
                return render_template("results.html", data=data)
            elif response.status_code == 404:
                return render_template("results.html", data=None, error="Établissement non trouvé.")
            else:
                return render_template("results.html", data=None, error=f"Erreur API : {response.status_code}")
        except requests.exceptions.RequestException as e:
            return render_template("results.html", data=None, error=f"Erreur de connexion : {e}")

    return render_template("search.html")


from flask import render_template, request
import requests

@app.route("/bodacc", methods=["GET", "POST"])
def bodacc():
    if "user" not in session:
        return redirect(url_for("login"))

    siret_or_siren = None
    if request.method == "POST":
        siret_or_siren = request.form.get("siret", "").strip()
    else:
        siret_or_siren = request.args.get("siret", "").strip()

    if not siret_or_siren or not siret_or_siren.isdigit() or len(siret_or_siren) not in (9, 14):
        return render_template("bodacc.html", error="Numéro SIREN ou SIRET invalide.", results=None, siret=siret_or_siren)

    siren = siret_or_siren[:9]

    url = f"https://bodacc-datadila.opendatasoft.com/api/records/1.0/search/?dataset=annonces-commerciales&q={siren}&rows=50&sort=dateparution"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        records = data.get("records", [])

        results = []
        for record in records:
            fields = record.get("fields", {})

            # Récupération du lien PDF — souvent dans 'url_pdf' ou 'pdf'
            pdf_url = fields.get("url_pdf") or fields.get("pdf") or None
            # Exemple de lien alternatif (en construisant une url vers bodacc.fr)
            if not pdf_url and "numeroannonce" in fields:
                pdf_url = f"https://www.bodacc.fr/annonce/pdf/{fields['numeroannonce']}"

            # Description, on essaie d'extraire/modificationsgenerales
            description = fields.get("modificationsgenerales", "")
            if description:
                try:
                    # Parfois c'est une chaîne JSON
                    description = json.loads(description)
                    if isinstance(description, dict):
                        description = ", ".join(f"{k} : {v}" for k, v in description.items())
                    else:
                        description = str(description)
                except Exception:
                    # Si erreur JSON, on garde la chaîne brute
                    pass

            results.append({
                "date": fields.get("dateparution", "N/A"),
                "type_document": fields.get("familleavis_lib", "N/A"),
                "source": fields.get("tribunal", "N/A"),
                "type_avis": fields.get("typeavis_lib") or fields.get("typeavis", "N/A"),
                "reference": fields.get("numeroannonce", "N/A"),
                "description": description or "N/A",
                "contenu": fields.get("decision", "N/A"),
                "pdf_url": pdf_url,
            })

        if not results:
            return render_template("bodacc.html", error="Aucune annonce trouvée.", results=None, siret=siret_or_siren)

        return render_template("bodacc.html", results=results, siret=siret_or_siren)

    except requests.exceptions.RequestException as e:
        return render_template("bodacc.html", error=f"Erreur lors de la récupération des données : {e}", results=None, siret=siret_or_siren)


@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return "URL manquante", 400
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        headers = {
            'Content-Disposition': 'attachment; filename=document.pdf',  # adapter le nom de fichier
            'Content-Type': r.headers.get('Content-Type', 'application/octet-stream'),
        }
        return Response(r.iter_content(chunk_size=8192), headers=headers)
    except requests.RequestException:
        return "Erreur lors du téléchargement", 500

if __name__ == "__main__":
    app.run(debug=True)