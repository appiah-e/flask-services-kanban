from flask import Flask, request, jsonify
import numpy as np
from scipy import stats
from db import fetch_series

app = Flask(__name__)

# -------------------------
# ROUTE PRINCIPALE
# -------------------------
# Je crée une route de test pour vérifier que le service fonctionne
@app.route('/')
def home():
    return {
        "service": "Service 3 MySQL",
        "status": "OK"
    }


# -------------------------
# ROUTE DESCRIBE
# -------------------------
# Je récupère une série dans la base de données et je calcule des statistiques descriptives
# (moyenne, médiane, écart-type, min, max)
@app.route('/db/stats/describe', methods=['GET'])
def db_describe():

    # Je récupère le nom de la série envoyé dans l'URL
    nom_serie = request.args.get('serie')

    # Je vérifie si la série est bien fournie
    if not nom_serie:
        return jsonify({
            'erreur': 'Paramètre serie manquant'
        }), 400

    try:
        # Je récupère les données depuis la base de données
        values = np.array(fetch_series(nom_serie))

        # Je calcule les statistiques descriptives
        result = {
            'serie': nom_serie,
            'n': int(len(values)),
            'moyenne': round(float(np.mean(values)), 4),
            'mediane': round(float(np.median(values)), 4),
            'ecart_type': round(float(np.std(values, ddof=1)), 4),
            'minimum': round(float(np.min(values)), 4),
            'maximum': round(float(np.max(values)), 4)
        }

        # Je retourne les résultats sous format JSON
        return jsonify({
            'source': 'mysql',
            'resultat': result
        })

    except ValueError as e:
        # Je gère le cas où la série n'existe pas
        return jsonify({
            'erreur': str(e)
        }), 404

    except Exception as e:
        # Je gère les autres erreurs serveur
        return jsonify({
            'erreur': 'Erreur serveur',
            'detail': str(e)
        }), 500


# -------------------------
# ROUTE CORRELATION
# -------------------------
# Je calcule la corrélation entre deux séries de données
@app.route('/db/stats/correlation', methods=['GET'])
def db_correlation():

    # Je récupère les deux séries depuis l'URL
    serie_x = request.args.get('serie_x')
    serie_y = request.args.get('serie_y')

    # Je vérifie que les deux paramètres sont présents
    if not serie_x or not serie_y:
        return jsonify({
            'erreur': 'serie_x et serie_y requis'
        }), 400

    try:
        # Je récupère les données des deux séries
        x = np.array(fetch_series(serie_x))
        y = np.array(fetch_series(serie_y))

        # Je m'assure qu'elles ont la même taille
        n = min(len(x), len(y))
        x = x[:n]
        y = y[:n]

        # Je calcule la corrélation de Pearson
        r, p_value = stats.pearsonr(x, y)

        # Je retourne le résultat
        return jsonify({
            'source': 'mysql',
            'resultat': {
                'r': round(float(r), 4),
                'p_value': round(float(p_value), 6),
                'significatif': bool(p_value < 0.05)
            }
        })

    except Exception as e:
        # Je gère les erreurs générales
        return jsonify({
            'erreur': str(e)
        }), 500


# -------------------------
# LANCEMENT DU SERVEUR
# -------------------------
# Je démarre l'application Flask sur le port 5003
if __name__ == '__main__':
    app.run(debug=True, port=5003)