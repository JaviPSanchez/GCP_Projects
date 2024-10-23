import os
import sqlalchemy
from sqlalchemy import create_engine, text
from google.cloud.sql.connector import Connector
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
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
# Google Cloud SQL connection information
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
logger.debug("Done loading environment variables!")

# Instance connection name
INSTANCE_CONNECTION_NAME = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"

# Raise an error if critical environment variables are missing
if not PROJECT_ID or not REGION or not INSTANCE_NAME or not DB_USER or not DB_PASS or not DB_NAME:
    logger.critical("Critical environment variables are missing! Exiting program.")
    raise EnvironmentError("Environment variables must be set.")

def ingest_to_db():
    logger.info("Ingest to DB started")

    # Initialize the Connector for Google Cloud SQL
    connector = Connector()
    db_conn = None

    try:
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
        pool = sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=getconn,
        )
        logger.info("Connection pool created")

        # Connect to the connection pool and execute queries
        with pool.connect() as db_conn:
            logger.info("Connected to the database")

            # Execute a sample query to show databases and assign result
            result = db_conn.execute(text("SHOW DATABASES;"))
            logger.info("Showing Databases...")

            # Fetch and display the databases
            databases = result.fetchall()
            for db in databases:
                logger.debug(f"Database: {db[0]}")
            
            # Create the coin_cryptos table if it doesn't exist
            create_table_coin_cryptos = """
            CREATE TABLE IF NOT EXISTS coin_cryptos (
                auto_id INT PRIMARY KEY AUTO_INCREMENT,
                status DATETIME,
                id INT,
                name VARCHAR(255),
                symbol VARCHAR(10),
                slug VARCHAR(100),
                num_market_pairs INT,
                date_added DATETIME,
                tags JSON,
                max_supply BIGINT,
                circulating_supply BIGINT,
                total_supply BIGINT,
                infinite_supply BOOLEAN,
                platform VARCHAR(255),
                cmc_rank INT,
                self_reported_circulating_supply DECIMAL(30, 10) NULL,
                self_reported_market_cap DECIMAL(30, 10) NULL,
                tvl_ratio DECIMAL(30, 10) NULL,
                last_updated DATETIME,
                price DECIMAL(30, 10) NULL,
                volume_24h DECIMAL(30, 10) NULL,
                volume_change_24h DECIMAL(30, 10) NULL,
                percent_change_1h DECIMAL(30, 10) NULL,
                percent_change_24h DECIMAL(30, 10) NULL,
                percent_change_7d DECIMAL(30, 10) NULL,
                percent_change_30d DECIMAL(30, 10) NULL,
                percent_change_60d DECIMAL(30, 10) NULL,
                percent_change_90d DECIMAL(30, 10) NULL,
                market_cap DECIMAL(30, 10) NULL,
                market_cap_dominance DECIMAL(5, 2) NULL,
                fully_diluted_market_cap DECIMAL(30, 10) NULL,
                tvl DECIMAL(30, 10) NULL
            );
            """
            db_conn.execute(text(create_table_coin_cryptos))
            logger.info("table coin_cryptos created or already exists.")
            
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error occurred: {str(e)}")

    except Exception as e:
        logger.error(f"General error occurred: {str(e)}")

    finally:
        # Ensure db_conn is closed if it was opened
        if db_conn is not None:
            db_conn.close()
            logger.info("Database connection closed")

        # Properly close the connector to prevent aiohttp errors
        connector.close()
        logger.info("Connector closed")

# Start the ingestion process
ingest_to_db()
logger.info("Ingest to DB function completed")
