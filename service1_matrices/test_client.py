import requests

# L'URL de base de votre service (l'adresse où écoute l'API Flask)
BASE_URL = 'http://localhost:5001/matrices'


def tester_addition():
    print("--- 1. Test POST /matrices/add ---")
    url = f"{BASE_URL}/add"
    # Envoi de deux matrices 2x2 valides
    donnees = {"A": [[1, 2], [3, 4]], "B": [[5, 6], [7, 8]]}
    try:
        # Exécution de la requête HTTP POST avec les données sérialisées en JSON
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code}")  # Attendu : 200 (Succès)
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


def tester_addition_erreur():
    print("--- 1b. Test Erreur Addition (Dimensions incompatibles) ---")
    url = f"{BASE_URL}/add"
    # A est 2x2, B est 2x3 : les dimensions ne correspondent pas pour une addition case par case
    donnees = {"A": [[1, 2], [3, 4]], "B": [[1, 2, 3], [4, 5, 6]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code} (Attendu : 400)")  # Attendu : 400 (Erreur client)
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


def tester_multiplication():
    print("--- 2. Test POST /matrices/multiply ---")
    url = f"{BASE_URL}/multiply"
    donnees = {"A": [[1, 2], [3, 4]], "B": [[5, 6], [7, 8]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code}")  # Attendu : 200 (Succès)
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


def tester_multiplication_erreur():
    print("--- 2b. Test Erreur Multiplication (Colonnes A != Lignes B) ---")
    url = f"{BASE_URL}/multiply"
    # A a 3 colonnes, B a 2 lignes : la règle mathématique de multiplication n'est pas respectée
    donnees = {"A": [[1, 2, 3], [4, 5, 6]], "B": [[1, 2], [3, 4]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code} (Attendu : 400)")  # Attendu : 400
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


def tester_transpose():
    print("--- 3. Test POST /matrices/transpose ---")
    url = f"{BASE_URL}/transpose"
    donnees = {"A": [[1, 2, 3], [4, 5, 6]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code}")  # Attendu : 200 (Succès)
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


def tester_transpose_erreur():
    print("--- 3b. Test Erreur Transposee (Format invalide) ---")
    url = f"{BASE_URL}/transpose"
    # Envoi d'une chaîne de caractères au lieu d'une structure matricielle (liste de listes)
    donnees = {"A": "Ceci n'est pas une matrice"}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code} (Attendu : 400)")  # Attendu : 400 (Échec de la conversion NumPy)
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


def tester_determinant():
    print("--- 4. Test POST /matrices/determinant ---")
    url = f"{BASE_URL}/determinant"
    donnees = {"A": [[1, 2], [3, 4]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code}")  # Attendu : 200 (Succès)
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


def tester_determinant_erreur():
    print("--- 4b. Test Erreur Determinant (Matrice non carrée) ---")
    url = f"{BASE_URL}/determinant"
    # Matrice rectangulaire (2 lignes x 3 colonnes) : le déterminant n'existe pas
    donnees = {"A": [[1, 2, 3], [4, 5, 6]]}

    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code} (Attendu : 400)")  # Attendu : 400
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


def tester_inverse():
    print("--- 5. Test POST /matrices/inverse ---")
    url = f"{BASE_URL}/inverse"
    donnees = {"A": [[1, 2], [3, 4]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code}")  # Attendu : 200 (Succès)
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


def tester_inverse_erreur():
    print("--- 5b. Test Erreur Inverse (Matrice singulière) ---")
    url = f"{BASE_URL}/inverse"
    # Matrice singulière (lignes proportionnelles, déterminant = 0), non inversible
    donnees = {"A": [[1, 2], [2, 4]]}
    try:
        reponse = requests.post(url, json=donnees)
        print(f"Statut HTTP : {reponse.status_code} (Attendu : 400)")  # Attendu : 400
        print(f"Résultat : {reponse.json()}\n")
    except Exception as e:
        print(f"Erreur de connexion : {e}\n")


# Point d'entrée du script : exécute les fonctions de test une par une
if __name__ == '__main__':
    print("DÉBUT DES TESTS CLIENTS Python\n")
    # Tests des cas nominaux (succès attendus, code 200)
    tester_addition()
    tester_multiplication()
    tester_transpose()
    tester_determinant()
    tester_inverse()
    # Tests des cas limites et erreurs (protection et code 400 attendus)
    tester_addition_erreur()
    tester_multiplication_erreur()
    tester_transpose_erreur()
    tester_determinant_erreur()
    tester_inverse_erreur()