from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as SQLAlchemySession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Token
from fast_zero.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

router = APIRouter(prefix="/auth", tags=["auth"])


OAuth2From = Annotated[
    OAuth2PasswordRequestForm,
    Depends(),
]

Session = Annotated[
    SQLAlchemySession,
    Depends(get_session),
]


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2From,
    session: Session,
):
    """Gera um token de acesso para o usuário."""

    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    user = await session.scalar(
        select(User).where(User.email == form_data.username),
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        data={"sub": user.email},
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/refresh_token", response_model=Token)
async def refresh_access_token(user: CurrentUser):
    """Gera um novo token de acesso para o usuário."""

    new_access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
