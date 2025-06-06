import requests

ACCESS_TOKEN = "96b2de82-9878-3049-9dcd-e85a099714cf"

def get_company_data(siren):
    url = f"https://api.insee.fr/entreprises/sirene/V3/siren"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    params = {
        "q": f"siren:{siren}"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        # Le résultat est une liste dans 'etablissements'
        etablissements = data.get('etablissements', [])
        if etablissements:
            entreprise = etablissements[0]
            print("Dénomination sociale:", entreprise.get('uniteLegale', {}).get('denominationUniteLegale', 'N/A'))
            print("SIREN:", entreprise.get('siren', 'N/A'))
            print("Date début activité:", entreprise.get('uniteLegale', {}).get('dateCreationUniteLegale', 'N/A'))
            adresse = entreprise.get('adresseEtablissement', {})
            adresse_str = f"{adresse.get('numeroVoieEtablissement', '')} {adresse.get('typeVoieEtablissement', '')} {adresse.get('libelleVoieEtablissement', '')} {adresse.get('codePostalEtablissement', '')} {adresse.get('libelleCommuneEtablissement', '')}".strip()
            print("Adresse siège:", adresse_str if adresse_str else "N/A")
            print("Forme juridique:", entreprise.get('uniteLegale', {}).get('formeJuridiqueUniteLegale', 'N/A'))
            print("Code APE:", entreprise.get('uniteLegale', {}).get('activitePrincipaleUniteLegale', 'N/A'))
        else:
            print("Aucune entreprise trouvée pour ce SIREN.")
    else:
        print(f"Erreur HTTP {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    siren = "732829320"
    get_company_data(siren)
