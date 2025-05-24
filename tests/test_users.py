from http import HTTPStatus

import pytest

from fast_zero.schemas import UserPublic
from fast_zero.security import create_access_token


@pytest.mark.asyncio
async def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'manahmanah@muppets.com',
            'password': 'testpassword',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'testuser',
        'email': 'manahmanah@muppets.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(f'/users/{user.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_read_user_not_found(client, user, token):
    response = client.get(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'updateduser',
            'email': 'manahmanahupdated@muppets.com',
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'updateduser',
        'email': 'manahmanahupdated@muppets.com',
        'id': user.id,
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_integrity_error_username(client, user, token):
    # Cria um novo usuário
    client.post(
        '/users/',
        json={
            'username': 'testuser2',
            'email': 'testuser2@testado.com',
            'password': 'testpassword',
        },
    )
    # Aterando o user.username da fixture para o mesmo do novo usuário
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'testuser2',
            'email': 'cobaia@laboratorio.com',
            'password': 'cobaia123',
        },
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or email already exists',
    }


def test_update_integrity_error_email(client, user, token):
    # Cria um novo usuário
    client.post(
        '/users/',
        json={
            'username': 'testuser3',
            'email': 'testeuser3@testado.com',
            'password': 'testpassword',
        },
    )
    # Aterando o user.email da fixture para o mesmo do novo usuário
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'cobaia',
            'email': 'testeuser3@testado.com',
            'password': 'testpassword',
        },
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or email already exists',
    }


def test_get_current_user_not_found(client):
    """Testa a obtenção de um usuário sem informar o e-mail."""
    data = {'no-email': 'test'}
    token = create_access_token(data)
    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate credentials',
    }


def test_get_current_user_not_exists(client):
    """Testa a obtenção de um usuário atual que não existe."""
    data = {'sub': 'notauser@missed.com'}
    token = create_access_token(data)
    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate credentials',
    }
