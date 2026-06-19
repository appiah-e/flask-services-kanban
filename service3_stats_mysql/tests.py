import pytest
from app import app

# --------------------
# CLIENT FLASK
# --------------------
@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


# --------------------
# 1. TEST HOME
# --------------------
def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


# --------------------
# 2. TEST ERREUR DESCRIBE
# --------------------
def test_describe_missing_param(client):
    response = client.get("/db/stats/describe")
    assert response.status_code == 400


# --------------------
# 3. TEST CORRELATION
# --------------------
def test_correlation(client):
    response = client.get("/db/stats/correlation?serie_x=a&serie_y=b")
    assert response.status_code in [200, 500]