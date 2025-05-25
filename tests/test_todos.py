from http import HTTPStatus

import factory.fuzzy
import pytest
from sqlalchemy import select

from fast_zero.models import Todo, TodoState, User


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Todo',
                'description': 'Test Description',
                'state': 'draft',
            },
        )
    todo = response.json()
    assert response.status_code == HTTPStatus.CREATED
    assert todo == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'Test Description',
        'state': 'draft',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(expected_todos))
    await session.commit()
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )
    todos = response.json()
    assert response.status_code == HTTPStatus.OK
    assert len(todos['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session, client, user, token
):
    create_todos = 5
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(create_todos, user_id=user.id))
    await session.commit()
    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )
    todos = response.json()
    assert response.status_code == HTTPStatus.OK
    assert len(todos['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    filter_title = 'Test todo 1'
    session.add_all(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            title=filter_title,
        )
    )
    await session.commit()
    response = client.get(
        f'/todos/?title={filter_title}',
        headers={'Authorization': f'Bearer {token}'},
    )
    todos = response.json()
    assert response.status_code == HTTPStatus.OK
    assert len(todos['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    filter_description = 'Test todo 1'
    session.add_all(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            description=filter_description,
        )
    )
    await session.commit()
    response = client.get(
        f'/todos/?description={filter_description}',
        headers={'Authorization': f'Bearer {token}'},
    )
    todos = response.json()
    assert response.status_code == HTTPStatus.OK
    assert len(todos['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    filter_state = TodoState.draft
    session.add_all(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            state=filter_state,
        )
    )
    await session.commit()
    response = client.get(
        f'/todos/?state={filter_state.value}',
        headers={'Authorization': f'Bearer {token}'},
    )
    todos = response.json()
    assert response.status_code == HTTPStatus.OK
    assert len(todos['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )

    await session.commit()
    url = '/todos/?'
    url += 'title=Test todo combined'
    url += '&description=description'
    url += '&state=done'
    response = client.get(
        url,
        headers={'Authorization': f'Bearer {token}'},
    )
    todos = response.json()
    assert response.status_code == HTTPStatus.OK
    assert len(todos['todos']) == expected_todos


def test_patch_todo_error(client, token):
    response = client.patch(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Task not found',
    }


@pytest.mark.asyncio
async def test_patch_todo_should_update_todo(session, client, user, token):
    todo = TodoFactory.create(user_id=user.id)
    session.add(todo)

    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Updated Title',
        },
    )
    updated_todo = response.json()
    assert response.status_code == HTTPStatus.OK
    assert updated_todo['title'] == 'Updated Title'


@pytest.mark.asyncio
async def test_delete_todo_should_remove_todo(session, client, user, token):
    todo = TodoFactory.create(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.',
    }


def test_delete_todo_error(client, token):
    response = client.delete(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Task not found',
    }


@pytest.mark.asyncio
async def test_list_todos_shoud_return_all_expected_fields(
    session, client, user, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory.create(user_id=user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json()['todos'] == [
        {
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
            'description': todo.description,
            'id': todo.id,
            'state': todo.state.value,
            'title': todo.title,
        }
    ]


@pytest.mark.asyncio
async def test_create_todo_with_wrong_state_raises_error(session, user: User):
    todo = Todo(
        title='Test Todo',
        description='Test Description',
        state='test',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    with pytest.raises(LookupError):
        await session.scalar(select(Todo))
