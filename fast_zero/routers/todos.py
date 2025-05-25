from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fast_zero.security import get_current_user

router = APIRouter(
    prefix='/todos',
    tags=['Todos'],
)

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
TodoFilter = Annotated[FilterTodo, Query()]


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=TodoList,
)
async def list_todos(
    session: Session,
    user: CurrentUser,
    filter_todo: TodoFilter,
):
    query = select(Todo).where(Todo.user_id == user.id)

    if filter_todo.title:
        query = query.filter(Todo.title.contains(filter_todo.title))

    if filter_todo.description:
        query = query.filter(
            Todo.description.contains(filter_todo.description),
        )

    if filter_todo.state:
        query = query.filter(Todo.state == filter_todo.state)

    todos = await session.scalars(
        query.offset(filter_todo.skip).limit(filter_todo.limit)
    )

    return {'todos': todos.all()}


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=TodoPublic,
)
async def create_todo(
    todo: TodoSchema,
    session: Session,
    user: CurrentUser,
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.patch(
    '/{todo_id}',
    status_code=HTTPStatus.OK,
    response_model=TodoPublic,
)
async def patch_todo(
    todo_id: int,
    session: Session,
    user: CurrentUser,
    todo: TodoUpdate,
):
    db_todo = await session.scalar(
        select(Todo).where(
            Todo.id == todo_id,
            Todo.user_id == user.id,
        )
    )
    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo


@router.delete(
    '/{todo_id}',
    response_model=Message,
)
async def delete_todo(
    todo_id: int,
    session: Session,
    user: CurrentUser,
):
    todo = await session.scalar(
        select(Todo).where(
            Todo.user_id == user.id,
            Todo.id == todo_id,
        )
    )
    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    await session.delete(todo)
    await session.commit()
    return {'message': 'Task has been deleted successfully.'}
