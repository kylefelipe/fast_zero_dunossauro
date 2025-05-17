from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, event
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import get_password_hash


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


@pytest.fixture
def session():
    """Fixture para criar uma sessão de banco de dados para testes."""
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    table_registry.metadata.drop_all(engine)


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


@pytest.fixture
def user(session):
    """Fixture para criar um usuário de teste."""
    plain_password = 'cobaia123'
    user = User(
        username='cobaia',
        email='cobaia@laboratorio.com',
        password=get_password_hash(plain_password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = plain_password
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        "/auth/token",
        data={
            "username": user.email,
            "password": user.clean_password,
        },
    )

    return response.json()['access_token']
