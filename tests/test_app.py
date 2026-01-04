import importlib
import pathlib
import sys

from fastapi.testclient import TestClient

# Ensure src is importable
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_PATH = str(ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import app as app_module


def fresh_client():
    # Reload module to reset in-memory state between tests
    importlib.reload(app_module)
    return TestClient(app_module.app)


def test_get_activities():
    client = fresh_client()

    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()

    # Basic sanity checks
    assert isinstance(data, dict)
    assert "Programming Class" in data
    assert "participants" in data["Programming Class"]


def test_signup_and_duplicate():
    client = fresh_client()

    # Sign up a new participant
    r = client.post("/activities/Programming%20Class/signup?email=testuser@example.com")
    assert r.status_code == 200
    assert "Signed up" in r.json()["message"]

    # Signing up again should fail with 400
    r2 = client.post("/activities/Programming%20Class/signup?email=testuser@example.com")
    assert r2.status_code == 400


def test_unregister():
    client = fresh_client()

    # Ensure a known participant exists first (emma@mergington.edu)
    r0 = client.get("/activities")
    assert r0.status_code == 200
    data0 = r0.json()
    assert "emma@mergington.edu" in data0["Programming Class"]["participants"]

    # Unregister emma
    r = client.post("/activities/Programming%20Class/unregister?email=emma@mergington.edu")
    assert r.status_code == 200
    assert "Unregistered" in r.json()["message"]

    # Confirm removal
    r2 = client.get("/activities")
    data2 = r2.json()
    assert "emma@mergington.edu" not in data2["Programming Class"]["participants"]


def test_unregister_nonexistent():
    client = fresh_client()

    # Try to unregister someone who is not signed up
    r = client.post("/activities/Programming%20Class/unregister?email=doesnotexist@example.com")
    assert r.status_code == 404
