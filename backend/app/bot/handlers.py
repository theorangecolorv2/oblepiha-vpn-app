"""
Обработчики команд Telegram бота
"""

import logging
import random
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart, CommandObject
from aiogram.enums import ChatMemberStatus
from sqlalchemy import select

from app.config import get_settings
from app.database import async_session_maker
from app.models.user import User
from app.services.remnawave import get_remnawave_service

logger = logging.getLogger(__name__)
router = Router()

settings = get_settings()

# Канал для проверки подписки
CHANNEL_USERNAME = "Oblepiha_Channel"

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


def get_referral_keyboard(referral_code: str) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой открытия Mini App с реферальным кодом"""
    app_url = f"{MINI_APP_URL}?ref={referral_code}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🍊 Открыть Облепиха VPN",
            web_app=WebAppInfo(url=app_url)
        )]
    ])


@router.message(CommandStart(deep_link=True))
async def cmd_start_with_param(message: Message, command: CommandObject):
    """Обработка /start с параметром (например, после оплаты или реферальная ссылка)"""
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
    elif param and param.startswith("ref_"):
        # Реферальная ссылка
        referral_code = param[4:]  # Убираем "ref_"
        user_name = message.from_user.first_name or "друг"

        await message.answer(
            f"👋 Привет, <b>{user_name}</b>!\n\n"
            "🍊 Тебя пригласил друг в <b>Облепиха VPN</b> — быстрый и надёжный VPN для всей семьи.\n\n"
            "• Безлимит устройств\n"
            "• 500 ГБ трафика в месяц\n"
            "• Простая настройка\n\n"
            "Нажми кнопку ниже, чтобы начать 👇",
            reply_markup=get_referral_keyboard(referral_code),
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


@router.callback_query(F.data == "check_channel_subscription")
async def check_channel_subscription(callback: CallbackQuery):
    """Проверка подписки на канал и начисление бонуса"""
    user_id = callback.from_user.id
    bot = callback.bot

    try:
        # Проверяем подписку на канал
        member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)

        is_subscribed = member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]

        if not is_subscribed:
            await callback.answer(
                "❌ Вы не подписаны на канал. Подпишитесь и попробуйте снова.",
                show_alert=True
            )
            return

        # Проверяем, получал ли уже бонус
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                await callback.answer(
                    "❌ Пользователь не найден. Откройте приложение для регистрации.",
                    show_alert=True
                )
                return

            if user.channel_bonus_received_at:
                await callback.answer(
                    "ℹ️ Вы уже получили бонус за подписку на канал.",
                    show_alert=True
                )
                return

            # Начисляем бонус: 2-3 дня случайно
            bonus_days = random.randint(2, 3)

            # Обновляем подписку в Remnawave
            if user.remnawave_uuid:
                try:
                    remnawave = get_remnawave_service()
                    updated_user = await remnawave.update_user_expiration(
                        uuid=user.remnawave_uuid,
                        days_to_add=bonus_days
                    )

                    # Обновляем локальную БД
                    new_expire = updated_user.get("expireAt")
                    if new_expire:
                        user.subscription_expires_at = datetime.fromisoformat(
                            new_expire.replace("Z", "+00:00")
                        ).replace(tzinfo=None)
                        user.is_active = True

                except Exception as e:
                    logger.error(f"Failed to update Remnawave subscription for user {user_id}: {e}")
                    await callback.answer(
                        "❌ Ошибка при начислении бонуса. Попробуйте позже.",
                        show_alert=True
                    )
                    return

            # Отмечаем получение бонуса
            user.channel_bonus_received_at = datetime.utcnow()
            await session.commit()

            await callback.answer(
                f"🎉 Вам начислено {bonus_days} дня подписки!",
                show_alert=True
            )

            # Обновляем сообщение: убираем кнопки подписки, меняем текст
            new_text = """👥 <b>Новое: Реферальная программа!</b>

Приглашайте друзей и получайте бонусные дни или деньги. Подробности во вкладке «Рефералы».


🎁 <b>Бонус получен!</b>

Спасибо за подписку на канал! Вам начислено <b>{days} дня</b> подписки.""".format(days=bonus_days)

            new_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🍊 Открыть Облепиха VPN",
                    web_app=WebAppInfo(url=MINI_APP_URL)
                )]
            ])

            try:
                await callback.message.edit_text(
                    text=new_text,
                    reply_markup=new_keyboard,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.warning(f"Failed to edit message after bonus: {e}")

            logger.info(f"Channel bonus granted to user {user_id}: {bonus_days} days")

    except Exception as e:
        logger.error(f"Error checking channel subscription for user {user_id}: {e}")
        await callback.answer(
            "❌ Произошла ошибка. Попробуйте позже.",
            show_alert=True
        )

