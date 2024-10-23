# Libraries
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
# Google Cloud Services
from google.cloud import storage
import functions_framework
# Custom Logging
from loguru import logger
from logging_config import configure_logger

# Configure logging
configure_logger()

# Local Development
dotenv_path = Path(__file__).parent / "secrets/.env"
google_credentials_path = Path(__file__).parent / "secrets/key_access_sql.json"
load_dotenv(dotenv_path)

# Environment variables
logger.debug("Attempting to load environment variables!")
BUCKET_NAME = os.getenv("BUCKET_NAME")
logger.debug(f"Bucket to access: {BUCKET_NAME}")

# Only for Local Development Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(google_credentials_path)

# Raise an error if critical environment variables are missing
if not BUCKET_NAME:
    logger.critical("Critical environment variables are missing! Exiting program.")
    raise EnvironmentError("Environment variables must be set.")

def get_previous_day():
    """
    Calculate the previous day's date and return it as a string in the format 'YYYY-MM-DD'.
    
    This function returns the date from 23:59 of the previous day.
    """
    # Calculate the previous day
    previous_day = datetime.now() - timedelta(days=1)
    previous_day_formatted = previous_day.strftime('%Y-%m-%d')
    logger.info(f"Previous Day: {previous_day_formatted}")
    return previous_day_formatted


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def consolidate_daily_files(cloud_event):
    """
    Consolidates JSON files stored in Cloud Storage.

    This function is triggered daily at 00:00 via a Cloud Pub/Sub topic. It listens for a Pub/Sub message 
    and initiates the process to retrieve all JSON files stored in a designated Cloud Storage bucket.
    These JSON files are then consolidated into a single file or dataset, which can later be stored, 
    processed, or transferred for further use (e.g., loading into BigQuery for reporting or analysis).

    Args:
        cloud_event (cloud_event): The event payload, which contains the Pub/Sub message data 
        and attributes such as the event time and triggering topic information.
    """
    logger.info("Cloud event triggered.")
    logger.info(f"Cloud Event Data: {cloud_event}")
    
    # Get the previous day's date dynamically
    previous_day_formatted = get_previous_day()

    # Initialize a Cloud Storage client
    storage_client = storage.Client()

    try:
        # Access the specified bucket
        bucket = storage_client.get_bucket(BUCKET_NAME)
        logger.info(f"Accessing bucket: {BUCKET_NAME}")
        
        # List all objects (blobs) in the bucket
        blobs = list(bucket.list_blobs(prefix="Minute/"))
        
        # Filter files by the date string (e.g., '2024-10-11')
        filtered_blobs = [blob for blob in blobs if previous_day_formatted in blob.name]
        logger.info(f"Found {len(filtered_blobs)} objects for date {previous_day_formatted}.")
        
        if not filtered_blobs:
            logger.warning(f"No files found for date: {previous_day_formatted}")
            return
        
        # Initialize a list to hold all JSON objects
        consolidated_data = []
        
        # Download each JSON file and merge it into the list
        for blob in filtered_blobs:
            # This operation takes time!
            blob_data = json.loads(blob.download_as_text())
            consolidated_data.append(blob_data)
            logger.info(f"Merged data from: {blob.name}")
            
        # Create the consolidated JSON object
        consolidated_json = {"data": consolidated_data}
        logger.info(f"Json to upload: {consolidated_json}")
        
        # Define the new file path inside the "Day" folder
        consolidated_file_name = f"Day/{previous_day_formatted}-consolidated.json"
        output_blob = bucket.blob(consolidated_file_name)
        
        # Upload the consolidated JSON back to Cloud Storage
        output_blob.upload_from_string(json.dumps(consolidated_json), content_type='application/json')
        logger.info(f"Consolidated file uploaded to {consolidated_file_name}")

    except Exception as e:
        logger.exception(f"Error in consolidate_daily_files: {e}")

        


consolidate_daily_files(None)
