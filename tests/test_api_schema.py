from fastapi.testclient import TestClient
from src.main import app  # adjust to your entrypoint

client = TestClient(app)

def test_generate_patched_returns_schema():
    r = client.post("/generate_patched", json={"prompt":"hello"})
    assert r.status_code == 200
    j = r.json()
    assert "response" in j
    assert "target" in j
