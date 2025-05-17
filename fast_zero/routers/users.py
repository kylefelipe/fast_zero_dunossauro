from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import (
    FilterPage,
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fast_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix="/users", tags=["users"])

Session = Annotated[
    Session,
    Depends(get_session),
]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email),
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Username already exists",
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Email already exists",
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        username=user.username,
        password=hashed_password,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/", status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    session: Session,
    filter_users: Annotated[FilterPage, Query()],
):
    users = session.scalars(
        select(User).offset(filter_users.skip).limit(filter_users.limit)
    ).all()
    return {"users": users}


@router.get(
    "/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
def read_user(user_id: int, session: Session):
    """Retorna um usuário específico."""

    db_user = session.scalar(
        select(User).where(User.id == user_id),
    )
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found",
        )
    return db_user


@router.put("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: User = Depends(get_current_user),
):
    """Atualiza um usuário existente."""

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permissions",
        )
    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)
        session.commit()
        session.refresh(current_user)
        # Retorna o usuário atualizado
        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username or email already exists",
        )


@router.delete(
    "/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def delete_user(
    user_id: int,
    session: Session,
    current_user: User = Depends(get_current_user),
):
    """Deleta um usuário existente."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permissions",
        )
    session.delete(current_user)
    session.commit()
    return {"message": "User deleted"}
