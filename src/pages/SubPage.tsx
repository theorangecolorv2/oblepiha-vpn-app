import { useEffect, useState } from 'react'

/**
 * Страница для импорта подписки в VPN клиент
 * URL: /sub?url=<subscription_url>
 * 
 * Эта страница показывается когда пользователь нажимает "Авто-подключение"
 * и позволяет:
 * - Открыть подписку в Happ/v2rayNG
 * - Показать QR код для сканирования
 * - Скопировать ключ
 */

type OS = 'ios' | 'android' | 'windows' | 'unknown'

function detectOS(): OS {
  if (typeof navigator === 'undefined') return 'unknown'
  const ua = navigator.userAgent.toLowerCase()
  
  if (ua.includes('iphone') || ua.includes('ipad') || ua.includes('mac')) return 'ios'
  if (ua.includes('android')) return 'android'
  if (ua.includes('win')) return 'windows'
  return 'unknown'
}

// Deep link схемы для разных клиентов
const getDeepLinks = (subscriptionUrl: string) => ({
  // Happ использует sub:// или просто открытие URL
  happ: `happ://add?url=${encodeURIComponent(subscriptionUrl)}`,
  // v2rayNG на Android
  v2rayng: `v2rayng://install-sub?url=${encodeURIComponent(subscriptionUrl)}`,
  // Альтернативный формат
  clash: `clash://install-config?url=${encodeURIComponent(subscriptionUrl)}`,
})

export function SubPage() {
  const [subscriptionUrl, setSubscriptionUrl] = useState<string>('')
  const [copySuccess, setCopySuccess] = useState(false)
  const [os] = useState<OS>(detectOS)
  const [showQR, setShowQR] = useState(false)

  useEffect(() => {
    // Получаем URL подписки из query параметра
    const params = new URLSearchParams(window.location.search)
    const url = params.get('url')
    if (url) {
      setSubscriptionUrl(url)
    }
  }, [])

  const handleCopy = async () => {
    if (!subscriptionUrl) return
    try {
      await navigator.clipboard.writeText(subscriptionUrl)
      setCopySuccess(true)
      setTimeout(() => setCopySuccess(false), 2000)
    } catch (err) {
      console.error('Copy failed:', err)
    }
  }

  const handleOpenInApp = (scheme: 'happ' | 'v2rayng') => {
    if (!subscriptionUrl) return
    const links = getDeepLinks(subscriptionUrl)
    
    // Пробуем открыть deep link
    const link = links[scheme]
    console.log('[SubPage] Opening:', link)
    
    // Создаём скрытую ссылку и кликаем
    const a = document.createElement('a')
    a.href = link
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    
    // Fallback
    setTimeout(() => {
      window.location.href = link
    }, 100)
  }

  // Пробуем открыть прямой URL (может сработать если приложение зарегистрировано)
  const handleOpenDirect = () => {
    if (!subscriptionUrl) return
    window.location.href = subscriptionUrl
  }

  if (!subscriptionUrl) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-6 shadow-lg text-center">
          <span className="text-4xl mb-4 block">❌</span>
          <h1 className="text-xl font-bold text-gray-800">Ссылка не найдена</h1>
          <p className="text-gray-500 mt-2">Вернитесь в приложение и попробуйте снова</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 p-4">
      <div className="max-w-md mx-auto">
        {/* Header */}
        <div className="text-center mb-6 pt-8">
          <img 
            src="/logo.webp" 
            alt="Облепиха VPN" 
            className="w-20 h-20 mx-auto rounded-2xl shadow-lg mb-4"
          />
          <h1 className="text-2xl font-bold text-gray-800">Облепиха VPN</h1>
          <p className="text-gray-500 mt-1">Добавить подписку</p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl p-5 shadow-lg mb-4">
          <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <span>📱</span> Открыть в приложении
          </h2>
          
          <div className="flex flex-col gap-3">
            {/* Happ Button */}
            <button
              onClick={() => handleOpenInApp('happ')}
              className="w-full py-3 px-4 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-xl font-semibold flex items-center justify-center gap-2 active:scale-[0.98] transition-transform"
            >
              <img src="/happ.webp" alt="Happ" className="w-6 h-6 rounded" />
              Открыть в Happ
            </button>

            {/* v2rayNG for Android */}
            {os === 'android' && (
              <button
                onClick={() => handleOpenInApp('v2rayng')}
                className="w-full py-3 px-4 bg-gray-100 text-gray-700 rounded-xl font-semibold flex items-center justify-center gap-2 active:scale-[0.98] transition-transform"
              >
                <span>📡</span>
                Открыть в v2rayNG
              </button>
            )}

            {/* Direct URL */}
            <button
              onClick={handleOpenDirect}
              className="w-full py-2.5 px-4 border border-gray-200 text-gray-600 rounded-xl text-sm flex items-center justify-center gap-2 active:scale-[0.98] transition-transform"
            >
              <span>🔗</span>
              Открыть ссылку напрямую
            </button>
          </div>
        </div>

        {/* QR Code Card */}
        <div className="bg-white rounded-2xl p-5 shadow-lg mb-4">
          <button
            onClick={() => setShowQR(!showQR)}
            className="w-full flex items-center justify-between"
          >
            <h2 className="font-semibold text-gray-800 flex items-center gap-2">
              <span>📷</span> QR-код для сканирования
            </h2>
            <span className="text-gray-400">{showQR ? '▲' : '▼'}</span>
          </button>
          
          {showQR && (
            <div className="mt-4 flex flex-col items-center">
              <div className="bg-white p-3 rounded-xl border border-gray-100">
                {/* QR код через внешний API */}
                <img 
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(subscriptionUrl)}`}
                  alt="QR Code"
                  width={200}
                  height={200}
                  className="rounded"
                />
              </div>
              <p className="text-xs text-gray-400 mt-3 text-center">
                Откройте Happ → Добавить → Сканировать QR
              </p>
            </div>
          )}
        </div>

        {/* Copy Key Card */}
        <div className="bg-white rounded-2xl p-5 shadow-lg mb-4">
          <h2 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <span>📋</span> Скопировать ключ
          </h2>
          
          <div className="bg-gray-50 rounded-xl p-3 mb-3">
            <p className="text-xs text-gray-500 font-mono break-all">
              {subscriptionUrl.length > 60 
                ? subscriptionUrl.slice(0, 60) + '...' 
                : subscriptionUrl
              }
            </p>
          </div>
          
          <button
            onClick={handleCopy}
            className={`w-full py-3 px-4 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all ${
              copySuccess 
                ? 'bg-green-100 text-green-700' 
                : 'bg-gray-100 text-gray-700 active:scale-[0.98]'
            }`}
          >
            <span>{copySuccess ? '✓' : '📋'}</span>
            {copySuccess ? 'Скопировано!' : 'Скопировать ссылку'}
          </button>
        </div>

        {/* Instructions */}
        <div className="bg-amber-50 rounded-2xl p-4 mb-8">
          <h3 className="font-semibold text-amber-800 mb-2 flex items-center gap-2">
            <span>💡</span> Инструкция
          </h3>
          <ol className="text-sm text-amber-700 space-y-1 list-decimal list-inside">
            <li>Скачайте приложение Happ</li>
            <li>Нажмите кнопку "Открыть в Happ" выше</li>
            <li>Или скопируйте ссылку и вставьте в приложении</li>
            <li>Подключайтесь и пользуйтесь VPN!</li>
          </ol>
        </div>

        {/* Back Button */}
        <button
          onClick={() => window.history.back()}
          className="w-full py-3 text-gray-500 text-sm"
        >
          ← Вернуться назад
        </button>
      </div>
    </div>
  )
}

