from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Olá Mundo"}


def test_send_html_deve_retornar_ok_e_html(client):
    response = client.get("/html")

    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert (
        response.text
        == """
    <html>
        <head>
            <title>FastAPI HTML</title>
        </head>
        <body>
            <h1>Olá Mundo</h1>
        </body>
    </html>
    """
    )


def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "manahmanah@muppets.com",
            "password": "testpassword",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "username": "testuser",
        "email": "manahmanah@muppets.com",
        "id": 1,
    }


def test_read_users(client):
    response = client.get("/users/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


def test_read_user(client, user):

    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(f"/users/{user.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_read_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_update_user(client, user):

    response = client.put(
        "/users/1",
        json={
            "username": "updateduser",
            "email": "manahmanahupdated@muppets.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "updateduser",
        "email": "manahmanahupdated@muppets.com",
        "id": 1,
    }


def test_delete_user(client, user):
    response = client.delete(f"/users/{user.id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_update_integrity_error_username(client, user):
    # Cria um novo usuário
    client.post(
        "/users/",
        json={
            "username": "testuser2",
            "email": "testuser2@testado.com",
            "password": "testpassword",
        },
    )
    # Aterando o user.username da fixture para o mesmo do novo usuário
    response_update = client.put(
        f"/users/{user.id}",
        json={
            "username": "testuser2",
            "email": "cobaia@laboratorio.com",
            "password": "cobaia123",
        },
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        "detail": "Username or email already exists",
    }


def test_update_integrity_error_email(client, user):
    # Cria um novo usuário
    client.post(
        "/users/",
        json={
            "username": "testuser3",
            "email": "testeuser3@testado.com",
            "password": "testpassword",
        },
    )
    # Aterando o user.email da fixture para o mesmo do novo usuário
    response_update = client.put(
        f"/users/{user.id}",
        json={
            "username": "cobaia",
            "email": "testeuser3@testado.com",
            "password": "testpassword",
        },
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        "detail": "Username or email already exists",
    }


def test_update_user_not_found(client):
    response = client.put(
        "/users/999",
        json={
            "username": "notfounduser",
            "email": "notfounduser@missing.com",
            "password": "notfoundpassword",
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_delete_user_not_found(client):
    response = client.delete("/users/999")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}
