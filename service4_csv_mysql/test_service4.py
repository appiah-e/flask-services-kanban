import io
import pytest
from unittest.mock import patch, MagicMock

# ── Imports de l'application (Ajustez le chemin si nécessaire) ────────────────
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "service4_csv_mysql"))

from app import app


# ── Fixture client Flask ─────────────────────────────────────────────────────
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── Helpers / Mocks ──────────────────────────────────────────────────────────
def make_csv_file(content: str, filename: str = "test.csv"):
    """Crée un objet FileStorage simulé à partir d'une chaîne CSV."""
    return (io.BytesIO(content.encode("utf-8")), filename)


def mock_db_cursor(rows=None):
    """Renvoie un mock de connexion/cursor MySQL."""
    cursor = MagicMock()
    cursor.fetchall.return_value = rows or []
    conn = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


# ── Les 5 Tests Essentiels ───────────────────────────────────────────────────

# 1. Test d'absence de fichier (Erreur 400)
def test_pas_de_fichier(client):
    """Vérifie que l'application refuse un envoi vide."""
    res = client.post("/upload/csv", data={})
    assert res.status_code == 400
    assert "file" in res.get_json()["erreur"].lower()


# 2. Test de format invalide (Erreur 400)
def test_mauvaise_extension(client):
    """Vérifie que l'application rejette un fichier qui n'est pas un .csv."""
    data = {"file": (io.BytesIO(b"a,b\n1,2"), "data.txt")}
    res = client.post("/upload/csv", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
    assert ".csv" in res.get_json()["erreur"]


# 3. Test d'insertion réussie (Succès 201)
def test_insertion_reussie(client):
    """Vérifie le bon traitement d'un fichier CSV valide."""
    csv_valide = "nom_serie,valeur\nserie_A,12.5\n"
    conn, cursor = mock_db_cursor()
    with patch("app.get_connection", return_value=conn):
        data = {"file": make_csv_file(csv_valide)}
        res = client.post("/upload/csv", data=data, content_type="multipart/form-data")
    
    assert res.status_code == 201
    assert res.get_json()["statut"] == "success"


# 4. Test de récupération des données (Succès 200)
def test_retour_liste_series(client):
    """Vérifie que la route GET liste correctement les séries de la BD."""
    rows_mock = [("serie_A", 8, "2024-01-15", "2024-01-22")]
    conn, cursor = mock_db_cursor(rows=rows_mock)
    with patch("app.get_connection", return_value=conn):
        res = client.get("/upload/series")
        
    assert res.status_code == 200
    assert res.get_json()["total"] == 1


# 5. Test de la base de données vide (Succès 200)
def test_bd_vide(client):
    """Vérifie le comportement de l'API quand la BD ne contient rien."""
    conn, cursor = mock_db_cursor(rows=[])
    with patch("app.get_connection", return_value=conn):
        res = client.get("/upload/series")
        
    assert res.status_code == 200
    assert res.get_json()["total"] == 0