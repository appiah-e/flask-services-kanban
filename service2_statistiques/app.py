from flask import Flask, request, jsonify
import numpy as np
from scipy import stats

app = Flask(__name__)

def validate_data(data, key='data'):
    """Valide et retourne une liste de nombres."""
    if key not in data:
        raise ValueError(f"Clé '{key}' manquante dans la requête")

    values = data[key]

    if not isinstance(values, list) or len(values) < 2:
        raise ValueError("'data' doit être une liste d'au moins 2 valeurs")

    return np.array(values, dtype=float)


if __name__ == '__main__':
    app.run(debug=True, port=5002)