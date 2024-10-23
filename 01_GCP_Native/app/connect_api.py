import json
import requests
import os
import sys
from dotenv import load_dotenv
from google.cloud import pubsub_v1
# Custom Logging
from loguru import logger
from logging_config import configure_logger

# Configure logging
configure_logger()

# Load environment variables from .env file
load_dotenv("./secrets/.env.local")

# Environment variables
logger.debug("Attempting to load environment variables!")
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
TOPIC_ID = os.getenv("TOPIC_ID")
logger.debug("Done loading environment variables!")

# Raise an error if critical environment variables are missing
if not BASE_URL or not API_KEY or not PROJECT_ID or not REGION or not TOPIC_ID:
    logger.critical("Critical environment variables are missing! Exiting program.")
    raise EnvironmentError("Environment variables must be set.")

# Function to make an HTTP request to the API endpoint
def pull_from_api(event, context):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    headers = {
        'X-CMC_PRO_API_KEY': API_KEY
    }

    data_json = None  # Initialize data_json

    try:
        # Make the API request
        response = requests.get(f"{BASE_URL}/v1/cryptocurrency/listings/latest", headers=headers)
        response.raise_for_status()  # Raise error for HTTP errors
        data_json = response.json()
        logger.info("API request successful.")
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {e}")
        return  # Exit the function if API request fails
    
    # Pretty-print JSON data for better readability in logs
    pretty_json = json.dumps(data_json["data"][0], indent=4)
    # Local
    logger.debug(f"Json Data:\n{pretty_json}")
    # Production
    # logger.debug(f"Json Data: {data_json}")

    # Ensure data_json was successfully retrieved
    if data_json:
        try:
            logger.info("Creating Publisher...")
            # Google Cloud's message queue service
            publisher = pubsub_v1.PublisherClient()
            logger.debug(f"Publisher: {publisher}")
            # Creating Topic
            logger.info("Creating Topic...")
            topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
            logger.debug(f"Topic Path: {topic_path}")
            # Creating Message: Data coming from API
            logger.info("Creating Message...")
            message = json.dumps(data_json).encode("utf-8")
            logger.debug(f"Message: {message}")
            # Publish message to Pub/Sub
            logger.info("Sending Message...")
            future1 = publisher.publish(topic_path, message)
            logger.info(f"Message published with result: {future1.result()}")
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
    else:
        logger.error("No data received from API; nothing to publish.")

# Uncomment this line if you want to run the function in production (GCP)
pull_from_api(None, None)
