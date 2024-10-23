import pytest
import base64
import json
from unittest.mock import MagicMock
import os
from sqlalchemy.exc import SQLAlchemyError


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to mock environment variables."""
    monkeypatch.setenv("PROJECT_ID", "test-project")
    monkeypatch.setenv("REGION", "us-central1")
    monkeypatch.setenv("INSTANCE_NAME", "test-instance")
    monkeypatch.setenv("DB_USER", "test-user")
    monkeypatch.setenv("DB_PASS", "test-pass")
    monkeypatch.setenv("DB_NAME", "test-db")

@pytest.fixture
def mock_pubsub_event():
    """Fixture to simulate a Pub/Sub event with data from assets/testing_cryptos.json."""
    
    # Load the JSON file data from the assets folder
    with open("./test/assets/testing_cryptos.json") as json_file:
        mock_data = json.load(json_file)
    
    # Encode the data as Pub/Sub would
    encoded_message = base64.b64encode(json.dumps(mock_data).encode('utf-8')).decode('utf-8')

    # Mock the cloud_event to simulate the behavior of cloud_event.data["message"]["data"]
    mock_event = MagicMock()
    mock_event.data = {
        "message": {
            "data": encoded_message
        }
    }

    return mock_event


def test_write_to_database_sqlalchemy_error(mocker, mock_pubsub_event, mock_env_vars):
    """Test the write_to_database function with mocked Cloud SQL and SQLAlchemy, simulating a SQLAlchemy error."""

    # Mock the Google Cloud SQL connector
    mock_connector = mocker.patch('src.write_to_sql.Connector')

    # Mock SQLAlchemy engine and connection
    mock_create_engine = mocker.patch('src.write_to_sql.create_engine')
    mock_engine = MagicMock()
    mock_connection = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    # Simulate an SQLAlchemyError when executing the query
    mock_connection.execute.side_effect = SQLAlchemyError("Test SQLAlchemy Error")

    # Mock the logger to capture the SQLAlchemy error log
    mock_logger = mocker.patch('src.write_to_sql.logger')

    # Import the function after environment variables are set
    from src.write_to_sql import write_to_database

    # Call the function with the mocked Pub/Sub event
    write_to_database(mock_pubsub_event)

    # Ensure that the logger captured the SQLAlchemy error
    mock_logger.exception.assert_called_with("SQLAlchemy Error: Test SQLAlchemy Error")

    # Check that the function did not crash and continued running
    print("SQLAlchemy error test passed!")
