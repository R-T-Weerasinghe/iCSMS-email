from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_read_main_docs():
    response = client.get("/docs")
    assert response.status_code == 200

def test_read_main_openapi():
    response = client.get("/openapi.json")
    assert response.status_code == 200

def test_read_main_v2():
    response = client.get("/email/v2/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Email Filtering API Version 2!"}