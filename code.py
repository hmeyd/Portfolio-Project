#!/usr/bin/python3
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

API_SIRENE_URL = "https://entreprise.data.gouv.fr/api/sirene/v3"

@app.route("/", methods=["GET", "POST"])
def search_company():
    if request.method == "POST":
        siren = request.form.get("siren")
        if not siren or not siren.isdigit() or len(siren) != 9:
            return jsonify({"error": "SIREN invalide"}), 400
        response = requests.get(f"{API_SIRENE_URL}/siren/{siren}")
        if response.status_code != 200:
            return jsonify({"error": "Entreprise non trouvée"}), 404
        data = response.json()
        return jsonify(data)

    return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=True)