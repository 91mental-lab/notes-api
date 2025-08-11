from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
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