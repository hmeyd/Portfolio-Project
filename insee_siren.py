import requests

def test_api():
    token = "74299f23-813d-3dfe-924e-5b10813703b9"  # Remplace par un token valide
    url = "https://api.insee.fr/entreprises/sirene/V3.11/unitesLegales"
    codes_naf = ["6201Z", "6202A", "6202B"]
    naf_query = " OR ".join([f'activitePrincipaleUniteLegale:{code}' for code in codes_naf])
    query = f"({naf_query})"
    params = {
        "q": query,
        "nombre": 5
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers, params=params)
    print("URL finale :", response.url)
    print("Status code :", response.status_code)
    print("Response text :", response.text)

if __name__ == "__main__":
    test_api()
