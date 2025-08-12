from datetime import datetime, timedelta, UTC

import pytest
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from unittest.mock import MagicMock, patch


from ..auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    pwd_context,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from ..models import User
from ..schemas import User as UserSchema

TEST_SECRET_KEY = "big_booba_key"

def test_get_password_hash():
    password = "secretboobaword"
    hashed_password = get_password_hash(password)
    assert hashed_password is not None
    assert isinstance(hashed_password, str)
    assert hashed_password != password
    assert verify_password(password, hashed_password) is True

def test_verify_password_correct():
    password = "secretWord"
    hashed_password = pwd_context.hash(password)
    assert verify_password(password, hashed_password) is True

def test_verify_password_incorrect():
    password = "secretWord"
    wrong_password = "UNsecretWord"
    hashed_password = pwd_context.hash(password)
    assert verify_password(wrong_password, hashed_password) is False


@patch('SecureNotesAPI.auth.SECRET_KEY', TEST_SECRET_KEY)
@patch("SecureNotesAPI.auth.ALGORITHM", ALGORITHM)
def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert isinstance(token, str)

    decoded_payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_payload["sub"] == "testuser"
    assert "exp" in decoded_payload
    assert decoded_payload["exp"] > datetime.now(UTC).timestamp()


@patch('SecureNotesAPI.auth.SECRET_KEY', TEST_SECRET_KEY)
@patch("SecureNotesAPI.auth.ALGORITHM", ALGORITHM)
def test_create_access_token_with_expires_delta():
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=10)
    token = create_access_token(data, expires_delta=expires_delta)

    decoded_payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[ALGORITHM])

    assert "exp" in decoded_payload
    excepted_expiry_timestamp = (datetime.now(UTC) + expires_delta).timestamp()
    assert abs(decoded_payload["exp"] - excepted_expiry_timestamp) < 5


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.username = "mockuser"
    user.id = 1
    return user


@pytest.fixture
def mock_db_session():
    return MagicMock()


@patch('SecureNotesAPI.auth.SECRET_KEY', TEST_SECRET_KEY)
@patch("SecureNotesAPI.auth.ALGORITHM", ALGORITHM)
async def test_get_current_user_success(mock_db_session, mock_user):
    with patch('SecureNotesAPI.auth.jwt.decode', return_value = {"sub": "mocker", "exp": 9999999999}) as mock_jwt_decode:
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        current_user = await get_current_user("dummy token", mock_db_session)

        assert current_user == mock_user

        mock_jwt_decode.assert_called_once_with("dummy token", TEST_SECRET_KEY, algorithms=[ALGORITHM])

        mock_db_session.query.assert_called_once_with(User)
        mock_db_session.query.return_value.filter.assert_called_once()


@patch('SecureNotesAPI.auth.SECRET_KEY', TEST_SECRET_KEY)
@patch("SecureNotesAPI.auth.ALGORITHM", ALGORITHM)
async def test_get_current_user_invalid_token():
    with patch('SecureNotesAPI.auth.jwt.decode', side_effect=JWTError):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid_token", MagicMock())
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Could not validate credentials"


@patch('SecureNotesAPI.auth.SECRET_KEY', TEST_SECRET_KEY)
@patch("SecureNotesAPI.auth.ALGORITHM", ALGORITHM)
async def test_get_current_user_no_username_in_token():
    with patch('SecureNotesAPI.auth.jwt.decode', return_value = {"foo": "bar"}):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("token_without_sub", MagicMock())
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Could not validate credentials"


@patch('SecureNotesAPI.auth.SECRET_KEY', TEST_SECRET_KEY)
@patch("SecureNotesAPI.auth.ALGORITHM", ALGORITHM)
async def test_get_current_user_user_not_found(mock_db_session):
    with patch('SecureNotesAPI.auth.jwt.decode', return_value = {"sub": "mocker", "exp": 9999999999}):
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("token_for_nonexistent_user", mock_db_session)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Could not validate credentials"


