import asyncio
import pytest
from fastapi.testclient import TestClient
from backend import app

from tortoise.contrib.test import initializer, finalizer


@pytest.fixture(scope="function")
def client():
    loop = asyncio.new_event_loop()
    initializer(
        modules=["backend.models"],
        db_url="sqlite://:memory:",
        loop=loop,
    )

    with TestClient(app) as c:
        yield c

    finalizer()


@pytest.fixture(scope="function")
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


def create_user(client, name):
    token = client.post(
        "/register",
        json={
            "name": name,
            "surname": "Doe",
            "description": "Chess player",
            "birth_date": "2001-06-13",  # ISO 8601
            "email": "example.com",
            "password": "12345",
        },
    ).json()["token"]

    user = client.get("/me", headers={"X-Token": token}).json()
    user["token"] = token
    return user
