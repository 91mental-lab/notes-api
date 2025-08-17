import pytest
from unittest.mock import MagicMock,patch

from pytest_asyncio import fixture

import src.database

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def mock_create_engine():
    with patch('SecureNotesAPI.src.database.create_engine') as mock_engine:
        yield mock_engine

@pytest.fixture
def mock_session():
    with patch('SecureNotesAPI.src.database.create_session') as mock_sm:
        yield mock_sm

@pytest.fixture
def mock_session_local_factory():
    with patch('SecureNotesAPI.src.database.SessionLocal') as mock_slf:
        yield mock_slf


# def test_engine_creation(mocker):
    #    mocker.patch('SecureNotesAPI.config.DATABASE_URL', TEST_DATABASE_URL)
    # Патчим оригинальную функцию create_engine из sqlalchemy
    #mock_create_engine = mocker.patch('sqlalchemy.create_engine')

    # Сбрасываем кэш, чтобы get_engine() вызвал create_engine
    # database.engine = None

    #engine_instance = database.get_engine()

    #mock_create_engine.assert_called_once_with(
    #    TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    #assert engine_instance == mock_create_engine.return_value
    #assert database._engine == mock_create_engine.return_value

