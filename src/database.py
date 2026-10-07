import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
from src.logger import logging
from src.exception import MyCustomException

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "personal_finance_db")

_client = None

def get_database():
    global _client
    try:
        if not MONGODB_URI:
            raise ValueError("MONGODB_URI is not set in environment variables.")

        if _client is None:
            logging.info("Connecting to MongoDB cluster...")
            _client = MongoClient(MONGODB_URI)
            
        return _client[DB_NAME]
    except Exception as e:
        logging.error(f"MongoDB connection error: {str(e)}")
        raise MyCustomException(e, sys)

def close_database():
    global _client
    try:
        if _client is not None:
            _client.close()
            _client = None
            logging.info("MongoDB connection closed safely.")
    except Exception as e:
        logging.error(f"Error closing MongoDB connection: {str(e)}")
        raise MyCustomException(e, sys)