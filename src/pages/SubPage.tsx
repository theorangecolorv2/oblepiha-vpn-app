import { useEffect, useState } from 'react'

/**
 * Минималистичная страница для открытия подписки в Happ
 * URL: /sub?url=<subscription_url>
 * 
 * Автоматически пытается открыть Happ, показывает fallback если не получилось
 */

export function SubPage() {
  const [subscriptionUrl, setSubscriptionUrl] = useState<string>('')
  const [status, setStatus] = useState<'loading' | 'trying' | 'manual'>('loading')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const url = params.get('url')
    
    if (url) {
      setSubscriptionUrl(url)
      // Автоматически пытаемся открыть
      tryOpenInHapp(url)
    }
  }, [])

  const tryOpenInHapp = (url: string) => {
    setStatus('trying')
    console.log('[SubPage] Opening subscription URL:', url)
    
    // Просто редиректим на URL подписки
    // Happ должен перехватить если зарегистрирован как обработчик
    window.location.href = url
    
    // Если через 2 сек мы ещё здесь - показываем ручной режим
    setTimeout(() => {
      setStatus('manual')
    }, 2000)
  }

  const handleRetry = () => {
    if (subscriptionUrl) {
      tryOpenInHapp(subscriptionUrl)
    }
  }

  const handleCopy = async () => {
    if (!subscriptionUrl) return
    try {
      await navigator.clipboard.writeText(subscriptionUrl)
      alert('✅ Ссылка скопирована!\n\nОткройте Happ → Добавить → Из буфера')
    } catch {
      prompt('Скопируйте ссылку:', subscriptionUrl)
    }
  }

  // Ошибка - нет URL
  if (!subscriptionUrl && status !== 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 flex items-center justify-center p-6">
        <div className="text-center">
          <span className="text-5xl block mb-4">❌</span>
          <h1 className="text-xl font-bold text-gray-800">Ссылка не найдена</h1>
          <p className="text-gray-500 mt-2 text-sm">Вернитесь в приложение</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 flex items-center justify-center p-6">
      <div className="text-center max-w-xs w-full">
        {/* Logo */}
        <img 
          src="/logo.webp" 
          alt="Облепиха VPN" 
          className="w-20 h-20 mx-auto rounded-2xl shadow-lg mb-6"
        />
        
        {/* Loading */}
        {status === 'loading' && (
          <>
            <div className="text-4xl mb-3 animate-pulse">⏳</div>
            <p className="text-gray-500">Загрузка...</p>
          </>
        )}
        
        {/* Trying to open */}
        {status === 'trying' && (
          <>
            <div className="text-4xl mb-3 animate-bounce">🚀</div>
            <h1 className="text-lg font-bold text-gray-800">Открываем Happ...</h1>
            <p className="text-gray-500 text-sm mt-1">Подождите</p>
          </>
        )}
        
        {/* Manual mode - Happ didn't open */}
        {status === 'manual' && (
          <>
            <h1 className="text-lg font-bold text-gray-800 mb-5">
              Не открылось?
            </h1>
            
            <div className="flex flex-col gap-3">
              <button
                onClick={handleRetry}
                className="w-full py-3.5 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-xl font-semibold active:scale-[0.98] transition-transform shadow-lg"
              >
                🔄 Попробовать снова
              </button>
              
              <button
                onClick={handleCopy}
                className="w-full py-3.5 bg-white text-gray-700 rounded-xl font-semibold border border-gray-200 active:scale-[0.98] transition-transform"
              >
                📋 Скопировать ссылку
              </button>
            </div>
            
            <p className="text-xs text-gray-400 mt-5 leading-relaxed">
              Скопируйте и вставьте в Happ<br/>
              через меню "Добавить"
            </p>
          </>
        )}
      </div>
    </div>
  )
}
