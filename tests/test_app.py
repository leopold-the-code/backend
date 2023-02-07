from fastapi.testclient import TestClient
from backend import app

client = TestClient(app)


def test_create_user():
    resp = client.post(
        "/register",
        json={
            "name": "John",
            "surname": "Doe",
            "description": "Chess player",
            "birth_date": "2001-06-13",  # ISO 8601
            "email": "example.com",
            "password": "12345",
        },
    )
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_no_token_duplicates():
    user1 = client.post(
        "/register",
        json={
            "name": "John",
            "surname": "Doe",
            "description": "Chess player",
            "birth_date": "2001-06-13",
            "email": "example2.com",
            "password": "12345",
        },
    )
    user2 = client.post(
        "/register",
        json={
            "name": "John",
            "surname": "Doe",
            "description": "Chess player",
            "birth_date": "2001-06-13",
            "email": "example3.com",
            "password": "12345",
        },
    )
    assert (user1.status_code, user2.status_code) == (200, 200)
    assert user1.json()["token"] != user2.json()["token"]


def test_add_tags():
    resp = client.post("/tag", headers={"X-Token": "demotoken"}, json={"tag": "chess"})
    assert resp.status_code == 200


def test_get_people_unauthorized():
    resp = client.get("/people")
    assert resp.status_code == 401  # Unauthorized


def test_get_people():
    resp = client.get("/people", headers={"X-Token": "demotoken"})
    assert resp.status_code == 200

    json_data = resp.json()
    assert len(json_data["users"]) == 10

    for user in json_data["users"]:
        assert "id" in user
        assert "name" in user
        assert "surname" in user
        assert "description" in user
        assert "password" not in user

    swipes = ["/like"] * 5 + ["/dislike"] * 5

    for user, swipe in zip(json_data["users"], swipes):
        resp = client.post(
            swipe, headers={"X-Token": "demotoken"}, json={"id": user["id"]}
        )
        assert resp.status_code == 200
