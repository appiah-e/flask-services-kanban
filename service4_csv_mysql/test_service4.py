"""
Tests unitaires et d'intégration pour service4_csv_mysql (app.py)
Utilise pytest + unittest.mock pour éviter toute dépendance MySQL réelle.
"""

import io
import pytest
from unittest.mock import patch, MagicMock

# ── Import de l'application ──────────────────────────────────────────────────
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "service4_csv_mysql"))

from app import app, TAILLE_MAX_OCTETS


# ── Fixture client Flask ─────────────────────────────────────────────────────
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── Helpers ──────────────────────────────────────────────────────────────────
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


# ════════════════════════════════════════════════════════════════════════════
# 1. POST /upload/csv
# ════════════════════════════════════════════════════════════════════════════

class TestUploadCsvValidation:
    """Tests de validation de l'entrée (sans BD)."""

    def test_pas_de_fichier(self, client):
        """400 si la clé 'file' est absente."""
        res = client.post("/upload/csv", data={})
        assert res.status_code == 400
        assert "manquante" in res.get_json()["erreur"].lower() or \
               "file" in res.get_json()["erreur"].lower()

    def test_nom_de_fichier_vide(self, client):
        """400 si le nom de fichier est vide."""
        data = {"file": (io.BytesIO(b"a,b\n1,2"), "")}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 400
        assert "vide" in res.get_json()["erreur"].lower()

    def test_mauvaise_extension(self, client):
        """400 si le fichier n'est pas un .csv."""
        data = {"file": (io.BytesIO(b"a,b\n1,2"), "data.txt")}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 400
        assert ".csv" in res.get_json()["erreur"]

    def test_fichier_trop_volumineux(self, client):
        """413 si le fichier dépasse 5 Mo."""
        big_content = b"nom_serie,valeur\n" + b"A,1.0\n" * 1_000_000
        assert len(big_content) > TAILLE_MAX_OCTETS
        data = {"file": (io.BytesIO(big_content), "gros.csv")}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 413

    def test_colonnes_obligatoires_manquantes(self, client):
        """400 si 'nom_serie' ou 'valeur' sont absentes."""
        csv = "categorie,date_mesure\ntemp,2024-01-01\n"
        data = {"file": make_csv_file(csv)}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 400
        body = res.get_json()
        assert "manquantes" in body
        assert set(body["manquantes"]).issubset({"nom_serie", "valeur"})

    def test_valeur_non_numerique_ignoree(self, client):
        """Les lignes avec valeur non numérique sont ignorées, les valides insérées."""
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
        """400 si toutes les lignes ont une valeur non numérique."""
        csv = "nom_serie,valeur\nserie_A,NaN_texte\nserie_B,???\n"
        data = {"file": make_csv_file(csv)}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 400
        assert "valide" in res.get_json()["erreur"].lower()

    def test_csv_illisible(self, client):
        """400 si le fichier n'est pas parsable en CSV."""
        data = {"file": (io.BytesIO(b"\x00\xff\xfe"), "corrupt.csv")}
        res = client.post("/upload/csv", data=data,
                          content_type="multipart/form-data")
        assert res.status_code == 400


class TestUploadCsvInsertion:
    """Tests d'insertion dans la BD (BD mockée)."""

    CSV_VALIDE = (
        "nom_serie,valeur,categorie,date_mesure\n"
        "serie_A,12.50,temperature,2024-01-15\n"
        "serie_A,15.30,temperature,2024-01-16\n"
        "serie_B,45.10,pression,2024-01-15\n"
    )

    def test_insertion_reussie(self, client):
        """201 + bonne réponse JSON après insertion correcte."""
        conn, cursor = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(self.CSV_VALIDE)}
            res = client.post("/upload/csv", data=data,
                              content_type="multipart/form-data")
        assert res.status_code == 201
        body = res.get_json()
        assert body["statut"] == "success"
        assert body["lignes_inserees"] == 3
        assert body["lignes_invalides_ignorees"] == 0
        assert "3" in body["message"]

    def test_colonnes_optionnelles_absentes(self, client):
        """Insertion correcte même sans 'categorie' ni 'date_mesure'."""
        csv = "nom_serie,valeur\nserie_X,99.9\n"
        conn, cursor = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(csv)}
            res = client.post("/upload/csv", data=data,
                              content_type="multipart/form-data")
        assert res.status_code == 201
        # Vérifie que cursor.execute a bien été appelé avec None pour les colonnes absentes
        args = cursor.execute.call_args[0][1]
        assert args[2] is None  # categorie
        assert args[3] is None  # date_mesure

    def test_colonnes_inconnues_ignorees(self, client):
        """Les colonnes hors COLONNES_VALIDES sont silencieusement écartées."""
        csv = "nom_serie,valeur,colonne_inconnue\nserie_Z,7.0,JUNK\n"
        conn, cursor = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(csv)}
            res = client.post("/upload/csv", data=data,
                              content_type="multipart/form-data")
        assert res.status_code == 201

    def test_erreur_base_de_donnees(self, client):
        """500 si la connexion MySQL échoue."""
        with patch("app.get_connection", side_effect=Exception("Connexion refusée")):
            data = {"file": make_csv_file(self.CSV_VALIDE)}
            res = client.post("/upload/csv", data=data,
                              content_type="multipart/form-data")
        assert res.status_code == 500
        body = res.get_json()
        assert "erreur" in body
        assert "Connexion refusée" in body["detail"]

    def test_commit_appele(self, client):
        """Vérifie que conn.commit() est bien appelé après insertion."""
        conn, _ = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(self.CSV_VALIDE)}
            client.post("/upload/csv", data=data,
                        content_type="multipart/form-data")
        conn.commit.assert_called_once()

    def test_connexion_fermee_apres_insertion(self, client):
        """Vérifie que conn.close() est appelé même après succès."""
        conn, cursor = mock_db_cursor()
        with patch("app.get_connection", return_value=conn):
            data = {"file": make_csv_file(self.CSV_VALIDE)}
            client.post("/upload/csv", data=data,
                        content_type="multipart/form-data")
        conn.close.assert_called_once()
        cursor.close.assert_called_once()


# ════════════════════════════════════════════════════════════════════════════
# 2. GET /upload/series
# ════════════════════════════════════════════════════════════════════════════

class TestListSeries:
    """Tests de la route GET /upload/series."""

    ROWS_BD = [
        ("serie_A", 8, "2024-01-15", "2024-01-22"),
        ("serie_B", 8, "2024-01-15", "2024-01-22"),
        ("serie_C", 6, "2024-01-15", "2024-01-20"),
    ]

    def test_retour_liste_series(self, client):
        """200 + liste correcte quand la BD contient des données."""
        conn, cursor = mock_db_cursor(rows=self.ROWS_BD)
        with patch("app.get_connection", return_value=conn):
            res = client.get("/upload/series")
        assert res.status_code == 200
        body = res.get_json()
        assert body["total"] == 3
        assert len(body["series"]) == 3

    def test_structure_serie(self, client):
        """Chaque élément de la liste contient les bons champs."""
        conn, cursor = mock_db_cursor(rows=self.ROWS_BD)
        with patch("app.get_connection", return_value=conn):
            res = client.get("/upload/series")
        serie = res.get_json()["series"][0]
        assert "serie" in serie
        assert "n_points" in serie
        assert "debut" in serie
        assert "fin" in serie

    def test_bd_vide(self, client):
        """200 + liste vide si la table ne contient rien."""
        conn, cursor = mock_db_cursor(rows=[])
        with patch("app.get_connection", return_value=conn):
            res = client.get("/upload/series")
        assert res.status_code == 200
        body = res.get_json()
        assert body["total"] == 0
        assert body["series"] == []

    def test_erreur_bd_series(self, client):
        """500 si la BD est inaccessible lors du GET."""
        with patch("app.get_connection", side_effect=Exception("Timeout")):
            res = client.get("/upload/series")
        assert res.status_code == 500
        body = res.get_json()
        assert "erreur" in body
        assert "Timeout" in body["detail"]

    def test_connexion_fermee_apres_get(self, client):
        """conn.close() appelé après le GET /series."""
        conn, cursor = mock_db_cursor(rows=self.ROWS_BD)
        with patch("app.get_connection", return_value=conn):
            client.get("/upload/series")
        conn.close.assert_called_once()
        cursor.close.assert_called_once()


# ════════════════════════════════════════════════════════════════════════════
# 3. Tests d'intégration de bout en bout (flux complet mocké)
# ════════════════════════════════════════════════════════════════════════════

class TestFluxComplet:
    """Simule un upload suivi d'un listage, avec une BD mockée cohérente."""

    def test_upload_puis_list(self, client):
        """Upload 3 lignes → GET /series renvoie bien 1 série avec 3 points."""
        csv = (
            "nom_serie,valeur,categorie,date_mesure\n"
            "serie_X,1.0,cat,2024-03-01\n"
            "serie_X,2.0,cat,2024-03-02\n"
            "serie_X,3.0,cat,2024-03-03\n"
        )

        # Upload
        conn_up, _ = mock_db_cursor()
        with patch("app.get_connection", return_value=conn_up):
            res_up = client.post(
                "/upload/csv",
                data={"file": make_csv_file(csv)},
                content_type="multipart/form-data",
            )
        assert res_up.status_code == 201
        assert res_up.get_json()["lignes_inserees"] == 3

        # Listage
        rows = [("serie_X", 3, "2024-03-01", "2024-03-03")]
        conn_get, _ = mock_db_cursor(rows=rows)
        with patch("app.get_connection", return_value=conn_get):
            res_get = client.get("/upload/series")
        assert res_get.status_code == 200
        body = res_get.get_json()
        assert body["total"] == 1
        assert body["series"][0]["n_points"] == 3
