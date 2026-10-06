import os
import sys
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
from src.logger import logging
from src.exception import CustomException

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "personal_finance_db")

def seed_database():
    try:
        logging.info("Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        db.accounts.delete_many({})
        db.transactions.delete_many({})
        db.budgets.delete_many({})

        accounts_data = [
            {"accountId": "ACC001", "userId": "USR101", "accountType": "checking", "balance": 5200.50},
            {"accountId": "ACC002", "userId": "USR101", "accountType": "savings", "balance": 18500.00},
            {"accountId": "ACC003", "userId": "USR101", "accountType": "credit", "balance": 1200.00}
        ]
        db.accounts.insert_many(accounts_data)

        budgets_data = [
            {"userId": "USR101", "category": "food", "monthlyLimit": 600.0, "month": "2026-10"},
            {"userId": "USR101", "category": "travel", "monthlyLimit": 300.0, "month": "2026-10"},
            {"userId": "USR101", "category": "shopping", "monthlyLimit": 400.0, "month": "2026-10"},
            {"userId": "USR101", "category": "bills", "monthlyLimit": 800.0, "month": "2026-10"}
        ]
        db.budgets.insert_many(budgets_data)

        categories = ["food", "travel", "shopping", "bills"]
        merchants = {
            "food": ["Starbucks", "Chipotle", "Whole Foods", "McDonalds", "Subway"],
            "travel": ["Uber", "Lyft", "Shell Gas", "Chevron", "Delta Air"],
            "shopping": ["Amazon", "Target", "Walmart", "Best Buy", "Zara"],
            "bills": ["Electric Co", "Water Dept", "Internet Provider", "Netflix", "Gym Membership"]
        }
        account_ids = ["ACC001", "ACC002", "ACC003"]
        start_date = datetime(2026, 9, 1)

        transactions_data = []
        for i in range(1, 210):  
            cat = random.choice(categories)
            merchant = random.choice(merchants[cat])
            txn_type = "debit" if random.random() > 0.05 else "credit" 
            amount = round(random.uniform(5.0, 250.0), 2) if txn_type == "debit" else round(random.uniform(500.0, 2000.0), 2)
            txn_date = (start_date + timedelta(days=random.randint(0, 35))).strftime("%Y-%m-%d")

            transactions_data.append({
                "txnId": f"TXN{i:04d}",
                "accountId": random.choice(account_ids),
                "amount": amount,
                "type": txn_type,
                "category": cat,
                "merchant": merchant,
                "date": txn_date
            })

        db.transactions.insert_many(transactions_data)

        logging.info(f"Database successfully seeded with {len(transactions_data)} transactions.")
        print(f"Successfully seeded database '{DB_NAME}' with {len(transactions_data)} transactions!")

        client.close()

    except Exception as e:
        logging.error("Error occurred while seeding database")
        raise CustomException(e, sys)








if __name__ == "__main__":
    seed_database()