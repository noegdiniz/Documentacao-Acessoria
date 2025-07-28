import pytest
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Login com Google" in response.data # Verificando um texto presente no HTML renderizado

# Example: Test login page rendering
def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data

# Example: Test protected route (should redirect if not logged in)
def test_protected_route_requires_login(client):
    response = client.get("/adm_empresas", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data or b"Login com Google" in response.data

# Example: Test 404 error page
def test_404_page(client):
    response = client.get("/nonexistentpage")
    assert response.status_code == 404
    assert b"404" in response.data or b"Not Found" in response.data

# Example: Test logout (should redirect to login)
def test_logout(client):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data or b"Login com Google" in response.data
