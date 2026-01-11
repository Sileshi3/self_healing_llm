# from fastapi.testclient import TestClient
# from src.main import app  # adjust to your entrypoint
# import pytest 


# client = TestClient(app)

# def test_generate_patched_returns_schema():
#     r = client.post("/generate_patched", json={"prompt":"hello"})
#     assert r.status_code == 200
#     j = r.json()
#     assert "response" in j
#     assert "target" in j 
 
# def test_openapi_has_generate_routes():
#     client = TestClient(app)
#     r = client.get("/openapi.json")
#     assert r.status_code == 200
#     schema = r.json()

#     paths = schema.get("paths", {})
#     assert "/generate" in paths
#     assert "/generate_patched" in paths


# def test_generate_schema_roundtrip():
#     client = TestClient(app)
#     payload = {"prompt": "hello"}
#     r = client.post("/generate", json=payload)
#     assert r.status_code == 200
#     data = r.json()
#     assert "response" in data
#     assert "target" in data


# def test_generate_patched_schema_roundtrip():
#     client = TestClient(app)
#     payload = {"prompt": "hello"}
#     r = client.post("/generate_patched", json=payload)
#     assert r.status_code == 200
#     data = r.json()
#     assert "response" in data
#     assert data.get("target") in ("B", "A")  # B expected


from fastapi.testclient import TestClient
from src.main import app  # adjust if your FastAPI app lives elsewhere

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

