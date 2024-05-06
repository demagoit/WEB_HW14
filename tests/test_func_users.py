import asyncio
from logging import raiseExceptions
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from pytest import MonkeyPatch

from src.conf import messages
from src.services.auth import auth_service

# from src.routes.users import get_refresh_token, refresh_token

test_refresh_token = None

def test_create_user_new(client: TestClient, user, monkeypatch: MonkeyPatch, mock_redis):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    responce = client.post("api/auth/signup", json=user)

    assert responce.status_code == 201, responce.text
    data = responce.json()
    assert data['email'] == user.get('email')
    assert 'id' in data


def test_create_user_exist(client: TestClient, user, monkeypatch: MonkeyPatch, mock_redis):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    responce = client.post("api/auth/signup", json=user)

    assert responce.status_code == 409, responce.text
    data = responce.json()
    assert data['detail'] == messages.USER_ALREADY_EXISTS


def test_login_user_wrong_email(client: TestClient, user, mock_redis):
    form_body = {'username': 'wrong@mail.com', 'password': user.get('password')}

    responce = client.post(
        "api/auth/login", data=form_body)

    assert responce.status_code == 401, responce.text
    data = responce.json()
    assert data['detail'] == messages.EMAIL_INVALID


def test_login_user_not_confirmed(client: TestClient, user, mock_redis):
    form_body = {'username': user.get(
        'email'), 'password': user.get('password')}

    responce = client.post(
        "api/auth/login", data=form_body)

    assert responce.status_code == 401, responce.text
    data = responce.json()
    assert data['detail'] == messages.EMAIL_NOT_CONFIRMED

def test_confirm_email_success(client: TestClient, user, mock_redis):
    async def create_email_token():
        return await auth_service.create_email_token({'sub': user.get('email')})
    email_token = asyncio.run(create_email_token())

    responce = client.get(f"api/auth/confirm_email/{email_token}")

    assert responce.status_code == 200
    data = responce.json()
    assert data['message'] == messages.EMAIL_CONFIRMED_SUCCESS

def test_confirm_email_already_confirmed(client: TestClient, user, mock_redis):
    async def create_email_token():
        return await auth_service.create_email_token({'sub': user.get('email')})
    email_token = asyncio.run(create_email_token())

    responce = client.get(f"api/auth/confirm_email/{email_token}")

    assert responce.status_code == 200
    data = responce.json()
    assert data['message'] == messages.EMAIL_ALREADY_CONFIRMED

def test_confirm_email_wrong_email(client: TestClient, user, mock_redis):
    async def create_email_token():
        return await auth_service.create_email_token({'sub': 'wrong@mail.com'})
    email_token = asyncio.run(create_email_token())

    responce = client.get(f"api/auth/confirm_email/{email_token}")

    assert responce.status_code == 400
    data = responce.json()
    assert data['detail'] == messages.VERIFICATION_ERROR

def test_login_wrong_pass(client: TestClient, user, mock_redis):
    form_body = {'username': user.get(
        'email'), 'password': 'wrong_pass'}

    responce = client.post(
        "api/auth/login", data=form_body)

    assert responce.status_code == 401, responce.text
    data = responce.json()
    assert data['detail'] == messages.PASSWORD_INVALID

def test_login_success(client: TestClient, user, mock_redis):
    global test_refresh_token
    form_body = {'username': user.get(
        'email'), 'password': user.get('password')}

    responce = client.post(
        "api/auth/login", data=form_body)

    assert responce.status_code == 200, responce.text
    data = responce.json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    test_refresh_token = data['refresh_token'] # for next test
    assert data['token_type'] == 'bearer'

def test_login_token_fail(client: TestClient, user, monkeypatch: MonkeyPatch, mock_redis):
    form_body = {'username': user.get(
        'email'), 'password': user.get('password')}
    mock_user_refresh = AsyncMock()
    mock_user_refresh.refresh_token = 'false_refresh_token'
    monkeypatch.setattr('src.repository.users.update_user_token', mock_user_refresh)

    responce = client.post(
        "api/auth/login", data=form_body)

    assert responce.status_code == 500, responce.text
    data = responce.json()
    assert data['detail'] == messages.REFRESH_TOKEN_INVALID
