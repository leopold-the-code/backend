import asyncio
import pytest
from fastapi.testclient import TestClient
from backend import app

from tortoise.contrib.test import initializer, finalizer


@pytest.fixture(scope="function")  # Creates new db for every test!
def uniq_client():
    loop = asyncio.new_event_loop()
    initializer(
        modules=["backend.models.models"],
        db_url="sqlite://:memory:",
        loop=loop,
    )

    with TestClient(app) as c:
        yield c

    finalizer()


# demotoken - user.id = 1
# demotoken - user.id = 2


def test_mutual_like(uniq_client: TestClient):
    uniq_client.post("/like", params={"subject": 2}, headers={"X-Token": "demotoken"})
    uniq_client.post("/like", params={"subject": 1}, headers={"X-Token": "demotoken2"})

    user1_matches = uniq_client.get("/matches", headers={"X-Token": "demotoken"}).json()
    companions_ids = [user["id"] for user in user1_matches]
    assert len(user1_matches) == 1
    assert 2 in companions_ids

    user2_matches = uniq_client.get(
        "/matches", headers={"X-Token": "demotoken2"}
    ).json()
    companions_ids = [user["id"] for user in user2_matches]
    assert len(user2_matches) == 1
    assert 1 in companions_ids


def test_mutual_dislike(uniq_client: TestClient):
    uniq_client.post(
        "/dislike", params={"subject": 2}, headers={"X-Token": "demotoken"}
    )
    uniq_client.post(
        "/dislike", params={"subject": 1}, headers={"X-Token": "demotoken2"}
    )

    user1_matches = uniq_client.get("/matches", headers={"X-Token": "demotoken"}).json()
    assert len(user1_matches) == 0

    user2_matches = uniq_client.get(
        "/matches", headers={"X-Token": "demotoken2"}
    ).json()
    assert len(user2_matches) == 0


def test_not_mutual(uniq_client: TestClient):
    uniq_client.post(
        "/dislike", params={"subject": 2}, headers={"X-Token": "demotoken"}
    )
    uniq_client.post("/like", params={"subject": 1}, headers={"X-Token": "demotoken2"})

    user1_matches = uniq_client.get("/matches", headers={"X-Token": "demotoken"}).json()
    assert len(user1_matches) == 0

    user2_matches = uniq_client.get(
        "/matches", headers={"X-Token": "demotoken2"}
    ).json()
    assert len(user2_matches) == 0
