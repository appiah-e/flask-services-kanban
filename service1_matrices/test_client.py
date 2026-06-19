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

def tester_addition_erreur():
    print("--- 1b. Test Erreur Addition (Dimensions incompatibles) ---")
    url = f"{BASE_URL}/add"
    # A est 2x2, B est 2x3
    donnees = {"A": [[1, 2], [3, 4]], "B": [[1, 2, 3], [4, 5, 6]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code} (Attendu : 400)")
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")

def tester_multiplication():
    print("--- 2. Test POST /matrices/multiply ---")
    url = f"{BASE_URL}/multiply"
    donnees = {"A": [[1, 2], [3, 4]], "B": [[5, 6], [7, 8]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code}")
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")

def tester_multiplication_erreur():
    print("--- 2b. Test Erreur Multiplication (Colonnes A != Lignes B) ---")
    url = f"{BASE_URL}/multiply"
    # A a 3 colonnes, B a 2 lignes
    donnees = {"A": [[1, 2, 3], [4, 5, 6]], "B": [[1, 2], [3, 4]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code} (Attendu : 400)")
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")

def tester_transpose():
    print("--- 3. Test POST /matrices/transpose ---")
    url = f"{BASE_URL}/transpose"
    donnees = {"A": [[1, 2, 3], [4, 5, 6]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code}")
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")

def tester_transpose_erreur():
    print("--- 3b. Test Erreur Transposee (Format invalide) ---")
    url = f"{BASE_URL}/transpose"
    donnees = {"A": "Ceci n'est pas une matrice"}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code} (Attendu : 400)")
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")

def tester_determinant():
    print("--- 4. Test POST /matrices/determinant ---")
    url = f"{BASE_URL}/determinant"
    donnees = {"A": [[1, 2], [3, 4]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code}")
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")

def tester_determinant_erreur():
    print("--- 4b. Test Erreur Determinant (Matrice non carrée) ---")
    url = f"{BASE_URL}/determinant"
    # On envoie une matrice 2 lignes x 3 colonnes
    donnees = {"A": [[1, 2, 3], [4, 5, 6]]}

    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code} (Attendu : 400)")
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")

def tester_inverse():
    print("--- 5. Test POST /matrices/inverse ---")
    url = f"{BASE_URL}/inverse"
    donnees = {"A": [[1, 2], [3, 4]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code}")
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")

def tester_inverse_erreur():
    print("--- 5b. Test Erreur Inverse (Matrice singulière) ---")
    url = f"{BASE_URL}/inverse"
    donnees = {"A": [[1, 2], [2, 4]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code} (Attendu : 400)")
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")

if __name__ == '__main__':
    print("DÉBUT DES TESTS CLIENTS Python\n")
    tester_addition()
    tester_multiplication()
    tester_transpose()
    tester_determinant()
    tester_inverse()
    tester_addition_erreur()
    tester_multiplication_erreur()
    tester_transpose_erreur()
    tester_determinant_erreur()
    tester_inverse_erreur()