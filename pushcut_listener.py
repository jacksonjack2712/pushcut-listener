from flask import Flask, request
import json
from datetime import datetime, timedelta

app = Flask(__name__)

ALLOWED_USERS_FILE = 'allowed_users.json'
PENDING_PAYMENTS_FILE = 'pending_payments.txt'

@app.route('/payment', methods=['POST'])
def handle_payment():
    try:
        with open(PENDING_PAYMENTS_FILE, 'r', encoding='utf-8') as f:
            pending = json.load(f)
    except FileNotFoundError:
        pending = {}

    try:
        with open(ALLOWED_USERS_FILE, 'r', encoding='utf-8') as f:
            allowed = json.load(f)
    except FileNotFoundError:
        allowed = {}

    for user_id, data in list(pending.items()):
        days = data['days']
        expiry = datetime.now() + timedelta(days=days)
        allowed[user_id] = expiry.strftime("%Y-%m-%d %H:%M:%S")
        del pending[user_id]

    with open(ALLOWED_USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(allowed, f, ensure_ascii=False, indent=2)
    with open(PENDING_PAYMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

    return "[OK] Подписка выдана"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
