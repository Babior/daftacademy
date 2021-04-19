from fastapi.testclient import TestClient

from main import app
import pytest

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world!"}

def test_request_method():
    response = client.get("/method")
    assert response.status_code == 200


def test_auth():
    response = client.get("/auth")
    assert response.status_code == 201
    assert response.json() == {"message": "Hello World"}