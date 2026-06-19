"""
Tests unitaires et d'intégration pour service4_csv_mysql (app.py)
Utilise pytest + unittest.mock pour éviter toute dépendance MySQL réelle.
"""

import io
import pytest
from unittest.mock import patch, MagicMock

# Je modifie le chemin pour pouvoir importer l'application Flask
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "service4_csv_mysql"))

from app import app, TAILLE_MAX_OCTETS


# Je crée un client Flask pour simuler les requêtes HTTP
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# Je crée un fichier CSV simulé à partir d'une chaîne de texte
def make_csv_file(content: str, filename: str = "test.csv"):
    """Je transforme une chaîne CSV en fichier simulé."""
    return (io.BytesIO(content.encode("utf-8")), filename)


# Je crée un mock de base de données MySQL (connexion + curseur)
def mock_db_cursor(rows=None):
    """Je simule une connexion MySQL sans vraie base."""
    cursor = MagicMock()
    cursor.fetchall.return_value = rows or []
    conn = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


# ════════════════════════════════════════════════════════════════════════════
# 1. POST /upload/csv
# ════════════════════════════════════════════════════════════════════════════

class TestUploadCsvValidation:
    """Je teste les validations du fichier CSV."""

    def test_pas_de_fichier(self, client):
        """Je vérifie que l'API renvoie une erreur si aucun fichier n'est envoyé."""
        res = client.post("/upload/csv", data={})
        assert res.status_code == 400
        assert "manquante" in res.get_json()["erreur"].lower() or \
               "file" in res.get_json()["erreur"].lower()

    def test_nom_de_fichier_vide(self, client):
        """Je vérifie que le nom de fichier vide est refusé."""
        data = {"file": (io.BytesIO(b"a,b\n1,2"), "")}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 400
        assert "vide" in res.get_json()["erreur"].lower()

    def test_mauvaise_extension(self, client):
        """Je vérifie que seuls les fichiers CSV sont acceptés."""
        data = {"file": (io.BytesIO(b"a,b\n1,2"), "data.txt")}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 400
        assert ".csv" in res.get_json()["erreur"]

    def test_fichier_trop_volumineux(self, client):
        """Je vérifie qu'un fichier trop volumineux est refusé."""
        big_content = b"nom_serie,valeur\n" + b"A,1.0\n" * 1_000_000
        assert len(big_content) > TAILLE_MAX_OCTETS
        data = {"file": (io.BytesIO(big_content), "gros.csv")}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 413

    def test_colonnes_obligatoires_manquantes(self, client):
        """Je vérifie que les colonnes obligatoires sont détectées."""
        csv = "categorie,date_mesure\ntemp,2024-01-01\n"
        data = {"file": make_csv_file(csv)}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 400
        body = res.get_json()
        assert "manquantes" in body
        assert set(body["manquantes"]).issubset({"nom_serie", "valeur"})

    def test_valeur_non_numerique_ignoree(self, client):
        """Je vérifie que les valeurs non numériques sont ignorées."""
        csv = "nom_serie,valeur\nserie_A,12.5\nserie_B,ABC\n"
        conn, cursor = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(csv)}
            res = client.post("/upload/csv", data=data,
                              content_type="multipart/form-data")
        assert res.status_code == 201
        body = res.get_json()
        assert body["lignes_inserees"] == 1
        assert body["lignes_invalides_ignorees"] == 1

    def test_toutes_valeurs_invalides(self, client):
        """Je vérifie le cas où toutes les valeurs sont invalides."""
        csv = "nom_serie,valeur\nserie_A,NaN_texte\nserie_B,???\n"
        data = {"file": make_csv_file(csv)}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 400
        assert "valide" in res.get_json()["erreur"].lower()

    def test_csv_illisible(self, client):
        """Je vérifie qu'un CSV corrompu est refusé."""
        data = {"file": (io.BytesIO(b"\x00\xff\xfe"), "corrupt.csv")}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 400


# ════════════════════════════════════════════════════════════════════════════
# 2. POST /upload/csv - INSERTION
# ════════════════════════════════════════════════════════════════════════════

class TestUploadCsvInsertion:
    """Je teste l'insertion en base de données (mockée)."""

    CSV_VALIDE = (
        "nom_serie,valeur,categorie,date_mesure\n"
        "serie_A,12.50,temperature,2024-01-15\n"
        "serie_A,15.30,temperature,2024-01-16\n"
        "serie_B,45.10,pression,2024-01-15\n"
    )

    def test_insertion_reussie(self, client):
        """Je vérifie qu'un CSV valide est inséré correctement."""
        conn, cursor = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(self.CSV_VALIDE)}
            res = client.post("/upload/csv", data=data,
                              content_type="multipart/form-data")
        assert res.status_code == 201
        body = res.get_json()
        assert body["statut"] == "success"

    def test_colonnes_optionnelles_absentes(self, client):
        """Je vérifie que les colonnes optionnelles peuvent être absentes."""
        csv = "nom_serie,valeur\nserie_X,99.9\n"
        conn, cursor = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(csv)}
            res = client.post("/upload/csv", data=data,
                              content_type="multipart/form-data")
        assert res.status_code == 201

    def test_colonnes_inconnues_ignorees(self, client):
        """Je vérifie que les colonnes inconnues sont ignorées."""
        csv = "nom_serie,valeur,colonne_inconnue\nserie_Z,7.0,JUNK\n"
        conn, cursor = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(csv)}
            res = client.post("/upload/csv", data=data,
                              content_type="multipart/form-data")
        assert res.status_code == 201

    def test_erreur_base_de_donnees(self, client):
        """Je vérifie la gestion des erreurs MySQL."""
        with patch("app.get_connection", side_effect=Exception("Connexion refusée")):
            data = {"file": make_csv_file(self.CSV_VALIDE)}
            res = client.post("/upload/csv", data=data,
                              content_type="multipart/form-data")
        assert res.status_code == 500

    def test_commit_appele(self, client):
        """Je vérifie que commit est bien appelé."""
        conn, _ = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(self.CSV_VALIDE)}
            client.post("/upload/csv", data=data,
                        content_type="multipart/form-data")
        conn.commit.assert_called_once()

    def test_connexion_fermee_apres_insertion(self, client):
        """Je vérifie que la connexion est fermée après insertion."""
        conn, cursor = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(self.CSV_VALIDE)}
            client.post("/upload/csv", data=data,
                        content_type="multipart/form-data")
        conn.close.assert_called_once()
        cursor.close.assert_called_once()


# ════════════════════════════════════════════════════════════════════════════
# 3. GET /upload/series
# ════════════════════════════════════════════════════════════════════════════

class TestListSeries:
    """Je teste la récupération des séries."""

    ROWS_BD = [
        ("serie_A", 8, "2024-01-15", "2024-01-22"),
        ("serie_B", 8, "2024-01-15", "2024-01-22"),
        ("serie_C", 6, "2024-01-15", "2024-01-20"),
    ]

    def test_retour_liste_series(self, client):
        """Je vérifie que la liste est retournée correctement."""
        conn, cursor = mock_db_cursor(rows=self.ROWS_BD)
        with patch("app.get_connection", return_value=conn):
            res = client.get("/upload/series")
        assert res.status_code == 200

    def test_structure_serie(self, client):
        """Je vérifie la structure des données."""
        conn, cursor = mock_db_cursor(rows=self.ROWS_BD)
        with patch("app.get_connection", return_value=conn):
            res = client.get("/upload/series")
        serie = res.get_json()["series"][0]
        assert "serie" in serie

    def test_bd_vide(self, client):
        """Je vérifie le comportement si la BD est vide."""
        conn, cursor = mock_db_cursor(rows=[])
        with patch("app.get_connection", return_value=conn):
            res = client.get("/upload/series")
        assert res.status_code == 200

    def test_erreur_bd_series(self, client):
        """Je vérifie la gestion des erreurs BD."""
        with patch("app.get_connection", side_effect=Exception("Timeout")):
            res = client.get("/upload/series")
        assert res.status_code == 500

    def test_connexion_fermee_apres_get(self, client):
        """Je vérifie que la connexion est fermée après lecture."""
        conn, cursor = mock_db_cursor(rows=self.ROWS_BD)
        with patch("app.get_connection", return_value=conn):
            client.get("/upload/series")
        conn.close.assert_called_once()
        cursor.close.assert_called_once()


# ════════════════════════════════════════════════════════════════════════════
# 4. TEST D'INTÉGRATION
# ════════════════════════════════════════════════════════════════════════════

class TestFluxComplet:
    """Je teste un flux complet upload → lecture."""

    def test_upload_puis_list(self, client):
        """Je vérifie le flux complet."""
        csv = (
            "nom_serie,valeur,categorie,date_mesure\n"
            "serie_X,1.0,cat,2024-03-01\n"
            "serie_X,2.0,cat,2024-03-02\n"
            "serie_X,3.0,cat,2024-03-03\n"
        )

        conn_up, _ = mock_db_cursor()
        with patch("app.get_connection", return_value=conn_up):
            res_up = client.post(
                "/upload/csv",
                data={"file": make_csv_file(csv)},
                content_type="multipart/form-data",
            )
        assert res_up.status_code == 201

        rows = [("serie_X", 3, "2024-03-01", "2024-03-03")]
        conn_get, _ = mock_db_cursor(rows=rows)
        with patch("app.get_connection", return_value=conn_get):
            res_get = client.get("/upload/series")
        assert res_get.status_code == 200