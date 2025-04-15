import sqlite3
import json
from datetime import datetime, timedelta, timezone

DB_NAME = "payments.db"

# Создание таблиц
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Таблица заявок на оплату
    c.execute("""
        CREATE TABLE IF NOT EXISTS pending_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            duration INTEGER,
            created_at TEXT,
            status TEXT
        )
    """)

    # Таблица активных подписок
    c.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            start_date TEXT,
            end_date TEXT
        )
    """)

    conn.commit()
    conn.close()

def add_pending_payment(user_id, amount, days):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now(timezone.utc)
    c.execute("""
        INSERT INTO pending_payments (user_id, amount, duration, created_at, status)
        VALUES (?, ?, ?, ?, 'pending')
    """, (user_id, amount, days, now.isoformat()))
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

# Найти подходящую заявку по user_id и сумме
def find_matching_payment(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now(timezone.utc)

    c.execute("""
        SELECT id, user_id, duration, created_at
        FROM pending_payments
        WHERE user_id = ? AND amount = ? AND status = 'paid'
    """, (user_id, amount))

    rows = c.fetchall()
    print("Все строки по сумме, юзеру и статусу:")
    for row in rows:
        print(row)

    for row in rows:
        created_at = datetime.fromisoformat(row[3])
        if abs((now - created_at).total_seconds()) <= 600:
            conn.close()
            return row[0], row[1], row[2]  # id, user_id, duration

    conn.close()
    return None

# Пометить заявку как оплаченную
def mark_payment_paid(payment_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE pending_payments SET status = 'paid' WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()

# Добавить подписку
def add_subscription(user_id, days):
    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=days)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO subscriptions (user_id, start_date, end_date)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
        end_date = excluded.end_date
    """, (user_id, now.isoformat(), end_date.isoformat()))
    conn.commit()
    conn.close()
