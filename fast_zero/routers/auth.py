from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Token
from fast_zero.security import (
    create_access_token,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])


OAuth2From = Annotated[
    OAuth2PasswordRequestForm,
    Depends(),
]

Session = Annotated[
    SQLAlchemySession,
    Depends(get_session),
]


@router.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2From,
    session: Session,
):
    """Gera um token de acesso para o usuário."""

    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
        )
    user = session.scalar(
        select(User).where(User.email == form_data.username),
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
        )

    access_token = create_access_token(
        data={'sub': user.email},
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer',
    }
