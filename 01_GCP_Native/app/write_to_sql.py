import os
import logging
import base64
import json
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
# ORM
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
# Google Cloud Services
import functions_framework
from google.cloud.sql.connector import Connector
# Custom Logging
from loguru import logger
from .logging_config import configure_logger
# Import the Pydantic schema
from .schemas import Record

# Configure logging
configure_logger()

# Local Development
load_dotenv("./secrets/.env.local")

# Environment variables
logger.debug("Attempting to load environment variables!")
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
logger.debug("Done loading environment variables!")

# Instance connection name to connect to DB
INSTANCE_CONNECTION_NAME = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"

# Raise an error if critical environment variables are missing
if not PROJECT_ID or not REGION or not INSTANCE_NAME or not DB_USER or not DB_PASS or not DB_NAME:
    logger.critical("Critical environment variables are missing! Exiting program.")
    raise EnvironmentError("Environment variables must be set.")

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def write_to_database(cloud_event):
    """Triggered by Cloud Pub/Sub and writes data to the database.

    Args:
        cloud_event (CloudEvent): Event containing data to be processed.
    """
    logger.info("Cloud event triggered.")
    logger.debug(f"Cloud Event: {cloud_event}")

    def ingest_to_db(str_record):
        logger.info("Ingest to DB started")

        # Initialize the Connector for Google Cloud SQL
        connector = Connector()

        try:
            # Load the JSON string
            logger.debug(f"Raw string before JSON load: {str_record}")
            dict_record = json.loads(str_record)
            logger.debug(f"JSON loaded: {dict_record}")

            # Validate data using Pydantic schema
            record = Record(**dict_record)
            logger.debug(f"Validated record: {record}")

            # Convert the timestamp to UTC+2 using a fixed offset
            utc_plus_2 = record.status.timestamp + timedelta(hours=2)
            status = utc_plus_2.strftime('%Y-%m-%d %H:%M:%S')

            # Function to get a connection to the Cloud SQL instance
            def getconn():
                conn = connector.connect(
                    INSTANCE_CONNECTION_NAME,
                    "pymysql",
                    user=DB_USER,
                    password=DB_PASS,
                    db=DB_NAME,
                )
                logger.info(f"Connecting to instance: {INSTANCE_CONNECTION_NAME}")
                return conn

            # Create a connection pool with SQLAlchemy
            pool = create_engine(
                "mysql+pymysql://",
                creator=getconn,
            )
            logger.info("Connection pool created")

            # Connect to the connection pool
            with pool.connect() as db_conn:
                logger.info("Connected to the database")

                # Loop over the data items and insert each one
                for data_item in record.data:
                    # Prepare each dict_record for insertion
                    dict_record = data_item.model_dump()  # Convert to a dict

                    if data_item.date_added:
                        dict_record['date_added'] = data_item.date_added.strftime('%Y-%m-%d %H:%M:%S')

                    if data_item.last_updated:
                        dict_record['last_updated'] = data_item.last_updated.strftime('%Y-%m-%d %H:%M:%S')

                    dict_record['tags'] = json.dumps(data_item.tags)  # Convert list of tags to a JSON string
                    dict_record['platform'] = json.dumps(data_item.platform.model_dump() if data_item.platform else None)  # Handle platform serialization

                    # Access attributes from the QuoteUSD Pydantic model directly
                    usd_quote = data_item.quote.get('USD')  # Get the QuoteUSD object for USD
                    dict_record['price'] = usd_quote.price if usd_quote.price is not None else 0.0
                    dict_record['volume_24h'] = usd_quote.volume_24h if usd_quote.volume_24h is not None else 0.0
                    dict_record['volume_change_24h'] = usd_quote.volume_change_24h if usd_quote.volume_change_24h is not None else 0.0
                    dict_record['percent_change_1h'] = usd_quote.percent_change_1h if usd_quote.percent_change_1h is not None else 0.0
                    dict_record['percent_change_24h'] = usd_quote.percent_change_24h if usd_quote.percent_change_24h is not None else 0.0
                    dict_record['percent_change_7d'] = usd_quote.percent_change_7d if usd_quote.percent_change_7d is not None else 0.0
                    dict_record['percent_change_30d'] = usd_quote.percent_change_30d if usd_quote.percent_change_30d is not None else 0.0
                    dict_record['percent_change_60d'] = usd_quote.percent_change_60d if usd_quote.percent_change_60d is not None else 0.0
                    dict_record['percent_change_90d'] = usd_quote.percent_change_90d if usd_quote.percent_change_90d is not None else 0.0
                    dict_record['market_cap'] = usd_quote.market_cap if usd_quote.market_cap is not None else 0.0
                    dict_record['market_cap_dominance'] = usd_quote.market_cap_dominance if usd_quote.market_cap_dominance is not None else 0.0
                    dict_record['fully_diluted_market_cap'] = usd_quote.fully_diluted_market_cap if usd_quote.fully_diluted_market_cap is not None else 0.0
                    dict_record['tvl'] = usd_quote.tvl if usd_quote.tvl is not None else 0.0

                    # Add the 'status' field
                    dict_record['status'] = status

                    logger.debug(f"Prepared data for insertion: {dict_record}")

                    # Insert data into the coin_cryptos table
                    insert_statement = """
                    INSERT INTO coin_cryptos (
                        status, id, name, symbol, slug, num_market_pairs, date_added, tags, max_supply,
                        circulating_supply, total_supply, infinite_supply, platform, cmc_rank,
                        self_reported_circulating_supply, self_reported_market_cap, tvl_ratio, last_updated,
                        price, volume_24h, volume_change_24h, percent_change_1h, percent_change_24h,
                        percent_change_7d, percent_change_30d, percent_change_60d, percent_change_90d,
                        market_cap, market_cap_dominance, fully_diluted_market_cap, tvl
                    ) VALUES (
                        :status, :id, :name, :symbol, :slug, :num_market_pairs, :date_added, :tags, :max_supply,
                        :circulating_supply, :total_supply, :infinite_supply, :platform, :cmc_rank,
                        :self_reported_circulating_supply, :self_reported_market_cap, :tvl_ratio, :last_updated,
                        :price, :volume_24h, :volume_change_24h, :percent_change_1h, :percent_change_24h,
                        :percent_change_7d, :percent_change_30d, :percent_change_60d, :percent_change_90d,
                        :market_cap, :market_cap_dominance, :fully_diluted_market_cap, :tvl
                    )
                    """

                    # Execute the insertion for each dict_record
                    db_conn.execute(text(insert_statement), dict_record)

                db_conn.commit()  # Commit the transaction once all records are inserted
                logger.info("All data inserted successfully!")

        except SQLAlchemyError as e:
            logger.exception(f"SQLAlchemy Error: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error loading JSON: {e}")
            logger.error(f"Invalid JSON string: {str_record}")
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")

    # Get the message from the event that triggered this run
    t_record = base64.b64decode(cloud_event.data["message"]["data"])
    logger.debug(f"Raw Pub/Sub message: {cloud_event.data['message']['data']}")

    # Make sure that it's formatted as a UTF-8 string
    str_record = str(t_record, 'utf-8')
    logger.debug(f"Formatted message: {str_record}")

    # Start the ingestion process
    ingest_to_db(str_record)
    logger.info("Ingest to DB function completed")

