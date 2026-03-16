from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_documents_requires_auth():
    response = client.get("/api/documents")
    assert response.status_code == 401


def test_list_documents_with_api_key():
    response = client.get("/api/documents", headers={"X-API-Key": "dev-api-key-change-me"})
    # Will fail without DB, but auth should pass
    assert response.status_code != 401


def test_upload_wrong_type():
    response = client.post(
        "/api/documents/upload",
        files={"file": ("test.jpg", b"fake", "image/jpeg")},
        headers={"X-API-Key": "dev-api-key-change-me"},
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


def test_openapi_docs():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "GovDoc AI" in response.json()["info"]["title"]
