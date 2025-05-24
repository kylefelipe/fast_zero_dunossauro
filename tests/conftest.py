import secrets
import string
from contextlib import contextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash


def create_password(length=8):
    """Cria uma senha aleatória de 8 caracteres."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


@pytest.fixture
def client(session):
    """Fixture para criar um cliente de teste do FastAPI."""

    def get_session_override():
        """Sobrescreve a função de dependência get_session para testes."""
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    """Fixture para criar uma sessão de banco de dados para testes."""
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 5, 9)):
    """Mocka o tempo do banco de dados para um modelo específico."""

    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    event.listen(model, 'before_update', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)
    event.remove(model, 'before_update', fake_time_hook)


@pytest.fixture
def mock_db_time():
    """Fixture para mockar o tempo do banco de dados."""
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session):
    """Fixture para criar um usuário de teste."""
    plain_password = create_password()
    user = UserFactory(password=get_password_hash(plain_password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = plain_password
    return user


@pytest_asyncio.fixture
async def other_user(session):
    """Fixture para criar um outro usuário de teste."""
    plain_password = create_password()
    user = UserFactory(password=get_password_hash(plain_password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def users(session):
    """Fixture para criar uma lista de usuários de teste."""
    users = []
    for _ in range(5):
        plain_password = create_password()
        user = UserFactory(password=get_password_hash(plain_password))
        session.add(user)
        await session.commit()
        await session.refresh(user)
        users.append(user)

    return users


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    return response.json()['access_token']


class UserFactory(factory.Factory):
    """Factory para criar usuários de teste."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
