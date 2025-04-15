import json
from flask import Flask, request
from payments_db import init_db, find_matching_payment, is_subscription_active, mark_payment_paid

app = Flask(__name__)
init_db()

@app.route("/payment", methods=["POST"])
def handle_payment():
    try:
        data = request.get_json()
        print("Received data:", data)

        for user_id, info in data.items():
            days = info.get("days")
            amount = info.get("amount")
            user_id = str(user_id)

            print(f"Finding payment for user {user_id}...")
            payment = find_matching_payment(float(amount))

            if payment:
                print(f"Payment found! Activating subscription for user {user_id}.")
                mark_payment_paid(payment[0])  # payment_id
                return {"status": "success"}, 200
            else:
                print("No matching payment found.")
                return {"status": "no match"}, 404

    except Exception as e:
        print("Error:", e)
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
