"""
Миграция: добавление поля для отслеживания использования пробного периода

Новое поле в users:
- trial_used: использовал ли пользователь пробный период (3 дня за 10 руб)

Запуск:
    python -m migrations.add_trial_used
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
    print(f"Running migration: add_trial_used")
    print(f"Database: {settings.database_url}")
    print()

    try:
        async with engine.begin() as conn:
            # === Таблица users ===
            print("Migrating table 'users':")

            await add_column_if_not_exists(
                conn, "users", "trial_used",
                "BOOLEAN DEFAULT 0 NOT NULL"
            )

            print()
            print("Migration completed successfully!")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_migration())
