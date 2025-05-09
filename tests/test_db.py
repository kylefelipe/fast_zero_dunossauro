from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_db_time):
    """Testa a criação de um usuário."""
    user_test = {
        "username": "usuariodeteste",
        "password": "senhadetestes",
        "email": "email@deteste.com",
    }
    with mock_db_time(model=User) as time:
        new_user = User(
            username=user_test["username"],
            password=user_test["password"],
            email=user_test["email"],
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(
        select(User).where(User.username == user_test["username"]),
    )

    assert asdict(user) == user_test
