from datetime import datetime, timedelta
from database import get_subscription, set_subscription

TARIFFS = {
    "week": {"price": 2, "days": 7},
    "month": {"price": 5, "days": 30},
    "6months": {"price": 25, "days": 182},
    "year": {"price": 40, "days": 365},
}

def check_subscription(user_id):
    sub_type, end_date = get_subscription(user_id)
    if not sub_type or not end_date:
        return False
    return datetime.strptime(end_date, "%Y-%m-%d") >= datetime.now()

def activate_subscription(user_id, sub_type):
    days = TARIFFS[sub_type]["days"]
    _, end_date = get_subscription(user_id)
    now = datetime.now()
    if end_date and datetime.strptime(end_date, "%Y-%m-%d") > now:
        new_end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=days)
    else:
        new_end = now + timedelta(days=days)
    set_subscription(user_id, sub_type, new_end.strftime("%Y-%m-%d"))
