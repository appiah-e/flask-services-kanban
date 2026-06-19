from flask import Flask, request, jsonify # Importation des modules nécessaires de Flask pour créer l'API, lire les requêtes et formater les réponses en JSON
from flask_cors import CORS # Importation de CORS pour autoriser les requêtes venant d'autres origines (notamment votre page web HTML)
import numpy as np # Importation de NumPy pour effectuer les calculs et opérations matricielles de manière optimisée

app = Flask(__name__) # Initialisation de l'application Flask
CORS(app) # Activation de CORS sur toutes les routes de l'application pour éviter les blocages du navigateur


def parse_matrix(data, key):
    """Convertit une liste de listes en tableau NumPy."""
    try:
        # Tente d'extraire la clé (ex: 'A' ou 'B') du dictionnaire JSON et de la convertir en tableau de nombres décimaux (float)
        return np.array(data[key], dtype=float)
    except (KeyError, ValueError) as e:
        # Lève une exception si la clé est absente ou si le format des données est incorrect
        raise ValueError(f"Matrice '{key}' invalide : {e}")


# Route pour l'addition de deux matrices (Méthode POST)
@app.route('/matrices/add', methods=['POST'])
def add_matrices():
    # Récupération des données brutes envoyées au format JSON dans la requête
    data = request.get_json()
    try:
        # Analyse et conversion des matrices A et B
        A = parse_matrix(data, 'A')
        B = parse_matrix(data, 'B')

        # Vérification mathématique : l'addition matricielle nécessite des matrices de mêmes dimensions (shape)
        if A.shape != B.shape:
            return jsonify({'erreur': 'Dimensions incompatibles'}), 400

        # Calcul de l'addition et conversion du tableau NumPy de retour en liste Python native pour le JSON
        result = (A + B).tolist()
        return jsonify({
            'operation': 'addition',
            'resultat': result
        })
    # Gestion centralisée des erreurs de parsing ou d'incompatibilité de type
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# Route pour la multiplication de deux matrices (Méthode POST)
@app.route('/matrices/multiply', methods=['POST'])
def multiply_matrices():
    data = request.get_json()
    try:
        A = parse_matrix(data, 'A')
        B = parse_matrix(data, 'B')

        # Vérification mathématique : le nombre de colonnes de A doit correspondre au nombre de lignes de B
        if A.shape[1] != B.shape[0]:
            return jsonify({'erreur': 'Colonnes(A) doit egalerLignes(B)'}), 400

        # Produit matriciel via np.dot, puis conversion en liste native
        result = np.dot(A, B).tolist()
        return jsonify({'operation': 'multiplication', 'resultat': result})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# Route pour la transposition de matrice (Méthode POST)
@app.route('/matrices/transpose', methods=['POST'])
def transpose_matrix():
    data = request.get_json()
    try:
        A = parse_matrix(data, 'A')
        # Utilisation de l'attribut .T de NumPy pour transposer la matrice (lignes <=> colonnes)
        result = A.T.tolist()
        return jsonify({'operation': 'transposee', 'resultat': result})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# Route pour le calcul du déterminant d'une matrice (Méthode POST)
@app.route('/matrices/determinant', methods=['POST'])
def determinant_matrix():
    data = request.get_json()
    try:
        A = parse_matrix(data, 'A')
        # Vérification : le déterminant n'est calculable que sur une matrice carrée (lignes == colonnes)
        if A.shape[0] != A.shape[1]:
            return jsonify({'erreur': 'La matrice doit etre carree'}), 400

        # Calcul du déterminant via l'algèbre linéaire de NumPy, arrondi pour éviter les erreurs de précision flottante
        det = np.linalg.det(A)
        return jsonify({'operation': 'determinant', 'resultat': round(det, 6)})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# Route pour le calcul de l'inverse d'une matrice (Méthode POST)
@app.route('/matrices/inverse', methods=['POST'])
def inverse_matrix():
    data = request.get_json()
    try:
        A = parse_matrix(data, 'A')
        # Vérification de la forme carrée
        if A.shape[0] != A.shape[1]:
            return jsonify({'erreur': 'La matrice doit etre carree'}), 400

        # Détermination de l'inversibilité via la valeur absolue du déterminant
        det = np.linalg.det(A)
        # Si le déterminant est très proche de 0, la matrice est dite "singulière" et n'a pas d'inverse
        if abs(det) < 1e-10:
            return jsonify({'erreur': 'Matrice singuliere, non inversible'}), 400

        # Inversion de la matrice et conversion en liste
        result = np.linalg.inv(A).tolist()
        return jsonify({'operation': 'inverse', 'resultat': result})
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# Point d'entrée pour démarrer l'application Flask en mode debug sur le port 5001
if __name__ == '__main__':
    app.run(debug=True, port=5001)