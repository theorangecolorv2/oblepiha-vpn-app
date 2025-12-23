import { useState } from 'react'
import type { UserOS } from '../hooks/useTelegram'
import { config, DEV_SUBSCRIPTION_KEY } from '../config'
import { STRINGS } from '../constants'

interface ConnectionScreenProps {
  userOS: UserOS
  // В будущем сюда будет передаваться ключ подписки из API
  subscriptionKey?: string
}

type OSTab = 'ios' | 'android' | 'windows'

// Конфигурация приложений для разных ОС
const getAppConfig = (os: OSTab) => ({
  appName: STRINGS.CLIENT_APP_NAME,
  downloadLabel: os === 'ios' 
    ? STRINGS.DOWNLOAD_IOS 
    : os === 'android' 
      ? STRINGS.DOWNLOAD_ANDROID 
      : STRINGS.DOWNLOAD_WINDOWS,
  downloadUrl: config.happDownload[os],
  v2rayUrl: config.v2rayDownload[os],
})

/**
 * Генерирует deep link для автоматического импорта подписки в Happ
 * 
 * Happ поддерживает несколько способов импорта:
 * 1. Прямые ссылки протоколов: vmess://, vless://, trojan://, ss://, socks://
 * 2. Зашифрованные ссылки: happ://crypto... (для скрытия настроек от пользователя)
 * 
 * При клике на такую ссылку, если Happ установлен, он откроется и предложит
 * добавить конфигурацию. На iOS/Android это работает через URL schemes,
 * на Windows - через ассоциацию протоколов.
 */
function generateDeepLink(subscriptionKey: string): string {
  // Если ключ уже содержит протокол (vmess://, vless://, etc.) - используем его напрямую
  // Это позволяет Happ автоматически импортировать конфигурацию
  if (subscriptionKey.match(/^(vmess|vless|trojan|ss|socks):\/\//)) {
    return subscriptionKey
  }
  
  // Если это зашифрованная ссылка happ://
  if (subscriptionKey.startsWith('happ://')) {
    return subscriptionKey
  }
  
  // Если это обычный URL подписки - оборачиваем в happ:// схему
  // Формат: happ://add?url=ENCODED_SUBSCRIPTION_URL
  return `happ://add?url=${encodeURIComponent(subscriptionKey)}`
}

export function ConnectionScreen({ userOS, subscriptionKey }: ConnectionScreenProps) {
  const [selectedOS, setSelectedOS] = useState<OSTab>(userOS)
  const [copySuccess, setCopySuccess] = useState(false)
  const appConfig = getAppConfig(selectedOS)
  
  // Используем переданный ключ или тестовый в режиме разработки
  const currentKey = subscriptionKey || (config.devMode ? DEV_SUBSCRIPTION_KEY : '')

  const handleDownload = () => {
    window.open(appConfig.downloadUrl, '_blank')
  }

  /**
   * Автоподключение через deep link
   * 
   * Логика работы:
   * 1. Генерируем deep link с ключом подписки
   * 2. Пытаемся открыть через window.location (работает на мобильных)
   * 3. Если Happ установлен - он откроется и импортирует конфигурацию
   * 4. Если не установлен - показываем страницу скачивания (или ничего не произойдёт)
   */
  const handleAutoConnect = () => {
    if (!currentKey) {
      console.error(STRINGS.ERROR_NO_SUBSCRIPTION)
      return
    }

    const deepLink = generateDeepLink(currentKey)
    
    // На мобильных устройствах открываем deep link напрямую
    // Это откроет Happ если он установлен
    if (selectedOS === 'ios' || selectedOS === 'android') {
      window.location.href = deepLink
    } else {
      // На десктопе открываем в новом окне
      // Windows может запросить разрешение на открытие приложения
      window.open(deepLink, '_blank')
    }
  }

  const handleCopyKey = async () => {
    if (!currentKey) {
      console.error(STRINGS.ERROR_NO_SUBSCRIPTION)
      return
    }

    try {
      await navigator.clipboard.writeText(currentKey)
      setCopySuccess(true)
      setTimeout(() => setCopySuccess(false), 2000)
    } catch (err) {
      console.error(STRINGS.ERROR_COPY_FAILED, err)
    }
  }

  const handleDownloadV2Ray = () => {
    window.open(appConfig.v2rayUrl, '_blank')
  }

  const handleSupport = () => {
    window.open(config.supportTg, '_blank')
  }

  return (
    <div className="flex flex-col gap-5 w-full">
      {/* Заголовок и переключатель ОС */}
      <div className="flex flex-col items-center">
        <h1 className="text-[28px] font-bold tracking-tight mb-5 text-chocolate">
          {STRINGS.SETUP_TITLE}
        </h1>

        {/* Segmented Control */}
        <div className="flex w-full bg-chocolate/5 p-1 rounded-full">
          {(['ios', 'android', 'windows'] as OSTab[]).map((os) => (
            <button
              key={os}
              onClick={() => setSelectedOS(os)}
              className={`
                flex-1 h-9 rounded-full text-sm font-medium transition-all duration-300
                ${selectedOS === os
                  ? 'bg-white text-chocolate shadow-sm font-bold'
                  : 'text-chocolate/50 hover:text-chocolate/70'
                }
              `}
            >
              {os === 'ios' ? 'iOS' : os === 'android' ? 'Android' : 'Windows'}
            </button>
          ))}
        </div>
      </div>

      {/* Основная карточка настройки */}
      <div className="bg-white rounded-2xl p-5 shadow-soft w-full">
        {/* App Header */}
        <div className="flex items-center gap-4 mb-6">
          <img 
            src="/happ.webp" 
            alt={STRINGS.CLIENT_APP_NAME}
            className="w-14 h-14 rounded-2xl shadow-md object-cover"
          />
          <div>
            <h2 className="text-xl font-bold text-chocolate leading-tight">
              {appConfig.appName}
            </h2>
            <p className="text-xs text-chocolate/50 font-medium">
              {STRINGS.CLIENT_APP_DESCRIPTION}
            </p>
          </div>
        </div>

        {/* Steps */}
        <div className="flex flex-col gap-6">
          {/* Step 1 */}
          <div className="relative pl-11 step-line">
            <div className="absolute left-0 top-0 w-7 h-7 rounded-full bg-blue-50 border-2 border-blue-100 flex items-center justify-center z-10">
              <span className="text-blue-600 font-bold text-xs">1</span>
            </div>
            <div className="flex flex-col gap-2.5">
              <h3 className="font-medium text-chocolate text-sm">
                {STRINGS.STEP_1_TITLE}
              </h3>
              <button 
                onClick={handleDownload}
                className="w-full h-11 bg-chocolate/5 hover:bg-chocolate/10 active:bg-chocolate/15 text-chocolate rounded-full flex items-center justify-center gap-2 transition-colors duration-200 font-semibold text-sm"
              >
                <span className="material-symbols-outlined text-[18px]">download_for_offline</span>
                {appConfig.downloadLabel}
              </button>
            </div>
          </div>

          {/* Step 2 */}
          <div className="relative pl-11">
            <div className="absolute left-0 top-0 w-7 h-7 rounded-full bg-orange-50 border-2 border-orange-100 flex items-center justify-center z-10">
              <span className="text-primary font-bold text-xs">2</span>
            </div>
            <div className="flex flex-col gap-2.5">
              <h3 className="font-medium text-chocolate text-sm">
                {STRINGS.STEP_2_TITLE}
              </h3>
              <button 
                onClick={handleAutoConnect}
                disabled={!currentKey}
                className={`
                  w-full h-12 rounded-full flex items-center justify-center gap-2 
                  transition-all duration-200 font-bold text-sm tracking-wide
                  ${currentKey 
                    ? 'bg-primary hover:bg-[#d54d26] active:scale-[0.98] text-white shadow-lg shadow-primary/30' 
                    : 'bg-chocolate/10 text-chocolate/40 cursor-not-allowed'
                  }
                `}
              >
                <span>🚀</span>
                {STRINGS.AUTO_CONNECT}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Другие способы - компактнее */}
      <div className="flex flex-col gap-2">
        <h4 className="text-[10px] uppercase tracking-wider text-chocolate/40 font-bold pl-2">
          {STRINGS.OTHER_METHODS}
        </h4>
        <div className="flex gap-2">
          {/* Copy Key */}
          <button 
            onClick={handleCopyKey}
            disabled={!currentKey}
            className={`
              flex-1 bg-white rounded-xl p-3 flex flex-col items-center gap-1.5 
              transition-transform shadow-soft
              ${currentKey ? 'active:scale-[0.98]' : 'opacity-50 cursor-not-allowed'}
            `}
          >
            <div className={`
              w-9 h-9 rounded-full flex items-center justify-center
              ${copySuccess ? 'bg-green-100 text-green-600' : 'bg-chocolate/5 text-chocolate'}
            `}>
              <span className="material-symbols-outlined text-[18px]">
                {copySuccess ? 'check' : 'content_copy'}
              </span>
            </div>
            <span className="text-xs font-medium text-chocolate/70">
              {copySuccess ? STRINGS.KEY_COPIED : STRINGS.COPY_KEY}
            </span>
          </button>

          {/* Download V2Ray */}
          <button 
            onClick={handleDownloadV2Ray}
            className="flex-1 bg-white rounded-xl p-3 flex flex-col items-center gap-1.5 active:scale-[0.98] transition-transform shadow-soft"
          >
            <div className="w-9 h-9 rounded-full bg-chocolate/5 flex items-center justify-center text-chocolate">
              <span className="material-symbols-outlined text-[18px]">file_download</span>
            </div>
            <span className="text-xs font-medium text-chocolate/70">{STRINGS.V2RAY}</span>
          </button>
        </div>
      </div>

      {/* Support Button - более заметная */}
      <button 
        onClick={handleSupport}
        className="w-full py-3 px-4 rounded-xl bg-chocolate/5 hover:bg-chocolate/10 active:scale-[0.99] transition-all flex items-center justify-center gap-2 text-chocolate/70 hover:text-chocolate"
      >
        <span className="material-symbols-outlined text-[20px]">support_agent</span>
        <span className="text-sm font-medium">{STRINGS.SUPPORT}</span>
      </button>
    </div>
  )
}
