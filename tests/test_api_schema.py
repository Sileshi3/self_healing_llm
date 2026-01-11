from fastapi.testclient import TestClient
from src.main import app    

client = TestClient(app) 

def test_openapi_contains_generate_routes():
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()

    paths = data.get("paths", {})
    assert "/generate" in paths
    assert "/generate_patched" in paths

    # ensure POST exists
    assert "post" in paths["/generate"]
    assert "post" in paths["/generate_patched"]
 
def test_openapi_has_generate_routes():
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()

    paths = schema.get("paths", {})
    assert "/generate" in paths
    assert "/generate_patched" in paths


def test_generate_schema_roundtrip():
    with TestClient(app) as client: 
        payload = {"prompt": "hello"}
        r = client.post("/generate", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "response" in data
        assert "target" in data

def test_generate_patched_schema_roundtrip():
    with TestClient(app) as client:
        payload = {"prompt": "hello"}
        r = client.post("/generate_patched", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "response" in data
        assert "target" in data

 




