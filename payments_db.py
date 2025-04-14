import sqlite3
from datetime import datetime, timedelta

DB_NAME = "payments.db"

# Создание таблиц

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Таблица заявок на оплату
    c.execute('''
    CREATE TABLE IF NOT EXISTS pending_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        duration INTEGER,
        created_at TEXT,
        status TEXT
    )
    ''')

    # Таблица подписок
    c.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        start_date TEXT,
        end_date TEXT
    )
    ''')

    conn.commit()
    conn.close()

# Добавить заявку на оплату

def add_pending_payment(user_id, amount, duration):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("INSERT INTO pending_payments (user_id, amount, duration, created_at, status) VALUES (?, ?, ?, ?, ?)",
              (user_id, amount, duration, now, "pending"))
    conn.commit()
    conn.close()

# Активировать подписку

def activate_subscription(user_id, duration):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    start_date = datetime.now()
    end_date = start_date + timedelta(days=duration)
    c.execute("REPLACE INTO subscriptions (user_id, start_date, end_date) VALUES (?, ?, ?)",
              (user_id, start_date.isoformat(), end_date.isoformat()))
    conn.commit()
    conn.close()

# Проверка активной подписки

def is_subscription_active(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT end_date FROM subscriptions WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return datetime.fromisoformat(row[0]) > datetime.now()
    return False

# Найти подходящую заявку по сумме

def find_matching_payment(amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now()
    c.execute("SELECT id, user_id, duration, created_at FROM pending_payments WHERE amount = ? AND status = 'pending'", (amount,))
    rows = c.fetchall()
    for row in rows:
        created_at = datetime.fromisoformat(row[3])
        if abs((now - created_at).total_seconds()) <= 600:
            conn.close()
            return row[0], row[1], row[2]  # id, user_id, duration
    conn.close()
    return None

# Пометить заявку как оплаченная

def mark_payment_paid(payment_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE pending_payments SET status = 'paid' WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()

# Очистка просроченных заявок (по желанию можно вызывать периодически)

def expire_old_pending():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("UPDATE pending_payments SET status = 'expired' WHERE status = 'pending' AND datetime(created_at) < datetime(?, '-10 minutes')", (now,))
    conn.commit()
    conn.close()

# При первом запуске
if __name__ == "__main__":
    init_db()
    print("Database initialized.")
