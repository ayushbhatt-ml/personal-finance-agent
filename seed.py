import os
from pymongo import MongoClient
from dotenv import load_dotenv
from src.logger import logging
from src.exception import CustomException
import sys

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "personal_finance_db")

def seed_database():
    try:
        logging.info("Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        db.users.delete_many({})
        db.accounts.delete_many({})
        db.transactions.delete_many({})
        db.budgets.delete_many({})

        user_id = "USR_101"
        db.users.insert_one({
            "user_id": user_id,
            "name": "Alex Mercer",
            "email": "alex.mercer@example.com"
        })

        accounts_data = [
            {"account_id": "ACC_001", "user_id": user_id, "type": "checking", "balance": 4500.50, "currency": "USD"},
            {"account_id": "ACC_002", "user_id": user_id, "type": "savings", "balance": 12800.00, "currency": "USD"},
            {"account_id": "ACC_003", "user_id": user_id, "type": "credit_card", "balance": -420.75, "currency": "USD"}
        ]
        db.accounts.insert_many(accounts_data)
        transactions_data = [
            {"txn_id": "TXN_1001", "user_id": user_id, "account_id": "ACC_001", "amount": 12.50, "category": "Food", "merchant": "Starbucks", "date": "2026-10-01"},
            {"txn_id": "TXN_1002", "user_id": user_id, "account_id": "ACC_001", "amount": 85.20, "category": "Groceries", "merchant": "Trader Joe's", "date": "2026-10-02"},
            {"txn_id": "TXN_1003", "user_id": user_id, "account_id": "ACC_003", "amount": 45.00, "category": "Entertainment", "merchant": "Netflix", "date": "2026-10-02"},
            {"txn_id": "TXN_1004", "user_id": user_id, "account_id": "ACC_001", "amount": 120.00, "category": "Utilities", "merchant": "Electric Co", "date": "2026-10-03"},
            {"txn_id": "TXN_1005", "user_id": user_id, "account_id": "ACC_001", "amount": 15.00, "category": "Food", "merchant": "Chipotle", "date": "2026-10-04"},
            {"txn_id": "TXN_1006", "user_id": user_id, "account_id": "ACC_002", "amount": 2500.00, "category": "Income", "merchant": "TechCorp Salary", "date": "2026-10-05"},
            {"txn_id": "TXN_1007", "user_id": user_id, "account_id": "ACC_003", "amount": 60.00, "category": "Gas", "merchant": "Shell", "date": "2026-10-05"},
            {"txn_id": "TXN_1008", "user_id": user_id, "account_id": "ACC_001", "amount": 220.00, "category": "Shopping", "merchant": "Amazon", "date": "2026-10-06"}
        ]
        db.transactions.insert_many(transactions_data)

        budgets_data = [
            {"user_id": user_id, "category": "Food", "monthly_limit": 300.00},
            {"user_id": user_id, "category": "Groceries", "monthly_limit": 400.00},
            {"user_id": user_id, "category": "Entertainment", "monthly_limit": 150.00}
        ]
        db.budgets.insert_many(budgets_data)

        logging.info("Database successfully seeded with collections: users, accounts, transactions, budgets.")
        print("Database seeding complete!")

        client.close()

    except Exception as e:
        logging.error("Error occurred while seeding database")
        raise CustomException(e, sys)

if __name__ == "__main__":
    seed_database()