from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    """Testa a criação de um usuário."""
    user_test = {
        'id': 1,
        'username': 'usuariodeteste',
        'password': 'senhadetestes',
        'email': 'email@deteste.com',
        'todos': [],
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


@pytest.mark.asyncio
async def test_create_todo(session, user, mock_db_time):
    with mock_db_time(model=Todo) as time:
        todo = Todo(
            title='Teste Todo',
            description='Teste Descrição',
            state='draft',
            user_id=user.id,
        )
        session.add(todo)
        await session.commit()
    todo = await session.scalar(select(Todo))
    assert asdict(todo) == {
        'id': 1,
        'title': 'Teste Todo',
        'description': 'Teste Descrição',
        'state': 'draft',
        'user_id': user.id,
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user):
    todo = Todo(
        title='Test Todo',
        description='Test Description',
        state='draft',
        user_id=user.id,
    )
    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]
