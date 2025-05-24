from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    """Testa a criação de um usuário."""
    user_test = {
        'id': 1,
        'username': 'usuariodeteste',
        'password': 'senhadetestes',
        'email': 'email@deteste.com',
    }
    with mock_db_time(model=User) as time:
        new_user = User(
            username=user_test['username'],
            password=user_test['password'],
            email=user_test['email'],
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(
        select(User).where(User.username == user_test['username']),
    )

    user_test['created_at'] = time
    user_test['updated_at'] = time

    assert asdict(user) == user_test
