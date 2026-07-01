import pytest


SIGNUP_PAYLOAD = {
    "email": "player@example.com",
    "first_name": "Ada",
    "last_name": "Lovelace",
    "password": "correct-horse",
}


async def test_signup_creates_user(client):
    response = await client.post("/sign-up", json=SIGNUP_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == SIGNUP_PAYLOAD["email"]
    assert "id" in body
    assert "password" not in body


async def test_signup_rejects_duplicate_email(client):
    await client.post("/sign-up", json=SIGNUP_PAYLOAD)
    response = await client.post("/sign-up", json=SIGNUP_PAYLOAD)

    assert response.status_code == 400


async def test_login_with_correct_credentials(client):
    await client.post("/sign-up", json=SIGNUP_PAYLOAD)

    response = await client.post("/login", data={
        "username": SIGNUP_PAYLOAD["email"],
        "password": SIGNUP_PAYLOAD["password"],
    })

    assert response.status_code == 200
    assert response.json()["email"] == SIGNUP_PAYLOAD["email"]


async def test_login_with_wrong_password(client):
    await client.post("/sign-up", json=SIGNUP_PAYLOAD)

    response = await client.post("/login", data={
        "username": SIGNUP_PAYLOAD["email"],
        "password": "not-the-password",
    })

    assert response.status_code == 401


async def test_login_with_unknown_email(client):
    response = await client.post("/login", data={
        "username": "nobody@example.com",
        "password": "whatever",
    })

    assert response.status_code == 401


async def test_logout(client):
    response = await client.post("/logout")

    assert response.status_code == 200
