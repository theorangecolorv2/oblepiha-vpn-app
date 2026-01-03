// Конфигурация приложения
// В продакшене эти значения берутся из переменных окружения (import.meta.env)

export const config = {
  // API бэкенда (на том же домене, Caddy проксирует /api/* на бэкенд)
  apiUrl: import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://oblepiha-app.ru'),
  
  // Режим разработки - показывать тестовые данные если нет Telegram
  devMode: import.meta.env.VITE_DEV_MODE === 'true' || import.meta.env.DEV,
  

  // Ссылка на поддержку в Telegram
  supportTg: import.meta.env.VITE_SUPPORT_TG || 'https://t.me/oblepiha_support',

  // Ссылка на условия пользования (страница /info в мини-аппе)
  termsUrl: import.meta.env.VITE_TERMS_URL || '/info',

  // Ссылки на скачивание приложения Happ
  happDownload: {
    ios: import.meta.env.VITE_HAPP_IOS || 'https://apps.apple.com/app/happ-vpn/id1234567890',
    android: import.meta.env.VITE_HAPP_ANDROID || 'https://play.google.com/store/apps/details?id=com.happ.vpn',
    windows: import.meta.env.VITE_HAPP_WINDOWS || 'https://happ.su/download/windows',
  },

  // Ссылки на скачивание v2Ray
  v2rayDownload: {
    ios: import.meta.env.VITE_V2RAY_IOS || 'https://apps.apple.com/app/v2rayng/id1234567890',
    android: import.meta.env.VITE_V2RAY_ANDROID || 'https://play.google.com/store/apps/details?id=com.v2ray.ang',
    windows: import.meta.env.VITE_V2RAY_WINDOWS || 'https://github.com/2dust/v2rayN/releases',
  },

  // Deep link схемы для Happ
  // Happ поддерживает: vmess://, vless://, trojan://, ss://, socks://
  // А также зашифрованные ссылки: happ://crypto...
  happDeepLink: {
    // URL схема для прямого импорта конфигурации
    scheme: 'happ',
    // Альтернативные схемы (работают на всех устройствах)
    altSchemes: ['vmess', 'vless', 'trojan', 'ss', 'socks'],
  },
}

// Тестовые данные для разработки без Telegram
export const devUser = {
  firstName: 'Вадим',
  lastName: 'Тест',
  username: 'test_user',
}

// Моковые данные пользователя с привязанной картой (для скриншотов ЮKassa)
export const mockUserData = {
  user: {
    id: 1,
    telegramId: 123456789,
    telegramUsername: 'vadim_test',
    firstName: 'Вадим',
    isActive: true,
    subscriptionExpiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // +30 дней
    daysLeft: 30,
    subscriptionUrl: 'vless://test-subscription-url',
    trafficUsedBytes: 10 * 1024 * 1024 * 1024, // 10 GB
    trafficLimitBytes: 500 * 1024 * 1024 * 1024, // 500 GB
    referralCode: 'VADIM2024',
    termsAcceptedAt: new Date().toISOString(),
    trialUsed: true,
    autoRenewEnabled: true,
    hasPaymentMethod: true,
    cardLast4: '4242',
    cardBrand: 'Visa',
  },
  stats: {
    isActive: true,
    daysLeft: 30,
    totalDays: 30,
    trafficLeftGb: 490,
    totalTrafficGb: 500,
    subscriptionUrl: 'vless://test-subscription-url',
  },
}

// Тестовый ключ подписки для разработки
// В продакшене будет получаться из API для каждого пользователя
export const DEV_SUBSCRIPTION_KEY = 'vmess://eyJhZGQiOiJ0ZXN0LmV4YW1wbGUuY29tIiwicG9ydCI6IjQ0MyIsInR5cGUiOiJub25lIiwiaWQiOiJ0ZXN0LWlkIiwiYWlkIjoiMCIsIm5ldCI6IndzIiwicGF0aCI6Ii8iLCJob3N0IjoidGVzdC5leGFtcGxlLmNvbSIsInRscyI6InRscyIsInNuaSI6InRlc3QuZXhhbXBsZS5jb20iLCJhbHBuIjoiIn0='

