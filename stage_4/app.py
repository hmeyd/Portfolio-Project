
import os
import base64
import requests
import sqlite3
import secrets
import json
import re
from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = secrets.token_hex(16)

# Configuration des variables d'environnement
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
    client_id = "XIZpcDln6Lqu_F7kRAIkt5PZ5TYa"
    client_secret = "NpZMeG_wz_p99RhJRE2kCd4NW3Ma"
    token_url = "https://api.insee.fr/token"

    response = requests.post(
        token_url,
        auth=(client_id, client_secret),
        data={"grant_type": "client_credentials"}
    )

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Erreur lors de la récupération du token :", response.status_code, response.text)
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
            return render_template("search.html", error="Numéro SIRET invalide. Il doit contenir 14 chiffres.")
        token = get_access_token()
        if not token:
            return render_template("search.html", error="Erreur d'authentification à l'API INSEE.")
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        url = API_SIRENE_URL.format(siret=siret)
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json().get("etablissement", {})
                siret = data.get("siret", "")
                if not siret:
                    return render_template("search.html", error="Impossible de récupérer le SIREN à partir du SIRET.")
                # Redirection vers bodacc avec le siren récupéré
                return render_template("results.html", data=data)
            elif response.status_code == 404:
                return render_template("search.html", error="Établissement non trouvé.")
            else:
                return render_template("search.html", error=f"Erreur API : {response.status_code}")
        except requests.exceptions.RequestException as e:
            return render_template("search.html", error=f"Erreur de connexion : {e}")
    return render_template("search.html")






def generate_pdf_url(annonce):
    publicationavis = annonce.get("publicationavis", "A")
    parution = annonce.get("parution", "")
    numerodossier = annonce.get("numerodossier", "0")

    numero_annonce = annonce.get("numeroannonce", "")
    numero_annonce_str = str(numero_annonce)  # Convertir en chaîne

    if numero_annonce_str.isdigit():
        numero_annonce_str = numero_annonce_str.zfill(5)
    else:
        numero_annonce_str = "00000"

    annee = parution[:4] if len(parution) >= 4 else "0000"

    base_url = (
        f"https://www.bodacc.fr/telechargements/COMMERCIALES/PDF/{publicationavis}/"
        f"{annee}/{parution}/"
    )

    # Première tentative avec numerodossier (0 ou autre)
    url_0 = f"{base_url}{numerodossier}/BODACC_{publicationavis}_PDF_Unitaire_{parution}_{numero_annonce_str}.pdf"
    
    # On fait une requête HEAD pour tester si le fichier existe
    try:
        response = requests.head(url_0)
        if response.status_code == 200:
            return url_0
        else:
            # Si le dossier est "0", on essaye avec "1"
            if numerodossier == "0":
                url_1 = f"{base_url}1/BODACC_{publicationavis}_PDF_Unitaire_{parution}_{numero_annonce_str}.pdf"
                response2 = requests.head(url_1)
                if response2.status_code == 200:
                    return url_1
            # Sinon on retourne quand même la première url
                url_3 = f"{base_url}2/BODACC_{publicationavis}_PDF_Unitaire_{parution}_{numero_annonce_str}.pdf"
            return url_3
    except requests.RequestException:
        # En cas d'erreur réseau on retourne quand même la première url
        return url_0
import json
from flask import jsonify

@app.route("/bodacc", methods=["GET", "POST"])
def bodacc():
    if "user" not in session:
        return redirect(url_for("login"))

    results = []

    if request.method == "POST":
        if request.is_json:
            siret_or_siren = request.get_json().get("siret", "").strip()
        else:
            siret_or_siren = request.form.get("siret", "").strip()
    else:
        siret_or_siren = request.args.get("siret", "").strip() or request.args.get("siren", "").strip()

    if not siret_or_siren:
        if request.is_json:
            return jsonify({"error": "Veuillez entrer un numéro SIREN ou SIRET."}), 400
        return render_template("bodacc.html", error="Veuillez entrer un numéro SIREN ou SIRET.")

    if not siret_or_siren.isdigit() or len(siret_or_siren) not in (9, 14):
        msg = "Numéro SIREN ou SIRET invalide."
        if request.is_json:
            return jsonify({"error": msg}), 400
        flash(msg, "warning")
        return render_template("bodacc.html", error=msg)

    siren = siret_or_siren[:9] if len(siret_or_siren) == 14 else siret_or_siren

    url = f"https://bodacc-datadila.opendatasoft.com/api/records/1.0/search/?dataset=annonces-commerciales&q={siren}&rows=50&sort=dateparution"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        records = resp.json().get("records", [])
        for rec in records:
            fields = rec.get("fields", {})
            description = fields.get("modificationsgenerales", "")
            if description:
                try:
                    description = json.loads(description)
                    if isinstance(description, dict):
                        description = ", ".join(f"{k} : {v}" for k, v in description.items())
                except Exception:
                    pass
            results.append({
                "date_parution": fields.get("dateparution", ""),
                "type_document": fields.get("familleavis_lib", ""),
                "source": fields.get("tribunal", ""),
                "type_avis": fields.get("typeavis_lib") or fields.get("typeavis", ""),
                "reference": fields.get("numeroannonce", ""),
                "description": description or "",
                "pdf_url": fields.get("urlpdf") or generate_pdf_url(fields)
            })
        if not results:
            flash("Aucune annonce trouvée pour ce SIREN.", "info")
    except requests.exceptions.RequestException as e:
        if request.is_json:
            return jsonify({"error": f"Erreur récupération annonces BODACC : {e}"}), 500
        flash(f"Erreur récupération annonces BODACC : {e}", "danger")

    if request.is_json:
        return jsonify({"results": results})
    return render_template("bodacc.html", results=results)



@app.route('/prospection', methods=['GET'])
def prospection():
    try:
        token = get_access_token()
        if not token:
            flash("Impossible d'obtenir un token INSEE", "error")
            return render_template("prospection.html", entreprises=[])

        url = "https://api.insee.fr/entreprises/sirene/V3.11/unites-legales"



        codes_naf = ["6201Z", "6202A", "6202B"]
        naf_query = " OR ".join([f'activitePrincipaleUniteLegale:{code}' for code in codes_naf])

        query = f"({naf_query})"
        params = {
            "q": query,
            "nombre": 50
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

        entreprises = data.get("unitesLegales", [])

        results = []
        for ent in entreprises:
            results.append({
                "siren": ent.get("siren"),
                "nom": ent.get("denominationUniteLegale") or ent.get("nomUniteLegale"),
                "ville": ent.get("l1Normalisee") or "N/A"
            })

        return render_template("prospection.html", entreprises=results)

    except requests.RequestException as e:
        flash(f"Erreur API SIRENE : {e}", "error")
        return render_template("prospection.html", entreprises=[])



if __name__ == "__main__":
    app.run(debug=True)
