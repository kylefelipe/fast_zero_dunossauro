from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo'}


def test_send_html_deve_retornar_ok_e_html(client):
    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
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


def test_update_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'manahmanah@muppets.com',
            'password': 'testpassword',
        },
    )
    response = client.put(
        '/users/1',
        json={
            'username': 'updateduser',
            'email': 'manahmanah@muppets.com',
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'updateduser',
        'email': 'manahmanah@muppets.com',
        'id': 1,
    }


def test_delete_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'manahmanah@muppets.com',
            'password': 'testpassword',
        },
    )
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}
