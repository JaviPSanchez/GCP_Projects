import pytest
import requests
import json
import os
from unittest.mock import patch, MagicMock
from google.cloud import pubsub_v1
from src.connect_api import pull_from_api  # Assuming your original script is named `connect_api.py`
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("../src/.env.local")

# Environment variables
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_ID = os.getenv("TOPIC_ID")
COIN = os.getenv("COIN")

# Helper function to create a mock response
def mock_response(status_code=200, json_data=None):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json = MagicMock(return_value=json_data)
    mock_resp.raise_for_status = MagicMock() if status_code == 200 else MagicMock(side_effect=requests.exceptions.HTTPError)
    return mock_resp


# Test when the API request is successful
@patch('requests.get')
@patch('google.cloud.pubsub_v1.PublisherClient')
def test_pull_from_api_success(mock_pubsub_client, mock_get):
    # Create mock response data
    api_data = {
        "data": {
            "coins": [{"id": 1, "name": "Bitcoin", "price": "50000"}]
        }
    }
    
    # Mock the API request and Pub/Sub
    mock_get.return_value = mock_response(200, json_data=api_data)
    mock_publisher = MagicMock()
    mock_pubsub_client.return_value = mock_publisher
    mock_future = MagicMock()
    mock_future.result.return_value = "Message ID"
    mock_publisher.publish.return_value = mock_future

    # Call the function
    event = {}
    context = {}
    pull_from_api(event, context)

    # Assertions
    mock_get.assert_called_once_with(f"{os.environ['BASE_URL']}/coins", headers={'x-access-token': os.environ['API_KEY']})
    mock_publisher.publish.assert_called_once()

    # Check that the response was correctly published
    message = json.dumps(api_data).encode("utf-8")
    topic_path = f"projects/{os.environ['PROJECT_ID']}/topics/{os.environ['TOPIC_ID']}"
    mock_publisher.publish.assert_called_once_with(topic_path, message)


# Test when the API request fails
@patch('requests.get')
def test_pull_from_api_api_failure(mock_get):
    # Mock the API request to raise an exception
    mock_get.return_value = mock_response(status_code=404)

    # Call the function
    event = {}
    context = {}
    pull_from_api(event, context)

    # Assertions
    mock_get.assert_called_once_with(f"{os.environ['BASE_URL']}/coin/{os.environ['COIN']}", headers={'x-access-token': os.environ['API_KEY']})


# Test when the Pub/Sub publishing fails
@patch('requests.get')
@patch('google.cloud.pubsub_v1.PublisherClient')
def test_pull_from_api_pubsub_failure(mock_pubsub_client, mock_get):
    # Create mock response data
    api_data = {
        "data": {
            "coins": [{"id": 1, "name": "Bitcoin", "price": "50000"}]
        }
    }
    
    # Mock the API request
    mock_get.return_value = mock_response(200, json_data=api_data)
    
    # Mock the Pub/Sub client to raise an exception
    mock_publisher = MagicMock()
    mock_pubsub_client.return_value = mock_publisher
    mock_publisher.publish.side_effect = Exception("Pub/Sub failure")

    # Call the function
    event = {}
    context = {}
    pull_from_api(event, context)

    # Assertions
    mock_get.assert_called_once_with(f"{os.environ['BASE_URL']}/coin/{os.environ['COIN']}", headers={'x-access-token': os.environ['API_KEY']})
    mock_publisher.publish.assert_called_once()


if __name__ == "__main__":
    pytest.main()
