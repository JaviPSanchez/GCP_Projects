# Libraries
import os
import base64
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
# GCP
from google.cloud import storage
import functions_framework
# Custom Logging
from loguru import logger
from logging_config import configure_logger

# Configure logging
configure_logger()

# Local Development
load_dotenv("./secrets/.env.local")


# Environment variables
logger.debug("Attempting to load environment variables!")
BUCKET_NAME = os.getenv("BUCKET_NAME")
logger.debug("Done loading environment variables!")

# Only for Local Development Google Application Credentials
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key_access_sql.json"

# Raise an error if critical environment variables are missing
if not BUCKET_NAME:
    logger.critical("Critical environment variables are missing! Exiting program.")
    raise EnvironmentError("Environment variables must be set.")

def write_to_storage(bucket_name, file_name, data):
    """Uploads a file to the bucket."""
    # Initialize a Cloud Storage client
    storage_client = storage.Client()

    try:
        bucket = storage_client.bucket(bucket_name)
        logger.info(f"Accessing bucket: {bucket_name}")
        
        blob = bucket.blob(file_name)
        logger.info(f"Creating blob: {file_name}")
        
        blob.upload_from_string(json.dumps(data), content_type='application/json')
        logger.info(f"File {file_name} uploaded to {bucket_name}.")
    except Exception as e:
        logger.exception(f"Error in write_to_storage: {e}")
        
def get_utc_plus_2_timestamp():
    """Generate a timestamp for UTC+2."""
    utc_now = datetime.utcnow()
    utc_plus_2 = utc_now + timedelta(hours=2)
    
    return utc_plus_2.strftime('%Y-%m-%dT%H-%M-%S')

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def write_to_database(cloud_event):
    """Triggered by Pub/Sub event and writes data to Cloud Storage."""
    logger.info("Cloud event triggered.")
    logger.info(f"Cloud Event: {cloud_event}")

    try:
        # Decode the Pub/Sub message data
        t_record = base64.b64decode(cloud_event.data["message"]["data"])
        str_record = str(t_record, 'utf-8')
        
        logger.info(f"Decoded message: {str_record}")

        # Convert string message to dictionary
        dict_record = json.loads(str_record)
       
        logger.info(f"JSON loaded: {dict_record}")


        # Generate a filename using the current timestamp in UTC+2
        timestamp = get_utc_plus_2_timestamp()
        # Generate a filename using the timestamp from the dict_record
        file_name = f"Minute/{timestamp}.json"
    
        logger.info(f"Generated file name: {file_name}")

      
        # Write the Pub/Sub message to Google Cloud Storage
        write_to_storage(bucket_name=BUCKET_NAME, file_name=file_name, data=dict_record)
        logger.info(f"Message written to Cloud Storage as {file_name}")

        return "Success"
    except Exception as e:
        logger.exception(f"Error in write_to_database: {e}")
        return "Error"
