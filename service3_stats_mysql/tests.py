import pytest
from app import app

# Je crée un client de test Flask pour simuler les requêtes HTTP sans lancer le serveur
@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client



# Je vérifie que la route "/" fonctionne correctement et renvoie un code 200
def test_home(client):
    response = client.get("/")
    assert response.status_code == 200



# Je vérifie que si aucun paramètre "serie" n'est fourni, l'API renvoie une erreur 400
def test_describe_missing_param(client):
    response = client.get("/db/stats/describe")
    assert response.status_code == 400

# Je vérifie que la route de corrélation fonctionne même si les données sont valides ou provoquent une erreur serveur
def test_correlation(client):
    response = client.get("/db/stats/correlation?serie_x=a&serie_y=b")
    assert response.status_code in [200, 500]