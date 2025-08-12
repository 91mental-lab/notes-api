import pytest
from unittest.mock import MagicMock, patch

from twisted.internet.defer import returnValue

from ..crud import (
    get_user_by_username,
    create_user,
    get_notes,
    get_note,
    create_user_note,
    update_note,
    delete_note
)

from ..models import User, Note
from ..schemas import UserCreate, NoteCreate, NoteUpdate

@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def mock_get_password_hash():
    with patch('crud.get_password_hash', returnValue="hashed_password") as mock_hash:
        yield mock_hash


def test_get_user_by_username(mock_db_session):
    mock_user = MagicMock(spec=User)
    mock_user.username = "testuser"
    mock_user.id = 1

    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    user = get_user_by_username(mock_db_session, "testuser")

    assert user == mock_user
    mock_db_session.query.assert_called_once_with(User)
    mock_db_session.query.return_value.filter.assert_called_once()

