import json
from datetime import datetime, timedelta
from flask import Flask, request
from payments_db import init_db, find_matching_payment, is_subscription_active, activate_subscription

app = Flask(__name__)
init_db()

@app.route("/payment", methods=["POST"])
def handle_payment():
    try:
        data = request.get_json()
        print("Received data:", data)

        for user_id, info in data.items():
            days = info.get("days")
            amount = info.get("amount")  # можно передавать сумму, если хочешь
            user_id = str(user_id)

            print(f"Finding payment for user {user_id}...")
            payment_id = find_matching_payment(int(amount))

            if payment_id:
                print(f"Payment found! Activating subscription for user {user_id}.")
                activate_subscription(user_id, days)
                return {"status": "success"}, 200
            else:
                print("No matching payment found.")
                return {"status": "no match"}, 404
    except Exception as e:
        print("Error:", e)
        return {"status": "error", "message": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
