"""
Сервис для отправки уведомлений пользователям через Telegram Bot API.
Используется для уведомлений об оплате из webhook.
"""

import logging
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


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
    settings = get_settings()
    
    message = (
        "✅ <b>Оплата прошла успешно!</b>\n\n"
        f"📦 Тариф: <b>{tariff_name}</b>\n"
        f"📅 Добавлено дней: <b>{days}</b>\n\n"
        "Ваша подписка активирована. Приятного пользования! 🎉\n\n"
        "💡 <i>Если дни не отобразились в приложении — просто перезапустите его.</i>"
    )
    
    # Кнопка для открытия Mini App
    keyboard = {
        "inline_keyboard": [[
            {
                "text": "🍊 Открыть Облепиха VPN",
                "web_app": {"url": settings.frontend_url}
            }
        ]]
    }
    
    url = TELEGRAM_API_URL.format(token=settings.telegram_bot_token)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "chat_id": telegram_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "reply_markup": keyboard
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.info(f"Payment success message sent to {telegram_id}")
                return True
            else:
                logger.error(f"Failed to send message to {telegram_id}: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Error sending message to {telegram_id}: {e}")
        return False

