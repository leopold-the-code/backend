import asyncio
import pytest
from fastapi.testclient import TestClient
from backend import app

from tortoise.contrib.test import initializer, finalizer


@pytest.fixture(scope="session")
def client():
    loop = asyncio.new_event_loop()
    initializer(
        modules=["backend.models.models"],
        db_url="sqlite://:memory:",
        loop=loop,
    )

    with TestClient(app) as c:
        yield c

    finalizer()


@pytest.fixture(scope="session")
def demotoken(client):
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
    return resp.json()["token"]


def test_create_user(client):
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


def test_no_token_duplicates(client):
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


def test_add_tags(demotoken, client):
    resp = client.post("/tag", headers={"X-Token": demotoken}, json={"tag": "chess"})
    assert resp.status_code == 200


def test_get_people_unauthorized(client):
    resp = client.get("/feed")
    assert resp.status_code == 401  # Unauthorized


def test_get_people(demotoken, client):
    resp = client.get("/feed", headers={"X-Token": demotoken})
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
            swipe, headers={"X-Token": demotoken}, json={"id": user["id"]}
        )
        assert resp.status_code == 200


def test_me(client):
    mydata = {
        "name": "John",
        "surname": "Doe",
        "description": "Chess player",
        "birth_date": "2001-06-13",
        "email": "exampleN.com",
    }
    mytoken = client.post(
        "/register",
        json={
            "name": mydata["name"],
            "surname": mydata["surname"],
            "description": mydata["description"],
            "birth_date": mydata["birth_date"],
            "email": "exampleN.com",
            "password": "12345",
        },
    ).json()["token"]

    me = client.get("/me", headers={"X-Token": mytoken}).json()

    for key, value in mydata.items():
        assert me[key] == value
