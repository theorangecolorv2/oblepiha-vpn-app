"""
Обработчики команд Telegram бота
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart, CommandObject

from app.config import get_settings

logger = logging.getLogger(__name__)
router = Router()

settings = get_settings()

# URL Mini App
MINI_APP_URL = settings.frontend_url


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой открытия Mini App"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🍊 Открыть Облепиха VPN",
            web_app=WebAppInfo(url=MINI_APP_URL)
        )]
    ])


@router.message(CommandStart(deep_link=True))
async def cmd_start_with_param(message: Message, command: CommandObject):
    """Обработка /start с параметром (например, после оплаты)"""
    param = command.args
    
    if param == "payment_success":
        # После успешной оплаты
        await message.answer(
            "✅ <b>Оплата прошла успешно!</b>\n\n"
            "Ваша подписка активирована. Приятного пользования! 🎉\n\n"
            "💡 <i>Если дни не отобразились — просто перезапустите приложение.</i>",
            reply_markup=get_start_keyboard(),
            parse_mode="HTML"
        )
    else:
        # Неизвестный параметр — показываем обычное приветствие
        await cmd_start(message)


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработка команды /start"""
    user_name = message.from_user.first_name or "друг"
    
    await message.answer(
        f"👋 Привет, <b>{user_name}</b>!\n\n"
        "🍊 <b>Облепиха VPN</b> — быстрый и надёжный VPN для всей семьи.\n\n"
        "• Безлимит устройств\n"
        "• 500 ГБ трафика в месяц\n"
        "• Простая настройка\n\n"
        "Нажми кнопку ниже, чтобы начать 👇",
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text)
async def any_message(message: Message):
    """Ответ на любое текстовое сообщение"""
    await message.answer(
        "🍊 Для управления подпиской используй приложение 👇",
        reply_markup=get_start_keyboard()
    )

