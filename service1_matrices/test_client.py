import requests

# L'URL de base de votre service
BASE_URL = 'http://localhost:5001/matrices'


def tester_addition():
    print("--- 1. Test POST /matrices/add ---")
    url = f"{BASE_URL}/add"
    donnees = {"A": [[1, 2], [3, 4]], "B": [[5, 6], [7, 8]]}

    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code}")
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


if __name__ == '__main__':
    print("DÉBUT DES TESTS CLIENTS Python\n")
    tester_addition()