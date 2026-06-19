from flask import Flask, request, jsonify
import numpy as np
from flask_cors import CORS
from scipy import stats

app = Flask(__name__)
CORS(app)


def validate_data(data, key='data'):
    if not data or key not in data:
        raise ValueError(f"Clé '{key}' manquante")

    values = data[key]

    if not isinstance(values, list) or len(values) < 2:
        raise ValueError("La liste doit contenir au moins 2 valeurs")

    return np.array(values, dtype=float)


# ===================== DESCRIBE =====================
@app.route('/stats/describe', methods=['POST'])
def describe():
    data = request.get_json()

    try:
        values = validate_data(data)

        return jsonify({
            'operation': 'description',
            'resultat': {
                'n': f"{len(values)} → nombre de valeurs",

                'moyenne': f"{round(float(np.mean(values)), 4)} → moyenne des données",

                'mediane': f"{round(float(np.median(values)), 4)} → valeur centrale",

                'ecart_type': f"{round(float(np.std(values, ddof=1)), 4)} → dispersion des données",

                'variance': f"{round(float(np.var(values, ddof=1)), 4)} → variation des données",

                'minimum': f"{round(float(np.min(values)), 4)} → plus petite valeur",

                'maximum': f"{round(float(np.max(values)), 4)} → plus grande valeur",

                'etendue': f"{round(float(np.ptp(values)), 4)} → max - min"
            }
        })

    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# ===================== CORRELATION =====================
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

                'r': f"{round(r, 4)} → force du lien entre X et Y (-1 à 1)",

                'p_value': f"{round(p_value, 6)} → si < 0.05 résultat fiable",

                'interpretation': f"{interpretation} → force de la relation",

                'significatif': f"{bool(p_value < 0.05)} → vrai si pas dû au hasard"
            }
        })

    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# ===================== NORMALITE =====================
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
                'statistique': f"{round(float(stat), 6)} → résultat du test",

                'p_value': f"{round(float(p_value), 6)} → si < 0.05 non normal",

                'est_normale': f"{bool(p_value > 0.05)} → True = données normales"
            }
        })

    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# ===================== STUDENT =====================
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
                't_statistique': f"{round(float(t_stat), 4)} → comparaison des moyennes",

                'p_value': f"{round(float(p_value), 6)} → si < 0.05 différence réelle",

                'difference_significative': f"{bool(p_value < 0.05)} → True si groupes différents"
            }
        })

    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5002)