"""
Сервис для отправки уведомлений пользователям через Telegram Bot API.
Используется для уведомлений об оплате из webhook и scheduler.
"""

import logging
from typing import Optional
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


async def _send_telegram_message(
    telegram_id: int,
    text: str,
    keyboard: Optional[dict] = None,
) -> bool:
    """
    Базовая функция отправки сообщения в Telegram.

    Args:
        telegram_id: Telegram ID пользователя
        text: Текст сообщения (HTML)
        keyboard: Inline клавиатура (опционально)

    Returns:
        True если сообщение отправлено успешно
    """
    settings = get_settings()
    url = TELEGRAM_API_URL.format(token=settings.telegram_bot_token)

    payload = {
        "chat_id": telegram_id,
        "text": text,
        "parse_mode": "HTML",
    }

    if keyboard:
        payload["reply_markup"] = keyboard

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)

            if response.status_code == 200:
                return True
            else:
                logger.error(f"Failed to send message to {telegram_id}: {response.text}")
                return False

    except Exception as e:
        logger.error(f"Error sending message to {telegram_id}: {e}")
        return False


def _get_app_keyboard() -> dict:
    """Клавиатура с кнопкой открытия Mini App"""
    settings = get_settings()
    return {
        "inline_keyboard": [[
            {
                "text": "🍊 Открыть Облепиха VPN",
                "web_app": {"url": settings.frontend_url}
            }
        ]]
    }


async def send_payment_success_message(telegram_id: int, days: int, tariff_name: str) -> bool:
    """
    Отправить сообщение об успешной оплате пользователю.

    Args:
        telegram_id: Telegram ID пользователя
        days: Количество дней подписки
        tariff_name: Название тарифа

    Returns:
        True если сообщение отправлено успешно
    """
    message = (
        "✅ <b>Оплата прошла успешно!</b>\n\n"
        f"📦 Тариф: <b>{tariff_name}</b>\n"
        f"📅 Добавлено дней: <b>{days}</b>\n\n"
        "Ваша подписка активирована. Приятного пользования!\n\n"
        "💡 <i>Если дни не отобразились в приложении — просто перезапустите его.</i>"
    )

    result = await _send_telegram_message(telegram_id, message, _get_app_keyboard())
    if result:
        logger.info(f"Payment success message sent to {telegram_id}")
    return result


async def send_expiration_warning(
    telegram_id: int,
    hours_left: int,
    has_auto_renew: bool = False,
    card_last4: Optional[str] = None,
) -> bool:
    """
    Отправить уведомление об истечении подписки.

    Args:
        telegram_id: Telegram ID пользователя
        hours_left: Часов до истечения
        has_auto_renew: Включено ли автопродление
        card_last4: Последние 4 цифры карты (если есть)

    Returns:
        True если сообщение отправлено успешно
    """
    if has_auto_renew and card_last4:
        # Уведомление для пользователей с автопродлением
        message = (
            "⏰ <b>Завтра будет автоматически продлена ваша подписка.</b>\n\n"
            f"💳 С карты *{card_last4} будет списано <b>199 ₽</b>.\n\n"
            "💡 Вы можете отключить автопродление в приложении."
        )
    else:
        # Уведомление для обычных пользователей
        if hours_left <= 24:
            time_text = "менее 24 часов"
        else:
            time_text = f"около {hours_left} часов"

        message = (
            "⏰ <b>Ваша подписка Облепиха VPN скоро истекает!</b>\n\n"
            f"📅 Осталось {time_text}.\n\n"
            "💡 Продлите подписку сейчас, чтобы не потерять доступ к VPN."
        )

    result = await _send_telegram_message(telegram_id, message, _get_app_keyboard())
    if result:
        logger.info(f"Expiration warning sent to {telegram_id}, hours_left={hours_left}")
    return result


async def send_auto_renew_success(
    telegram_id: int,
    days: int,
    amount: int,
    card_last4: Optional[str] = None,
) -> bool:
    """
    Отправить уведомление об успешном автопродлении.

    Args:
        telegram_id: Telegram ID пользователя
        days: Количество добавленных дней
        amount: Сумма списания в рублях
        card_last4: Последние 4 цифры карты

    Returns:
        True если сообщение отправлено успешно
    """
    card_info = f" *{card_last4}" if card_last4 else ""

    message = (
        "✅ <b>Подписка автоматически продлена!</b>\n\n"
        f"📅 Добавлено дней: <b>{days}</b>\n"
        f"💳 Списано{card_info}: <b>{amount} ₽</b>\n\n"
        "Приятного пользования!"
    )

    result = await _send_telegram_message(telegram_id, message, _get_app_keyboard())
    if result:
        logger.info(f"Auto-renew success message sent to {telegram_id}")
    return result


async def send_auto_renew_failed(
    telegram_id: int,
    reason: str,
    card_last4: Optional[str] = None,
) -> bool:
    """
    Отправить уведомление об ошибке автопродления.

    Args:
        telegram_id: Telegram ID пользователя
        reason: Причина ошибки
        card_last4: Последние 4 цифры карты

    Returns:
        True если сообщение отправлено успешно
    """
    card_info = f" *{card_last4}" if card_last4 else ""

    # Человекопонятные причины ошибок
    reason_messages = {
        "insufficient_funds": "недостаточно средств на карте",
        "card_expired": "срок действия карты истёк",
        "permission_revoked": "разрешение на автоплатежи отозвано в банке",
        "payment_method_not_available": "способ оплаты недоступен",
    }

    reason_text = reason_messages.get(reason, f"ошибка оплаты ({reason})")

    message = (
        "❌ <b>Не удалось продлить подписку автоматически</b>\n\n"
        f"💳 Карта{card_info}\n"
        f"📝 Причина: {reason_text}\n\n"
        "Пожалуйста, продлите подписку вручную или обновите способ оплаты."
    )

    result = await _send_telegram_message(telegram_id, message, _get_app_keyboard())
    if result:
        logger.info(f"Auto-renew failed message sent to {telegram_id}, reason={reason}")
    return result


async def send_subscription_expired(telegram_id: int) -> bool:
    """
    Отправить уведомление об истечении подписки.

    Args:
        telegram_id: Telegram ID пользователя

    Returns:
        True если сообщение отправлено успешно
    """
    message = (
        "⚠️ <b>Ваша подписка Облепиха VPN истекла</b>\n\n"
        "VPN больше не работает. Продлите подписку, чтобы продолжить пользоваться."
    )

    result = await _send_telegram_message(telegram_id, message, _get_app_keyboard())
    if result:
        logger.info(f"Subscription expired message sent to {telegram_id}")
    return result


async def send_auto_renew_disabled(
    telegram_id: int,
    card_last4: Optional[str] = None,
) -> bool:
    """
    Отправить уведомление об автоматическом отключении автопродления
    после нескольких неудачных попыток списания.

    Args:
        telegram_id: Telegram ID пользователя
        card_last4: Последние 4 цифры карты

    Returns:
        True если сообщение отправлено успешно
    """
    card_info = f" *{card_last4}" if card_last4 else ""

    message = (
        "🔕 <b>Автопродление отключено</b>\n\n"
        f"Не удалось списать средства с карты{card_info} несколько раз подряд.\n\n"
        "Автопродление было автоматически отключено, чтобы не беспокоить вас.\n\n"
        "💡 Вы можете продлить подписку вручную или включить автопродление снова в приложении."
    )

    result = await _send_telegram_message(telegram_id, message, _get_app_keyboard())
    if result:
        logger.info(f"Auto-renew disabled message sent to {telegram_id}")
    return result

