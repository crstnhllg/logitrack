from app.core.security import SECRET_KEY, ALGORITHM, create_access_token, get_current_user
from app.models import User
from datetime import datetime, timezone, timedelta
from tests.conftest import (
    client,
    test_user,
    db_session
)
from jose import jwt
from fastapi import status


def test_create_user():
    request_data = {
        'username': 'test',
        'email': 'test@email.com',
        'role': 'admin',
        'password': '12345',
    }
    response = client.post('/auth/', json=request_data)
    data = response.json()

    assert response.status_code == 201
    assert data.get('username') == request_data.get('username')
    assert data.get('email') == request_data.get('email')
    assert data.get('role') == request_data.get('role')


def test_create_user_duplicate(test_user):
    request_data = {
        'username': test_user.username,
        'email': test_user.email,
        'role': 'admin',
        'password': '12345',
    }
    response = client.post('/auth/', json=request_data)
    data = response.json()

    assert response.status_code == 409
    assert data == {'detail': 'A user with this username or email already exists.'}


def test_login_for_access_token(test_user):
    request_data = {
        'username': test_user.username,
        'password': '12345'
    }
    response = client.post('/auth/token', data=request_data)
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert 'access_token' in json_data
    assert json_data.get('token_type') == 'bearer'


def test_invalid_login():
    request_data = {
        'username': 'invalid_username',
        'password': 'invalid_password'
    }
    response = client.post('/auth/token', data=request_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json().get('detail') == 'Invalid username or password. Please check your credentials and try again.'


def test_create_access_token(test_user):
    token = create_access_token(
        test_user.username,
        test_user.id,
        timedelta(minutes=60)
    )

    assert token is not None
    assert isinstance(token, str)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload is not None
    assert payload.get('sub') == test_user.username
    assert payload.get('id') == test_user.id


def test_get_current_user(db_session, test_user):

    expires = datetime.now(timezone.utc) + timedelta(minutes=60)
    payload = {
        'sub': test_user.username,
        'id': test_user.id,
        'exp': expires
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    user = get_current_user(db_session, token)

    assert user is not None
    assert isinstance(user, User)
    assert user.id == test_user.id