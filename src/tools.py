import sys
import json
from datetime import datetime
from src.database import get_database
from src.logger import logging
from src.exception import MyCustomException


def get_account_balances(args: dict) -> str:
    try:
        user_id = args.get("userId")
        if not user_id:
            return json.dumps({"status": "error", "message": "userId parameter is required."})
        logging.info(f"Executing get_account_balances for userId: {user_id}")
        db = get_database()
        accounts = list(db.accounts.find(
            {"userId": user_id},
            {"_id": 0, "accountId": 1, "accountType": 1, "balance": 1}
        ))
        
        if not accounts:
            return json.dumps({"status": "error", "message": f"No accounts found for user '{user_id}'"})
        
        return json.dumps({"userId": user_id, "accounts": accounts})
    except Exception as e:
        logging.error(f"Error in get_account_balances: {str(e)}")
        raise MyCustomException(e, sys)


def calculate_category_spending(args: dict) -> str:
    """Compute Tool: Aggregates spending per category inside MongoDB using $group and $sum."""
    try:
        user_id = args.get("userId")
        month = args.get("month") 
        if not user_id or not month:
            return json.dumps({"status": "error", "message": "Both userId and month parameters are required."})

        logging.info(f"Executing calculate_category_spending for user: {user_id}, month: {month}")

        db = get_database()
        
        pipeline = [
            {
                "$match": {
                    "userId": user_id,
                    "type": "debit",
                    "date": {"$regex": f"^{month}"}
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "totalSpent": {"$sum": "$amount"},
                    "transactionCount": {"$sum": 1}
                }
            },
            {"$sort": {"totalSpent": -1}}
        ]
        
        results = list(db.transactions.aggregate(pipeline))
        
        if not results:
            return json.dumps({"status": "success", "message": f"No debit transactions found for user {user_id} in {month}."})

        formatted_summary = [
            {"category": item["_id"], "totalSpent": round(item["totalSpent"], 2), "count": item["transactionCount"]}
            for item in results
        ]
        
        return json.dumps({"userId": user_id, "month": month, "spendingSummary": formatted_summary})
    except Exception as e:
        logging.error(f"Error in calculate_category_spending: {str(e)}")
        raise MyCustomException(e, sys)


def set_category_budget(args: dict) -> str:
    """Write Tool: Sets or updates a monthly budget for a spending category."""
    try:
        user_id = args.get("userId")
        category = args.get("category", "").lower()
        monthly_limit = args.get("monthlyLimit")
        month = args.get("month")

        if not all([user_id, category, monthly_limit, month]):
            return json.dumps({"status": "error", "message": "Missing required fields for budget setting."})

        monthly_limit = float(monthly_limit)
        logging.info(f"Executing set_category_budget: user={user_id}, category={category}, limit={monthly_limit}")

        db = get_database()
        db.budgets.update_one(
            {"userId": user_id, "category": category, "month": month},
            {"$set": {"monthlyLimit": monthly_limit}},
            upsert=True
        )

        return json.dumps({
            "status": "success",
            "message": f"Budget for category '{category}' set to ${monthly_limit:.2f} for month {month}."
        })
    except Exception as e:
        logging.error(f"Error in set_category_budget: {str(e)}")
        raise MyCustomException(e, sys)


def get_current_datetime(args: dict = None) -> str:
    """Live Tool: Returns current live date and time."""
    try:
        logging.info("Executing get_current_datetime live tool")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return json.dumps({"currentDateTime": now})
    except Exception as e:
        logging.error(f"Error in get_current_datetime: {str(e)}")
        raise MyCustomException(e, sys)

TOOLS_MAP = {
    "get_account_balances": get_account_balances,
    "calculate_category_spending": calculate_category_spending,
    "set_category_budget": set_category_budget,
    "get_current_datetime": get_current_datetime,
}


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_account_balances",
            "description": "Retrieves account details and current balances for checking, savings, and credit accounts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "userId": {"type": "string", "description": "The user ID, e.g. USR101"}
                },
                "required": ["userId"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_category_spending",
            "description": "Calculates aggregated category spending totals for a specified month using a database sum pipeline.",
            "parameters": {
                "type": "object",
                "properties": {
                    "userId": {"type": "string", "description": "The user ID, e.g. USR101"},
                    "month": {"type": "string", "description": "Year and month in YYYY-MM format, e.g. 2026-10"}
                },
                "required": ["userId", "month"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_category_budget",
            "description": "Sets or updates a monthly category budget limit in the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "userId": {"type": "string", "description": "The user ID, e.g. USR101"},
                    "category": {"type": "string", "description": "The target category name, e.g. food, travel, shopping, bills"},
                    "monthlyLimit": {"type": "number", "description": "The spending budget limit"},
                    "month": {"type": "string", "description": "Year and month in YYYY-MM format, e.g. 2026-10"}
                },
                "required": ["userId", "category", "monthlyLimit", "month"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Fetches current live system timestamp.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]