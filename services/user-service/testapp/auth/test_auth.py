from faker import Faker
import pytest

faker = Faker()


def test_registration_user(client):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()
    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password,
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()

    assert isinstance(data, dict)

    user = data["user"]
    assert user["email"] == user_data["email"]
    assert user["username"] == user_data["username"]
    assert user["auth_role"] == "user"
    assert "id" in user

    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)


def test_register_user_duplicate_email_and_username(client):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()

    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password,
    }

    client.post("/auth/register", json=user_data)

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 400
    assert response.json()["detail"] in {
        "Email already exists",
        "Username already exists",
    }

def test_login_user(client):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()

    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password,
    }

    client.post("/auth/register", json=user_data)

    login_data = user_data

    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)

    user = data["user"]
    assert user["email"] == user_data["email"]
    assert user["username"] == user_data["username"]
    assert user["auth_role"] == "user"
    assert "id" in user

    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)


@pytest.mark.parametrize(
    "login_data",
    [
        {"email": faker.email(), "password": faker.password()},
        {"email": faker.email(), "password": "wrongpass"},
    ],
)
def test_login_user_invalid_credentials(client, login_data):
    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_user_wrong_password(client):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()

    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password,
    }

    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": "wrongpassword",
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_user_nonexistent_email(client):
    email = faker.email()
    password = faker.password()
    login_data = {
        "email": email,
        "password": password,
    }

    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_refresh_token_rotation(client):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()
    reg_data = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password,
    }
    reg_res = client.post("/auth/register", json=reg_data)
    old_refresh = reg_res.json()["refresh_token"]

    refresh_res = client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {old_refresh}"}
    )

    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert new_data["refresh_token"] != old_refresh

    fail_res = client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {old_refresh}"}
    )
    assert fail_res.status_code == 401

