from http import HTTPStatus

from jwt import decode

from fast_zero.security import create_access_token, settings


def test_jwt():
    """Testa a criação e decodificação de um token JWT."""
    data = {"test": "test"}
    token = create_access_token(data)

    decoded_data = decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert decoded_data["test"] == "test"
    assert "exp" in decoded_data


def test_jwt_invalid_token(client):
    """Testa a decodificação de um token JWT inválido."""

    response = client.delete(
        "/users/1",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "detail": "Could not validate credentials",
    }
