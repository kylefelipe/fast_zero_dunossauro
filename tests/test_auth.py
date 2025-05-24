from datetime import datetime, timedelta
from http import HTTPStatus

from freezegun import freeze_time

from fast_zero.security import settings


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_token_expired_after_time(client, user):
    base_time = '2023-10-01 12:00:00'
    # Pega o tempo de validade do token
    t_expired = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    # Adiciona 1 minuto para garantir que o token esteja expirado
    t_expired = timedelta(minutes=t_expired + 1)
    # Cria um tempo expirado usando o timedelta
    expired_time = datetime.strptime(base_time, '%Y-%m-%d %H:%M:%S')
    expired_time += t_expired
    with freeze_time(base_time):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        token = response.json()['access_token']

    with freeze_time(expired_time):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wronwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrongpassword',
            },
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate credentials',
    }


def test_token_inexistent_user(client):
    response = client.post(
        '/auth/token',
        data={
            'username': 'john_doe@notfound.com',
            'password': 'notfoundpassword',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_token_incorrect_password(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': 'wrongpassword',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_refresh_token(client, user, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(client, user):
    base_time = '2023-10-01 12:00:00'
    # Pega o tempo de validade do token
    t_expired = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    # Adiciona 1 minuto para garantir que o token esteja expirado
    t_expired = timedelta(minutes=t_expired + 1)
    # Cria um tempo expirado usando o timedelta
    expired_time = datetime.strptime(base_time, '%Y-%m-%d %H:%M:%S')
    expired_time += t_expired

    with freeze_time(base_time):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time(expired_time):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate credentials',
    }
