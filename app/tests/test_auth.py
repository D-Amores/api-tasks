def test_register(client):
    resp = client.post(
        "/api/v1/auth/register", json={"email": "new@test.com", "password": "secret123"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "new@test.com"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate(client):
    client.post(
        "/api/v1/auth/register", json={"email": "dup@test.com", "password": "secret123"}
    )
    resp = client.post(
        "/api/v1/auth/register", json={"email": "dup@test.com", "password": "secret123"}
    )
    assert resp.status_code == 409


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register", json={"email": "log@test.com", "password": "secret123"}
    )
    resp = client.post(
        "/api/v1/auth/login", data={"username": "log@test.com", "password": "wrong"}
    )
    assert resp.status_code == 401
