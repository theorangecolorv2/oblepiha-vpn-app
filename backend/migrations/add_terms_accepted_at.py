"""
Миграция: добавление поля terms_accepted_at в таблицу users

Запуск:
    python -m migrations.add_terms_accepted_at
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


async def run_migration():
    """Выполняет миграцию"""
    settings = get_settings()
    print(f"Running migration: add_terms_accepted_at")
    print(f"Database: {settings.database_url}")
    
    try:
        async with engine.begin() as conn:
            # Проверяем, существует ли уже колонка
            result = await conn.execute(text("""
                SELECT COUNT(*) as cnt 
                FROM pragma_table_info('users') 
                WHERE name='terms_accepted_at'
            """))
            row = result.fetchone()
            
            if row and row[0] > 0:
                print("✓ Column 'terms_accepted_at' already exists, skipping migration")
                return
            
            # Добавляем колонку
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN terms_accepted_at DATETIME NULL
            """))
            print("✓ Column 'terms_accepted_at' added successfully")
            
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_migration())

