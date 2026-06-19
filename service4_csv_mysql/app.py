from flask import Flask, request, jsonify, render_template
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
import io

# Je charge les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)

# Je définis les colonnes obligatoires et autorisées dans le CSV
COLONNES_REQUISES = {'nom_serie', 'valeur'}
COLONNES_VALIDES = {'nom_serie', 'valeur', 'categorie', 'date_mesure'}

# Je limite la taille maximale des fichiers CSV à 5 Mo
TAILLE_MAX_OCTETS = 5 * 1024 * 1024


# Je crée la connexion à la base de données MySQL
def get_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT'))
    )


# Je crée une route pour afficher une page HTML
@app.route('/index')
def Affiche_html():
    return render_template('index.html')


# Je crée une route pour uploader un fichier CSV et l'insérer en base
@app.route('/upload/csv', methods=['POST'])
def upload_csv():

    # Je vérifie si un fichier a bien été envoyé
    if 'file' not in request.files:
        return jsonify({'erreur': 'Aucun fichier envoyé (clé "file" manquante)'}), 400

    file = request.files['file']

    # Je vérifie que le fichier n'est pas vide
    if file.filename == '':
        return jsonify({'erreur': 'Nom de fichier vide'}), 400

    # Je vérifie que le fichier est bien un CSV
    if not file.filename.endswith('.csv'):
        return jsonify({'erreur': 'Seuls les fichiers .csv sont acceptés'}), 400

    try:
        # Je lis le contenu du fichier
        content = file.read()

        # Je vérifie la taille du fichier
        if len(content) > TAILLE_MAX_OCTETS:
            return jsonify({'erreur': 'Fichier trop volumineux (max 5 Mo)'}), 413

        # Je transforme le CSV en DataFrame pandas
        df = pd.read_csv(io.BytesIO(content))

    except Exception as e:
        return jsonify({'erreur': f'Lecture CSV impossible : {e}'}), 400

    # Je vérifie que les colonnes obligatoires sont présentes
    colonnes_manquantes = COLONNES_REQUISES - set(df.columns)
    if colonnes_manquantes:
        return jsonify({
            'erreur': 'Colonnes obligatoires manquantes',
            'manquantes': list(colonnes_manquantes)
        }), 400

    # Je garde uniquement les colonnes valides
    df = df[[c for c in df.columns if c in COLONNES_VALIDES]]

    # Je convertis la colonne valeur en numérique
    df['valeur'] = pd.to_numeric(df['valeur'], errors='coerce')

    # Je compte les lignes invalides
    lignes_invalides = df['valeur'].isna().sum()

    # Je supprime les lignes invalides
    df.dropna(subset=['valeur'], inplace=True)

    # Je vérifie qu'il reste des données valides
    if df.empty:
        return jsonify({'erreur': 'Aucune ligne valide dans le CSV'}), 400

    # Je me connecte à la base de données et j'insère les données
    try:
        conn = get_connection()
        cursor = conn.cursor()
        insertions = 0

        # Je parcours chaque ligne du CSV
        for _, row in df.iterrows():
            cursor.execute(
                '''
                INSERT INTO donnees (nom_serie, valeur, categorie, date_mesure)
                VALUES (%s, %s, %s, %s)
                ''',
                (
                    str(row['nom_serie']),
                    float(row['valeur']),
                    str(row['categorie']) if 'categorie' in df.columns else None,
                    str(row['date_mesure']) if 'date_mesure' in df.columns else None
                )
            )
            insertions += 1

        # Je valide les insertions
        conn.commit()

        # Je ferme la connexion
        cursor.close()
        conn.close()

    except Exception as e:
        return jsonify({
            'erreur': 'Erreur base de données',
            'detail': str(e)
        }), 500

    # Je retourne le résultat de l'import
    return jsonify({
        'statut': 'success',
        'lignes_inserees': insertions,
        'lignes_invalides_ignorees': int(lignes_invalides),
        'message': f'{insertions} ligne(s) chargée(s) dans la table donnees'
    }), 201


# Je crée une route pour afficher toutes les séries en base
@app.route('/upload/series', methods=['GET'])
def list_series():
    """Je retourne la liste des séries et leurs statistiques"""

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Je récupère les séries et leurs statistiques
        cursor.execute(
            '''
            SELECT nom_serie,
                   COUNT(*) AS n,
                   MIN(date_mesure),
                   MAX(date_mesure)
            FROM donnees
            GROUP BY nom_serie
            ORDER BY nom_serie
            '''
        )

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        # Je transforme les résultats en JSON lisible
        series = [
            {
                'serie': r[0],
                'n_points': r[1],
                'debut': str(r[2]),
                'fin': str(r[3])
            }
            for r in rows
        ]

        # Je retourne toutes les séries
        return jsonify({'series': series, 'total': len(series)})

    except Exception as e:
        return jsonify({
            'erreur': 'Erreur base de données',
            'detail': str(e)
        }), 500


# Je démarre l'application Flask sur le port 5004
if __name__ == '__main__':
    app.run(debug=True, port=5004)