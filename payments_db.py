import sqlite3
import json
from datetime import datetime, timezone

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

    # Таблица активных подписок
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            start_date TEXT,
            end_date TEXT
        )
    ''')

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
        return datetime.fromisoformat(row[0]) > datetime.now(timezone.utc)
    return False

# Найти подходящую заявку по сумме
def find_matching_payment(amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now(timezone.utc)

    c.execute("""
        SELECT id, user_id, duration, created_at
        FROM pending_payments
        WHERE amount = ? AND status = 'paid'
    """, (amount,))
    
    rows = c.fetchall()

    for row in rows:
        created_at = datetime.fromisoformat(row[3])
        diff = abs((now - created_at).total_seconds())
        print(f"⏱ now: {now}, created_at: {created_at}, diff: {diff}")
        if diff <= 600:
            print(f"✅ Нашёл запись: {row}")
            conn.close()
            return row[0], row[1], row[2]

    conn.close()
    return None

# Пометить заявку как оплаченную
def mark_payment_paid(payment_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE pending_payments SET status = 'used' WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()

# Добавить новую подписку
def activate_subscription(user_id, duration_days):
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=duration_days)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO subscriptions (user_id, start_date, end_date)
        VALUES (?, ?, ?)
    """, (user_id, now.isoformat(), end.isoformat()))
    conn.commit()
    conn.close()

