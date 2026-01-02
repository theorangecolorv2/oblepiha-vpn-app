#!/usr/bin/env python3
"""
Скрипт для установки лимита трафика 500 ГБ всем пользователям Облепихи в Remnawave.

Находит всех пользователей с username начинающимся на "oblepiha_"
и устанавливает им лимит трафика если он не был установлен (= 0).

Запуск:
    cd backend
    python set_traffic_limits.py

    # Только посмотреть без изменений:
    python set_traffic_limits.py --dry-run
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.insert(0, str(Path(__file__).parent))

from app.services.remnawave import get_remnawave_service, RemnawaveError
from app.config import get_settings


async def set_traffic_limits(dry_run: bool = False):
    """Установить лимит трафика всем пользователям oblepiha_*"""
    settings = get_settings()
    remnawave = get_remnawave_service()

    traffic_limit = settings.remnawave_traffic_limit_bytes
    traffic_limit_gb = traffic_limit / (1024 ** 3)

    print(f"🔧 Лимит трафика: {traffic_limit} байт ({traffic_limit_gb:.0f} ГБ)")
    print(f"📋 Стратегия сброса: {settings.remnawave_traffic_reset_strategy}")
    if dry_run:
        print("⚠️  DRY RUN - изменения НЕ будут применены\n")
    print()

    # Получаем всех пользователей (пагинация)
    all_users = []
    start = 0
    size = 100

    print("📥 Загружаем пользователей из Remnawave...")

    while True:
        try:
            users = await remnawave.get_all_users(start=start, size=size)
            if not users:
                break
            all_users.extend(users)
            print(f"   Загружено: {len(all_users)} пользователей...")
            start += size
        except RemnawaveError as e:
            print(f"❌ Ошибка при получении пользователей: {e}")
            return

    print(f"\n✅ Всего пользователей: {len(all_users)}")

    # Фильтруем только oblepiha_*
    oblepiha_users = [u for u in all_users if u.get("username", "").startswith("oblepiha_")]
    print(f"🌿 Пользователей Облепихи: {len(oblepiha_users)}")

    # Находим тех, у кого лимит = 0 (безлимит)
    users_without_limit = [u for u in oblepiha_users if u.get("trafficLimitBytes", 0) == 0]
    print(f"⚠️  Без лимита трафика: {len(users_without_limit)}")

    if not users_without_limit:
        print("\n✅ Все пользователи уже имеют лимит трафика!")
        return

    print(f"\n{'='*60}")
    print("Пользователи без лимита:")
    print(f"{'='*60}")

    for user in users_without_limit:
        username = user.get("username", "???")
        uuid = user.get("uuid", "???")
        status = user.get("status", "???")
        print(f"  • {username} ({status}) - {uuid[:8]}...")

    print(f"\n{'='*60}")

    if dry_run:
        print("\n⚠️  DRY RUN завершён. Запустите без --dry-run для применения изменений.")
        return

    # Обновляем лимит трафика
    print(f"\n🚀 Устанавливаем лимит {traffic_limit_gb:.0f} ГБ...")

    success_count = 0
    error_count = 0

    for user in users_without_limit:
        username = user.get("username", "???")
        uuid = user.get("uuid")

        if not uuid:
            print(f"  ⚠️  {username}: нет UUID, пропускаем")
            continue

        try:
            await remnawave.update_user_traffic_limit(uuid)
            print(f"  ✅ {username}: лимит установлен")
            success_count += 1
        except RemnawaveError as e:
            print(f"  ❌ {username}: ошибка - {e}")
            error_count += 1

        # Небольшая задержка чтобы не перегружать API
        await asyncio.sleep(0.1)

    print(f"\n{'='*60}")
    print(f"✅ Успешно обновлено: {success_count}")
    if error_count:
        print(f"❌ Ошибок: {error_count}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Установить лимит трафика 500 ГБ пользователям Облепихи"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать пользователей без изменений"
    )
    args = parser.parse_args()

    asyncio.run(set_traffic_limits(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
