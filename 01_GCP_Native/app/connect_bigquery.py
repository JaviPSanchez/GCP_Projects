import os
from dotenv import load_dotenv
from google.cloud import bigquery
# Custom Logging
from loguru import logger
from logging_config import configure_logger

# Configure logging
configure_logger()

# Load environment variables from .env file
load_dotenv("./secrets/.env.local")

# Set the environment variable for Google Application Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./secrets/key_access_sql.json"

# Environment variables
logger.debug("Attempting to load environment variables!")
# Google Cloud Project ID
PROJECT_ID = os.getenv("PROJECT_ID")

logger.debug("Done loading environment variables!")

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# List all datasets in the project
datasets = list(client.list_datasets())  # API call to list datasets

if datasets:
    logger.info(f"Datasets in project {PROJECT_ID}:")
    for dataset in datasets:
        logger.info(f" - {dataset.dataset_id}")

        # List all tables in the dataset
        tables = list(client.list_tables(dataset.dataset_id))
        if tables:
            for table in tables:
                logger.info(f"   * Table: {table.table_id}")

                # Check if the table is 'Cryptos'
                if table.table_id == 'Cryptos':
                    # Run a query to show the content of the Cryptos table
                    query = f"SELECT * FROM `{PROJECT_ID}.{dataset.dataset_id}.Cryptos` LIMIT 1"
                    logger.info(f"Querying the Cryptos table: {query}")
                    
                    # Execute the query
                    query_job = client.query(query)
                    results = query_job.result()  # Wait for the job to complete
                    
                    # Print the results
                    logger.info("Showing the first row from the Cryptos table:")
                    for row in results:
                        logger.info(dict(row))  # Convert each row to a dictionary and log it

        else:
            logger.info(f"   (No tables found in dataset {dataset.dataset_id})")
else:
    logger.info(f"{PROJECT_ID} does not contain any datasets.")
