from fastapi.testclient import TestClient
from tests.test_tools import create_user

# demotoken - user.id = 1
# demotoken - user.id = 2


def test_mutual_like(client: TestClient):
    user1 = create_user(client, "user1")
    user2 = create_user(client, "user2")
    client.post(
        "/like", params={"subject": user2["id"]}, headers={"X-Token": user1["token"]}
    )
    client.post(
        "/like", params={"subject": user1["id"]}, headers={"X-Token": user2["token"]}
    )

    user1_matches = client.get("/matches", headers={"X-Token": user1["token"]}).json()
    companions_ids = [user["id"] for user in user1_matches]
    assert len(user1_matches) == 1
    assert user2["id"] in companions_ids

    user2_matches = client.get("/matches", headers={"X-Token": user2["token"]}).json()
    companions_ids = [user["id"] for user in user2_matches]
    assert len(user2_matches) == 1
    assert user1["id"] in companions_ids


def test_mutual_dislike(client: TestClient):
    user1 = create_user(client, "user1")
    user2 = create_user(client, "user2")
    client.post("/dislike", params={"subject": 2}, headers={"X-Token": user1["token"]})
    client.post(
        "/dislike", params={"subject": user1["id"]}, headers={"X-Token": user2["token"]}
    )

    user1_matches = client.get("/matches", headers={"X-Token": user1["token"]}).json()
    assert len(user1_matches) == 0

    user2_matches = client.get("/matches", headers={"X-Token": user2["token"]}).json()
    assert len(user2_matches) == 0


def test_not_mutual(client: TestClient):
    user1 = create_user(client, "user1")
    user2 = create_user(client, "user2")
    client.post(
        "/dislike", params={"subject": user2["id"]}, headers={"X-Token": user1["token"]}
    )
    client.post(
        "/like", params={"subject": user1["id"]}, headers={"X-Token": user2["token"]}
    )

    user1_matches = client.get("/matches", headers={"X-Token": user1["token"]}).json()
    assert len(user1_matches) == 0

    user2_matches = client.get("/matches", headers={"X-Token": user2["token"]}).json()
    assert len(user2_matches) == 0
