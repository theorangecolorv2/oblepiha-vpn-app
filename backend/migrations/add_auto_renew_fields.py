"""
Миграция: добавление полей для автопродления подписок

Новые поля в users:
- auto_renew_enabled: включено ли автопродление
- payment_method_id: ID сохранённого способа оплаты в YooKassa
- card_last4: последние 4 цифры карты (для отображения)
- card_brand: бренд карты (Visa, Mastercard, Mir)
- last_notification_sent_at: время последнего уведомления об истечении

Новые поля в payments:
- payment_method_id: ID способа оплаты (для автоплатежей)
- is_auto_payment: флаг автоплатежа
- auto_payment_attempt: номер попытки автоплатежа

Запуск:
    python -m migrations.add_auto_renew_fields
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import engine
from app.config import get_settings


async def add_column_if_not_exists(conn, table: str, column: str, column_type: str):
    """Добавить колонку если её нет"""
    result = await conn.execute(text(f"""
        SELECT COUNT(*) as cnt
        FROM pragma_table_info('{table}')
        WHERE name='{column}'
    """))
    row = result.fetchone()

    if row and row[0] > 0:
        print(f"  ✓ Column '{table}.{column}' already exists, skipping")
        return False

    await conn.execute(text(f"""
        ALTER TABLE {table}
        ADD COLUMN {column} {column_type}
    """))
    print(f"  ✓ Column '{table}.{column}' added successfully")
    return True


async def run_migration():
    """Выполняет миграцию"""
    settings = get_settings()
    print(f"Running migration: add_auto_renew_fields")
    print(f"Database: {settings.database_url}")
    print()

    try:
        async with engine.begin() as conn:
            # === Таблица users ===
            print("Migrating table 'users':")

            await add_column_if_not_exists(
                conn, "users", "auto_renew_enabled",
                "BOOLEAN DEFAULT 0 NOT NULL"
            )

            await add_column_if_not_exists(
                conn, "users", "payment_method_id",
                "VARCHAR(64) NULL"
            )

            await add_column_if_not_exists(
                conn, "users", "card_last4",
                "VARCHAR(4) NULL"
            )

            await add_column_if_not_exists(
                conn, "users", "card_brand",
                "VARCHAR(32) NULL"
            )

            await add_column_if_not_exists(
                conn, "users", "last_notification_sent_at",
                "DATETIME NULL"
            )

            print()

            # === Таблица payments ===
            print("Migrating table 'payments':")

            await add_column_if_not_exists(
                conn, "payments", "payment_method_id",
                "VARCHAR(64) NULL"
            )

            await add_column_if_not_exists(
                conn, "payments", "is_auto_payment",
                "BOOLEAN DEFAULT 0 NOT NULL"
            )

            await add_column_if_not_exists(
                conn, "payments", "auto_payment_attempt",
                "INTEGER DEFAULT 0 NOT NULL"
            )

            print()
            print("Migration completed successfully!")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_migration())
