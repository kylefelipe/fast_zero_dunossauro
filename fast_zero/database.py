from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


def get_session():
    """Cria uma nova sessão de banco de dados."""
    with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
