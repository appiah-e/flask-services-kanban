import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():

    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

def fetch_series(nom_serie):

    conn = get_connection()

    cursor = conn.cursor()

    query = """
    SELECT valeur
    FROM donnees
    WHERE nom_serie = %s
    ORDER BY date_mesure
    """

    cursor.execute(query, (nom_serie,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    if not rows:
        raise ValueError(f"Série '{nom_serie}' introuvable")

    return [float(row[0]) for row in rows]