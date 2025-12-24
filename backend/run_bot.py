#!/usr/bin/env python3
"""
Запуск Telegram бота Облепиха VPN
"""

import sys
import os

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.bot.bot import run_bot

if __name__ == "__main__":
    run_bot()

