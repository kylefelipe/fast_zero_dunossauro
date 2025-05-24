from http import HTTPStatus


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
