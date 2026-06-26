def test_create_requires_auth(client):
    resp = client.post("/api/v1/projects", json={"name": "X"})
    assert resp.status_code == 401


def test_create_and_list(auth_client):
    resp = auth_client.post("/api/v1/projects", json={"name": "Mi proyecto"})
    assert resp.status_code == 201
    resp = auth_client.get("/api/v1/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_isolation_between_users(client):
    client.post(
        "/api/v1/auth/register", json={"email": "ana@test.com", "password": "secret123"}
    )
    ana = client.post(
        "/api/v1/auth/login", data={"username": "ana@test.com", "password": "secret123"}
    ).json()["access_token"]
    created = client.post(
        "/api/v1/projects",
        json={"name": "De Ana"},
        headers={"Authorization": f"Bearer {ana}"},
    )
    project_id = created.json()["id"]

    client.post(
        "/api/v1/auth/register",
        json={"email": "beto@test.com", "password": "secret123"},
    )
    beto = client.post(
        "/api/v1/auth/login",
        data={"username": "beto@test.com", "password": "secret123"},
    ).json()["access_token"]
    resp = client.get(
        f"/api/v1/projects/{project_id}", headers={"Authorization": f"Bearer {beto}"}
    )
    assert resp.status_code == 404
