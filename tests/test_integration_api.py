"""Integration tests exercising authentication, contacts, and role checks."""

from unittest.mock import Mock, patch

from src.services.auth import create_token


def test_registration_login_confirmation_and_reset(client, monkeypatch):
    monkeypatch.setattr("src.api.auth.send_verification_email", Mock())
    payload = {"username": "newuser", "email": "new@example.com", "password": "secret1"}
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201, response.text
    assert response.json()["role"] == "user"
    assert client.post("/api/auth/register", json=payload).status_code == 409
    assert client.post("/api/auth/login", data={"username": "newuser", "password": "secret1"}).status_code == 401

    confirmation = create_token("new@example.com", "email", 60)
    assert client.get(f"/api/auth/confirmed_email/{confirmation}").status_code == 200
    login = client.post("/api/auth/login", data={"username": "newuser", "password": "secret1"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"

    monkeypatch.setattr("src.api.auth.send_password_reset_email", Mock())
    requested = client.post("/api/auth/request-password-reset", json={"email": "new@example.com"})
    assert requested.status_code == 202
    reset = create_token("new@example.com", "password_reset", 60)
    assert client.post("/api/auth/reset-password", json={"token": reset, "new_password": "changed1"}).status_code == 200
    assert client.post("/api/auth/login", data={"username": "newuser", "password": "changed1"}).status_code == 200


def test_authentication_errors_and_private_profile(client, user_headers):
    assert client.post("/api/auth/login", data={"username": "regular", "password": "wrong"}).status_code == 401
    assert client.get("/api/users/me").status_code == 401
    response = client.get("/api/users/me", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "regular"


def test_contacts_crud_search_and_conflicts(client, user_headers):
    payload = {
        "first_name": "Ada", "last_name": "Lovelace", "email": "ada@example.com",
        "phone": "1234567", "birthday": "2000-09-22", "additional_data": "friend"
    }
    created = client.post("/api/contacts/", json=payload, headers=user_headers)
    assert created.status_code == 201, created.text
    contact_id = created.json()["id"]
    assert client.post("/api/contacts/", json=payload, headers=user_headers).status_code == 409
    listed = client.get("/api/contacts/?first_name=Ada", headers=user_headers)
    assert listed.status_code == 200 and len(listed.json()) == 1
    assert client.get(f"/api/contacts/{contact_id}", headers=user_headers).status_code == 200
    updated = client.put(f"/api/contacts/{contact_id}", json={"phone": "7654321"}, headers=user_headers)
    assert updated.status_code == 200 and updated.json()["phone"] == "7654321"
    assert client.get("/api/contacts/birthdays", headers=user_headers).status_code == 200
    assert client.delete(f"/api/contacts/{contact_id}", headers=user_headers).status_code == 200
    assert client.get(f"/api/contacts/{contact_id}", headers=user_headers).status_code == 404
    assert client.delete(f"/api/contacts/{contact_id}", headers=user_headers).status_code == 404


def test_only_admin_can_update_avatar(client, user_headers, admin_headers):
    files = {"file": ("avatar.jpg", b"image", "image/jpeg")}
    assert client.patch("/api/users/avatar", headers=user_headers, files=files).status_code == 403
    with patch("src.api.users.cloudinary.uploader.upload", return_value={"secure_url": "https://cdn/avatar.jpg"}):
        response = client.patch("/api/users/avatar", headers=admin_headers, files=files)
    assert response.status_code == 200, response.text
    assert response.json()["avatar"] == "https://cdn/avatar.jpg"
