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
    with patch('SecureNotesAPI.crud.get_password_hash', return_value="hashed_password") as mock_hash:
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

def test_create_user(mock_db_session, mock_get_password_hash):
    user_in = UserCreate(username="newuser", password="newpassword")

    mock_db_user_instance = MagicMock(spec=User)
    mock_db_user_instance.username = "newuser"
    mock_db_user_instance.hashed_password = "hashed_password"
    mock_db_user_instance.id = 1

    mock_db_session.add.side_effect = lambda x: None
    mock_db_session.refresh.side_effect = lambda x: setattr( x, "id", 1)

    user = create_user(mock_db_session, user_in)

    mock_get_password_hash.assert_called_once_with(user_in.password)
    mock_db_session.refresh.assert_called_once_with(mock_db_session.add.call_args[0][0])

    assert user.username == user_in.username
    assert user.hashed_password == "hashed_password"
    assert user.id == 1


def test_get_notes(mock_db_session):
    owner_id = 1
    skip = 0
    limit = 10
    mock_notes = [MagicMock(spec=Note), MagicMock(spec=Note)]
    mock_notes[0].id = 1
    mock_notes[1].id = 2

    mock_db_session.query.return_value \
    .filter.return_value \
    .offset.return_value \
    .limit.return_value \
    .all.return_value = mock_notes

    notes = get_notes(mock_db_session, owner_id, skip, limit)

    assert notes == mock_notes
    mock_db_session.query.assert_called_once_with(Note)
    mock_db_session.query.return_value.filter.assert_called_once()
    mock_db_session.query.return_value.filter.return_value.offset.assert_called_once_with(skip)
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.assert_called_once_with(limit)
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.assert_called_once()


def test_get_note(mock_db_session):
    note_id = 1
    mock_note = MagicMock(spec=Note)
    mock_note.id = note_id

    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_note

    note = get_note(mock_db_session, note_id)

    assert note == mock_note
    mock_db_session.query.assert_called_once_with(Note)
    mock_db_session.query.return_value.filter.assert_called_once()
    mock_db_session.query.return_value.filter.return_value.first.assert_called_once()

def test_create_user_note(mock_db_session):
    note_in = NoteCreate(title="Test Note", content="Some content")
    user_id = 1

    mock_db_note_instance = MagicMock(spec=Note)
    mock_db_session.add.side_effect = lambda x: None
    mock_db_session.refresh.side_effect = lambda x: setattr(x, 'id', 100)

    note = create_user_note(mock_db_session, note_in, user_id)

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    added_note = mock_db_session.add.call_args[0][0]

    assert added_note.title == note_in.title
    assert added_note.content == note_in.content
    assert added_note.owner_id == user_id
    assert note.id == 100


def test_update_note(mock_db_session):
    note_update = NoteUpdate(title="Updated Title", content="Updated Content")
    db_note = MagicMock(spec=Note)
    db_note.title = "Old Title"
    db_note.content = "Old content"

    updated_note = update_note(mock_db_session, note_update, db_note)

    assert updated_note.title == "Updated Title"
    assert updated_note.content == "Updated Content"

    mock_db_session.add.assert_called_once_with(db_note)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(db_note)


def test_update_note_partial(mock_db_session):
    note_update = NoteUpdate(content="Only Content Updated")

    db_note = MagicMock(spec=Note)
    db_note.title = "Original Title"
    db_note.content = "Original content"

    updated_note = update_note(mock_db_session,note_update,db_note)

    assert updated_note.title == "Original Title"
    assert updated_note.content == "Only Content Updated"

    mock_db_session.add.assert_called_once_with(db_note)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(db_note)


def test_delete_note(mock_db_session):
    db_note = MagicMock(spec=Note)

    result = delete_note(mock_db_session, db_note)

    mock_db_session.commit.assert_called_once()
    assert result == {"message": "Note deleted successfully"}
