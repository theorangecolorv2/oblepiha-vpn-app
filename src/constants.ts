// Строковые константы для локализации
export const STRINGS = {
  // Названия приложения
  APP_NAME: 'Облепиха VPN',
  CLIENT_APP_NAME: 'Happ',
  CLIENT_APP_DESCRIPTION: 'Клиент для подключения',

  // Навигация
  NAV_SUBSCRIPTION: 'Подписка',
  NAV_CONNECTION: 'Подключение',
  NAV_REFERRALS: 'Рефералы',

  // Экран подписки
  GREETING: 'Привет',
  SELECT_TARIFF: 'Выберите тариф',
  PAY_BUTTON: 'Оплатить',
  SELECT_TARIFF_BUTTON: 'Выберите тариф',

  // Статус
  STATUS_LABEL: 'Статус',
  STATUS_ACTIVE: 'Активен',
  STATUS_INACTIVE: 'Не активен',
  DAYS_LABEL: 'Дней',
  TRAFFIC_LABEL: 'Трафик',
  TRAFFIC_UNIT: 'ГБ',

  // Экран подключения
  SETUP_TITLE: 'Настройка',
  STEP_1_TITLE: 'Установите приложение',
  STEP_2_TITLE: 'Добавьте подписку',
  DOWNLOAD_IOS: 'Скачать в AppStore',
  DOWNLOAD_ANDROID: 'Скачать в Play Market',
  DOWNLOAD_WINDOWS: 'Скачать с оф. сайта',
  AUTO_CONNECT: 'Авто-подключение',
  OTHER_METHODS: 'Другие способы',
  COPY_KEY: 'Скопировать ключ',
  V2RAY: 'v2Ray',
  SUPPORT: 'Написать в поддержку',
  KEY_COPIED: 'Ключ скопирован в буфер обмена',

  // Экран рефералов
  REFERRAL_TITLE: 'Реферальная программа',
  REFERRAL_DESCRIPTION: 'Мы работаем над реферальной системой. Скоро вы сможете приглашать друзей и получать бонусы!',
  COMING_SOON: 'Скоро',

  // Ошибки
  ERROR_NO_SUBSCRIPTION: 'Нет активной подписки',
  ERROR_COPY_FAILED: 'Не удалось скопировать ключ',
} as const

// Единицы измерения
export const UNITS = {
  CURRENCY: '₽',
  TRAFFIC: 'ГБ',
} as const

