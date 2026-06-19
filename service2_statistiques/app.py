from flask import Flask, request, jsonify
import numpy as np
from flask_cors import CORS
from scipy import stats

# Création de l'application Flask
app = Flask(__name__)

# Activation CORS (autorise le HTML à appeler l'API)
CORS(app)


def validate_data(data, key='data'):
    """Valide et transforme les données en tableau numpy"""

    if not data or key not in data:
        raise ValueError(f"Clé '{key}' manquante")

    values = data[key]

    if not isinstance(values, list) or len(values) < 2:
        raise ValueError("La liste doit contenir au moins 2 valeurs")

    return np.array(values, dtype=float)

# =========================== Route /stat/describe ===========================

@app.route('/stats/describe', methods=['GET', 'POST'])
def describe():

    # Récupération JSON envoyé par le client
    data = request.get_json()

    try:
        values = validate_data(data)

        # Calcul des statistiques
        result = {
            'n': int(len(values)),
            'moyenne': round(float(np.mean(values)), 4),
            'mediane': round(float(np.median(values)), 4),
            'ecart_type': round(float(np.std(values, ddof=1)), 4),
            'variance': round(float(np.var(values, ddof=1)), 4),
            'minimum': round(float(np.min(values)), 4),
            'maximum': round(float(np.max(values)), 4),
            'q1': round(float(np.percentile(values, 25)), 4),
            'q3': round(float(np.percentile(values, 75)), 4),
            'etendue': round(float(np.ptp(values)), 4),
        }

        return jsonify({
            'operation': 'description',
            'resultat': result
        })

    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400

# =========================== Route /stat/correlation ===========================

@app.route('/stats/correlation', methods=['POST'])
def correlation():
    data = request.get_json()

    try:
        x = validate_data(data, 'x')
        y = validate_data(data, 'y')

        if len(x) != len(y):
            return jsonify({'erreur': 'x et y doivent avoir la même longueur'}), 400

        r, p_value = stats.pearsonr(x, y)

        interpretation = (
            'forte' if abs(r) > 0.7
            else 'modérée' if abs(r) > 0.4
            else 'faible'
        )

        return jsonify({
            'operation': 'correlation_pearson',
            'resultat': {
                'r': round(r, 4),
                'p_value': round(p_value, 6),
                'interpretation': interpretation,
                'significatif': bool(p_value < 0.05)
            }
        })

    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400

# =========================== Route /stat/test_normalite ===========================

@app.route('/stats/test_normalite', methods=['POST'])
def test_normalite():
    data = request.get_json()

    try:
        values = validate_data(data)

        if len(values) > 5000:
            return jsonify({'erreur': 'Shapiro-Wilk limité à 5000 valeurs'}), 400

        stat, p_value = stats.shapiro(values)

        return jsonify({
            'operation': 'test_normalite_shapiro_wilk',
            'resultat': {
                'statistique': round(float(stat), 6),
                'p_value': round(float(p_value), 6),
                'est_normale': bool(p_value > 0.05),
                'interpretation': (
                    'Distribution normale (p > 0.05)'
                    if p_value > 0.05
                    else 'Distribution non normale (p <= 0.05)'
                )
            }
        })

    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400

# =========================== Route /stat/test_normalite ===========================

@app.route('/stats/test_student', methods=['POST'])
def test_student():
    data = request.get_json()

    try:
        groupe1 = validate_data(data, 'groupe1')
        groupe2 = validate_data(data, 'groupe2')

        t_stat, p_value = stats.ttest_ind(groupe1, groupe2)

        return jsonify({
            'operation': 'test_t_student',
            'resultat': {
                't_statistique': round(float(t_stat), 4),
                'p_value': round(float(p_value), 6),
                'difference_significative': bool(p_value < 0.05)
            }
        })

    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400

# Lancement du serveur
if __name__ == '__main__':
    app.run(debug=True, port=5002)