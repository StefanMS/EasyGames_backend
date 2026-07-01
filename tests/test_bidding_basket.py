from datetime import datetime, timedelta, timezone


async def create_game(client, name="Chess", active=True):
    expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    response = await client.post("/add-game", data={
        "game_name": name,
        "active_game": "true" if active else "false",
        "expires_at": expires_at,
    })
    assert response.status_code == 200
    return response.json()


async def test_create_bid(client, as_user):
    game = await create_game(client)
    as_user(1)

    response = await client.post("/bids/", params={"game_id": game["game_id"]})

    assert response.status_code == 200
    body = response.json()
    assert body["game_id"] == game["game_id"]
    assert body["player_id"] == 1


async def test_get_bid_by_id(client, as_user):
    game = await create_game(client)
    as_user(1)
    created = (await client.post(
        "/bids/", params={"game_id": game["game_id"]}
    )).json()

    response = await client.get(f"/bids/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


async def test_get_bid_by_id_not_found(client):
    response = await client.get("/bids/999999")

    assert response.status_code == 404


async def test_get_all_bidding_baskets(client, as_user):
    game = await create_game(client)
    as_user(1)
    await client.post("/bids/", params={"game_id": game["game_id"]})

    response = await client.get("/bids/")

    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_owner_can_update_bid(client, as_user):
    game = await create_game(client)
    other_game = await create_game(client, name="Checkers")
    as_user(1)
    created = (await client.post(
        "/bids/", params={"game_id": game["game_id"]}
    )).json()

    response = await client.put(
        f"/bids/{created['id']}",
        json={"game_id": other_game["game_id"]},
    )

    assert response.status_code == 200
    assert response.json()["game_id"] == other_game["game_id"]


async def test_non_owner_cannot_update_bid(client, as_user):
    game = await create_game(client)
    as_user(1)
    created = (await client.post(
        "/bids/", params={"game_id": game["game_id"]}
    )).json()

    as_user(2)
    response = await client.put(
        f"/bids/{created['id']}",
        json={"game_id": game["game_id"]},
    )

    assert response.status_code == 403


async def test_update_missing_bid_returns_404(client, as_user):
    as_user(1)

    response = await client.put("/bids/999999", json={"game_id": 1})

    assert response.status_code == 404


async def test_owner_can_delete_bid(client, as_user):
    game = await create_game(client)
    as_user(1)
    created = (await client.post(
        "/bids/", params={"game_id": game["game_id"]}
    )).json()

    response = await client.delete(f"/bids/{created['id']}")

    assert response.status_code == 200
    assert (await client.get(f"/bids/{created['id']}")).status_code == 404


async def test_non_owner_cannot_delete_bid(client, as_user):
    game = await create_game(client)
    as_user(1)
    created = (await client.post(
        "/bids/", params={"game_id": game["game_id"]}
    )).json()

    as_user(2)
    response = await client.delete(f"/bids/{created['id']}")

    assert response.status_code == 403


async def test_user_filtered_collections_reports_enrollment_and_capacity(
    client, as_user
):
    game = await create_game(client)
    as_user(1)
    await client.post("/bids/", params={"game_id": game["game_id"]})

    response = await client.get("/user-collections/")

    assert response.status_code == 200
    [entry] = [g for g in response.json() if g["id"] == game["game_id"]]
    assert entry["enrolled_user"] is True
    assert entry["capacity"] == 1
