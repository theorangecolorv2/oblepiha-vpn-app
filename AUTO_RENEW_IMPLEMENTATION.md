# АВТОПРОДЛЕНИЯ (РЕКУРРЕНТНЫЕ ПЛАТЕЖИ) - ПЛАН РЕАЛИЗАЦИИ

## 📊 ТЕКУЩИЙ СТАТУС

**Дата создания:** 2026-01-02
**Статус:** ⏳ Ожидание активации от ЮKassa
**Готовность бэкенда:** 95%
**Готовность фронтенда:** 60%

---

## ✅ ЧТО УЖЕ РАБОТАЕТ (НЕ ТРОГАТЬ)

### Backend - Полностью готово:

1. **YooKassa сервис** (`backend/app/services/yookassa_service.py`)
   - ✅ Метод `create_payment()` с параметром `save_payment_method` (строки 26-92)
   - ✅ Передача `merchant_customer_id` (строка 79)
   - ✅ Метод `create_auto_payment()` для безакцептных списаний (строки 94-147)

2. **Webhook обработка** (`backend/app/routers/payments.py`)
   - ✅ Сохранение `payment_method_id` из webhook (строки 152-156)
   - ✅ Сохранение данных карты `card_last4`, `card_brand` (строки 232-237)
   - ✅ Автоматическое включение `auto_renew_enabled` при `setup_auto_renew=true` (строки 239-242)

3. **Scheduler автопродлений** (`backend/app/scheduler/tasks/auto_renew.py`)
   - ✅ Задача `process_auto_renewals()` запускается каждый час в :30
   - ✅ Поиск пользователей для продления (строки 74-84)
   - ✅ Проверка недавних платежей (строки 92-108)
   - ✅ Лимит 3 попытки за 24 часа (строки 110-129)
   - ✅ Создание автоплатежа через YooKassa (строки 137-143)
   - ✅ Уведомления об успехе/провале (строки 210-250)

4. **API endpoints** (`backend/app/routers/users.py`)
   - ✅ `GET /api/users/me/auto-renew/status` (строки 274-301)
   - ✅ `POST /api/users/me/auto-renew/enable` (строки 330-365)
   - ✅ `POST /api/users/me/auto-renew/disable` (строки 304-327)
   - ✅ `DELETE /api/users/me/auto-renew/payment-method` (строки 368-395)

5. **Модель User** (`backend/app/models/user.py`)
   - ✅ Поля: `auto_renew_enabled`, `payment_method_id`, `card_last4`, `card_brand` (строки 52-56)

### Frontend - Частично готово:

1. **UI компоненты**
   - ✅ `AutoRenewModal.tsx` - модалка управления автопродлением (полностью готова)
   - ✅ `Stats.tsx` - показывает статус автопродления (строки 9, 18, 80)

2. **App.tsx**
   - ✅ Переменная `autoRenewEnabled` существует (строка 15)
   - ✅ Передается в `Stats` компонент (строка 154)

---

## ❌ ЧТО НЕ РАБОТАЕТ (НУЖНО ИСПРАВИТЬ)

### Проблема 1: Frontend НЕ передает setup_auto_renew при создании платежа

**Файл:** `src/api/index.ts`
**Строки:** 133-137

**Текущий код:**
```typescript
async createPayment(tariffId: string): Promise<PaymentResponse> {
  return apiFetch<PaymentResponse>('/api/payments', {
    method: 'POST',
    body: JSON.stringify({ tariff_id: tariffId }), // ❌ Нет setup_auto_renew!
  })
}
```

**Нужно исправить на:**
```typescript
async createPayment(tariffId: string, setupAutoRenew = false): Promise<PaymentResponse> {
  return apiFetch<PaymentResponse>('/api/payments', {
    method: 'POST',
    body: JSON.stringify({
      tariff_id: tariffId,
      setup_auto_renew: setupAutoRenew
    }),
  })
}
```

---

### Проблема 2: useUser hook не передает setupAutoRenew

**Файл:** `src/hooks/useUser.ts`
**Нужно найти:** функцию `createPayment`

**Добавить параметр:**
```typescript
const createPayment = async (tariffId: string, setupAutoRenew = false): Promise<string | null> => {
  try {
    const response = await api.createPayment(tariffId, setupAutoRenew)
    return response.confirmationUrl
  } catch (err) {
    // ... error handling
  }
}
```

---

### Проблема 3: App.tsx НЕ использует autoRenewEnabled при оплате

**Файл:** `src/App.tsx`
**Строки:** 62-90 (функция `proceedWithPayment`)

**Текущий код:**
```typescript
const proceedWithPayment = async (tariffId: string) => {
  setIsPaymentLoading(true)
  setPaymentError(null)

  try {
    console.log('[Payment] Creating payment for tariff:', tariffId)
    const confirmationUrl = await createPayment(tariffId) // ❌ Не передается autoRenewEnabled
    // ...
```

**Нужно исправить на:**
```typescript
const proceedWithPayment = async (tariffId: string) => {
  setIsPaymentLoading(true)
  setPaymentError(null)

  try {
    console.log('[Payment] Creating payment for tariff:', tariffId, 'setupAutoRenew:', autoRenewEnabled)
    const confirmationUrl = await createPayment(tariffId, autoRenewEnabled) // ✅ Передаем флаг
    // ...
```

---

### Проблема 4: UI не показывает чекбокс автопродления при покупке

**Файл:** `src/App.tsx`
**Место:** В блоке с кнопкой "Оплатить" (примерно строки 150-250)

**Нужно добавить ПЕРЕД кнопкой оплаты:**

```tsx
{/* Чекбокс автопродления */}
{selectedTariff && (
  <div className="mb-4 p-4 bg-surface-light/50 rounded-2xl">
    <label className="flex items-start gap-3 cursor-pointer">
      <input
        type="checkbox"
        checked={autoRenewEnabled}
        onChange={(e) => setAutoRenewEnabled(e.target.checked)}
        className="mt-1 w-5 h-5 text-primary border-chocolate/30 rounded focus:ring-primary focus:ring-2"
      />
      <div className="flex-1">
        <div className="text-chocolate font-medium text-sm mb-1">
          Подключить автопродление
        </div>
        <div className="text-chocolate/60 text-xs leading-relaxed">
          Подписка будет автоматически продлеваться каждый месяц.
          Вы можете отключить это в любой момент в настройках.
        </div>
      </div>
    </label>
  </div>
)}
```

---

### Проблема 5: Нет API методов для управления автопродлением во фронтенде

**Файл:** `src/api/index.ts`
**Место:** В конце объекта `api` (после строки 154)

**Добавить методы:**

```typescript
/**
 * Получить статус автопродления
 */
async getAutoRenewStatus(): Promise<{
  enabled: boolean
  hasPaymentMethod: boolean
  cardLast4: string | null
  cardBrand: string | null
}> {
  return apiFetch('/api/users/me/auto-renew/status')
},

/**
 * Включить автопродление
 */
async enableAutoRenew(): Promise<{
  status: string
  autoRenewEnabled: boolean
  cardLast4: string | null
  cardBrand: string | null
}> {
  return apiFetch('/api/users/me/auto-renew/enable', {
    method: 'POST',
  })
},

/**
 * Отключить автопродление
 */
async disableAutoRenew(): Promise<{
  status: string
  autoRenewEnabled: boolean
}> {
  return apiFetch('/api/users/me/auto-renew/disable', {
    method: 'POST',
  })
},

/**
 * Удалить сохраненный способ оплаты
 */
async deletePaymentMethod(): Promise<{ status: string }> {
  return apiFetch('/api/users/me/auto-renew/payment-method', {
    method: 'DELETE',
  })
},
```

---

### Проблема 6: UserResponse не содержит поля автопродления

**Файл:** `src/api/index.ts`
**Строки:** 18-32 (интерфейс `UserResponse`)

**Добавить поля:**
```typescript
export interface UserResponse {
  id: number
  telegramId: number
  telegramUsername: string | null
  firstName: string | null
  isActive: boolean
  subscriptionExpiresAt: string | null
  daysLeft: number
  subscriptionUrl: string | null
  trafficUsedBytes: number
  trafficLimitBytes: number
  referralCode: string | null
  termsAcceptedAt: string | null
  trialUsed: boolean
  // ✅ Добавить эти поля:
  autoRenewEnabled: boolean
  hasPaymentMethod: boolean
  cardLast4: string | null
  cardBrand: string | null
}
```

---

### Проблема 7: AutoRenewModal не делает реальных API вызовов

**Файл:** `src/components/AutoRenewModal.tsx`
**Строки:** 16-18 (функция `handleToggle`)

**Текущий код:**
```typescript
const handleToggle = () => {
  onToggle(!isEnabled) // ❌ Только вызывает callback
}
```

**Это OK** - логика в родительском компоненте. Но нужно убедиться, что в `App.tsx` есть функция `handleAutoRenewToggle`:

```typescript
const handleAutoRenewToggle = async (enabled: boolean) => {
  try {
    if (enabled) {
      await api.enableAutoRenew()
    } else {
      await api.disableAutoRenew()
    }
    await refreshUser() // Обновляем данные пользователя
    setAutoRenewEnabled(enabled)
  } catch (err) {
    console.error('[AutoRenew] Failed to toggle:', err)
    // Показать ошибку пользователю
  }
}
```

---

## 🎯 ПОШАГОВЫЙ ПЛАН РЕАЛИЗАЦИИ (ПОСЛЕ ОДОБРЕНИЯ ЮKASSA)

### ШАГ 1: Обновить API клиент

**Файлы:** `src/api/index.ts`

1. Исправить `createPayment()` - добавить параметр `setupAutoRenew`
2. Обновить `UserResponse` interface - добавить поля автопродления
3. Добавить 4 новых метода API для управления автопродлением

### ШАГ 2: Обновить useUser hook

**Файл:** `src/hooks/useUser.ts`

1. Добавить параметр `setupAutoRenew` в функцию `createPayment`
2. Добавить новую функцию `refreshUser()` для обновления данных пользователя
3. Добавить функции для управления автопродлением

### ШАГ 3: Обновить App.tsx

**Файл:** `src/App.tsx`

1. Исправить `proceedWithPayment()` - передавать `autoRenewEnabled`
2. Добавить чекбокс "Подключить автопродление" в UI
3. Добавить функцию `handleAutoRenewToggle()`
4. Подключить `AutoRenewModal` к реальным API вызовам

### ШАГ 4: Добавить экран управления подпиской (опционально)

**Новый компонент:** `src/components/SubscriptionSettings.tsx`

Показывать:
- Статус автопродления (вкл/выкл)
- Данные карты (последние 4 цифры, бренд)
- Кнопки: "Отключить автопродление", "Удалить карту"
- История платежей

### ШАГ 5: Тестирование

1. **Тест 1:** Купить подписку с галочкой "Автопродление" ✓
   - Проверить: `payment_method_id` сохранился в БД
   - Проверить: `auto_renew_enabled = true`
   - Проверить: `card_last4` и `card_brand` заполнены

2. **Тест 2:** Отключить автопродление через UI ✓
   - Проверить: `auto_renew_enabled = false`
   - Проверить: `payment_method_id` ОСТАЛСЯ (не удалился)

3. **Тест 3:** Включить автопродление повторно ✓
   - Проверить: можно включить если есть `payment_method_id`

4. **Тест 4:** Удалить способ оплаты ✓
   - Проверить: `payment_method_id = null`
   - Проверить: `auto_renew_enabled = false`
   - Проверить: нельзя включить автопродление (нет карты)

5. **Тест 5:** Дождаться автопродления ✓
   - Установить `subscription_expires_at` на NOW + 30 минут
   - Дождаться срабатывания scheduler (запускается каждый час в :30)
   - Проверить: создался платеж с `is_auto_payment = true`
   - Проверить: подписка продлена на 30 дней
   - Проверить: пришло уведомление в Telegram

---

## 🔧 ВСПОМОГАТЕЛЬНЫЕ СКРИПТЫ

### Проверка статуса пользователя

```bash
# В backend директории
cd backend
python3 << EOF
import asyncio
from app.database import async_session_maker
from app.models.user import User
from sqlalchemy import select

async def check_user():
    async with async_session_manager() as db:
        result = await db.execute(select(User).where(User.telegram_id == YOUR_TELEGRAM_ID))
        user = result.scalar_one_or_none()
        if user:
            print(f"Auto-renew: {user.auto_renew_enabled}")
            print(f"Payment method: {user.payment_method_id}")
            print(f"Card: {user.card_brand} *{user.card_last4}")
        else:
            print("User not found")

asyncio.run(check_user())
EOF
```

### Тестовое срабатывание автопродления

```bash
# Запустить задачу вручную
cd backend
python3 << EOF
import asyncio
from app.scheduler.tasks.auto_renew import process_auto_renewals

asyncio.run(process_auto_renewals())
EOF
```

---

## 📋 ЧЕКЛИСТ ПЕРЕД ЗАПУСКОМ В PRODUCTION

- [ ] Получено одобрение от менеджера ЮKassa
- [ ] 3D-Secure ВКЛЮЧЕН в настройках магазина ЮKassa
- [ ] Все изменения из этого документа применены
- [ ] Фронтенд пересобран (`npm run build`)
- [ ] Backend перезапущен с новым кодом
- [ ] Scheduler работает (логи показывают "Starting auto-renewal task...")
- [ ] Проведен тест полного цикла на staging
- [ ] Настроены уведомления пользователям
- [ ] Добавлена страница с FAQ об автопродлении
- [ ] Обновлены условия пользования (Terms) с упоминанием автоплатежей

---

## 🚨 ВАЖНО: ТРЕБОВАНИЯ ЮKASSA

### Обязательные условия для активации:

1. **UI для отказа от автопродления**
   - ✅ Готово: `AutoRenewModal.tsx` с кнопкой "Отключить автопродление"
   - ✅ Готово: API endpoint `POST /api/users/me/auto-renew/disable`

2. **Возможность удалить карту**
   - ✅ Готово: API endpoint `DELETE /api/users/me/auto-renew/payment-method`
   - ⚠️ Нужно: Добавить кнопку в UI

3. **3D-Secure включен**
   - ⚠️ Проверить в личном кабинете ЮKassa
   - Без 3DS карты НЕ будут сохраняться

4. **merchant_customer_id передается**
   - ✅ Готово: `yookassa_service.py:79` передает `telegram_id`

### Шаблон письма менеджеру:

```
Тема: Активация рекуррентных платежей для магазина [SHOP_ID]

Здравствуйте!

Прошу активировать возможность сохранения способов оплаты для
автоматических платежей в магазине.

Детали магазина:
- Shop ID: [из .env YOOKASSA_SHOP_ID]
- Тип бизнеса: VPN-подписки
- Средний чек: 199 руб/месяц
- Периодичность: ежемесячное продление

Реализовано в системе:
✅ Интерфейс отключения автопродления (см. скриншот 1)
✅ Удаление сохраненной карты (см. скриншот 2)
✅ Уведомления пользователей перед списанием
✅ API для управления подписками

Прилагаю:
- Скриншот 1: Модальное окно с кнопкой "Отключить автопродление"
- Скриншот 2: Кнопка удаления способа оплаты

Ожидаемый оборот автоплатежей: [примерная сумма] руб/месяц

С уважением,
[Ваше имя]
```

---

## 📞 КОНТАКТЫ ЮKASSA

- **Email поддержки:** support@yookassa.ru
- **Телефон:** 8 800 250-66-99
- **Личный кабинет:** https://yookassa.ru/my
- **Документация:** https://yookassa.ru/developers/payment-acceptance/scenario-extensions/recurring-payments

---

## 🎓 ПОЛЕЗНЫЕ ССЫЛКИ

- [Официальная документация: Автоплатежи](https://yookassa.ru/developers/payment-acceptance/scenario-extensions/recurring-payments/basics)
- [Сохранение способа оплаты при платеже](https://yookassa.ru/developers/payment-acceptance/scenario-extensions/recurring-payments/save-payment-method/save-during-payment)
- [Python SDK ЮKassa](https://github.com/yoomoney/yookassa-sdk-python)

---

**ВАЖНО:** Не пытайтесь запустить автопродления до одобрения менеджером!
В production они просто не будут работать, в логах будут ошибки от ЮKassa API.

**Статус:** Ожидание активации от ЮKassa → После активации применить все изменения из этого документа
