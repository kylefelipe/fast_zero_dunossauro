from dataclasses import asdict
from datetime import datetime

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_db_time):
    """Testa a criação de um usuário."""
    user_test = {
        "id": 1,
        "username": "usuariodeteste",
        "password": "senhadetestes",
        "email": "email@deteste.com",
        "created_at": datetime(2025, 5, 9),
        "updated_at": datetime(2025, 5, 9),
    }
    with mock_db_time(model=User):
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
