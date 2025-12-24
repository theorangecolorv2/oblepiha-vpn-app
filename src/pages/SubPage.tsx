import { useEffect, useState, useRef } from 'react'

/**
 * Страница редиректа для автоподключения в Happ
 * URL: /sub?url=<subscription_url>
 * 
 * Формат deep link: happ://add/{subscription_url}
 * Работает как у конкурентов - просто и надёжно
 */

export function SubPage() {
  const [subscriptionUrl, setSubscriptionUrl] = useState<string>('')
  const [timer, setTimer] = useState(3)
  const [status, setStatus] = useState<'countdown' | 'manual'>('countdown')
  const timerRef = useRef<number | null>(null)
  const redirectedRef = useRef(false)

  // Формируем deep link для Happ
  const happDeepLink = subscriptionUrl ? `happ://add/${subscriptionUrl}` : ''

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const url = params.get('url')
    
    if (url) {
      setSubscriptionUrl(url)
    }
  }, [])

  // Таймер обратного отсчёта и автоматический редирект
  useEffect(() => {
    if (!subscriptionUrl || redirectedRef.current) return

    timerRef.current = window.setInterval(() => {
      setTimer((prev) => {
        if (prev <= 1) {
          // Останавливаем таймер
          if (timerRef.current) {
            clearInterval(timerRef.current)
          }
          
          // Выполняем редирект
          if (!redirectedRef.current) {
            redirectedRef.current = true
            window.location.href = happDeepLink
            
            // Если через 2 сек ещё здесь — показываем ручной режим
            setTimeout(() => {
              setStatus('manual')
            }, 2000)
          }
          
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [subscriptionUrl, happDeepLink])

  // Ручной клик по кнопке
  const handleOpenInHapp = () => {
    if (!happDeepLink) return
    window.location.href = happDeepLink
    
    // Показываем ручной режим через 2 сек
    setTimeout(() => {
      setStatus('manual')
    }, 2000)
  }

  // Копирование ссылки
  const handleCopy = async () => {
    if (!subscriptionUrl) return
    try {
      await navigator.clipboard.writeText(subscriptionUrl)
      alert('✅ Ссылка скопирована!\n\nОткройте Happ → + → Вставить из буфера')
    } catch {
      prompt('Скопируйте ссылку:', subscriptionUrl)
    }
  }

  // Ошибка - нет URL
  if (!subscriptionUrl) {
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
      <div className="text-center max-w-sm w-full">
        {/* Logo */}
        <img 
          src="/logo.webp" 
          alt="Облепиха VPN" 
          className="w-24 h-24 mx-auto rounded-3xl shadow-xl mb-6"
        />
        
        {/* App info */}
        <div className="flex items-center justify-center gap-3 mb-4">
          <svg viewBox="0 0 32 32" fill="currentColor" className="w-8 h-8 text-orange-500">
            <path d="M13.4,19.6l-7.9,7.9L5,30.4h6.6L13.4,19.6z" />
            <path d="M13.2,13.5L14.6,5l-7.9,7.9L4.2,27.4l7.9-7.9l0.2-1.2h1l4.9-4.9H13.2z" />
            <path d="M25.4,19.6L27.8,5l-7.9,7.9l-0.1,0.7h-0.6l-4.9,4.9h4.7l-1.5,9L25.4,19.6z" />
            <path d="M18.7,27.5l-0.5,2.9h6.6l1.8-10.8L18.7,27.5z" />
            <path d="M13.6,4.9l0.6-3.3H7.5L5.6,12.8L13.6,4.9z" />
            <path d="M18.8,12.8l7.9-7.9l0.6-3.3h-6.6L18.8,12.8z" />
          </svg>
          <h2 className="text-2xl font-bold text-gray-800">Happ</h2>
        </div>
        
        <p className="text-gray-600 mb-2">Перенаправление в Happ...</p>
        
        {/* Countdown */}
        {status === 'countdown' && timer > 0 && (
          <div className="mb-6">
            <p className="text-gray-500 text-sm mb-2">Автоматический переход через</p>
            <div className="flex items-baseline justify-center gap-2">
              <span className="text-4xl font-bold text-orange-500">{timer}</span>
              <span className="text-gray-500">сек</span>
            </div>
          </div>
        )}
        
        {/* Info text */}
        <p className="text-gray-500 text-sm mb-5">
          {status === 'countdown' 
            ? 'Если ничего не произошло, нажмите кнопку ниже'
            : 'Убедитесь, что приложение Happ установлено'
          }
        </p>
        
        {/* Buttons */}
        <div className="flex flex-col gap-3">
          <a
            href={happDeepLink}
            onClick={(e) => {
              e.preventDefault()
              handleOpenInHapp()
            }}
            className="w-full py-4 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-2xl font-semibold active:scale-[0.98] transition-transform shadow-lg flex items-center justify-center gap-2"
          >
            <svg viewBox="0 0 32 32" fill="currentColor" className="w-5 h-5">
              <path d="M13.4,19.6l-7.9,7.9L5,30.4h6.6L13.4,19.6z" />
              <path d="M13.2,13.5L14.6,5l-7.9,7.9L4.2,27.4l7.9-7.9l0.2-1.2h1l4.9-4.9H13.2z" />
              <path d="M25.4,19.6L27.8,5l-7.9,7.9l-0.1,0.7h-0.6l-4.9,4.9h4.7l-1.5,9L25.4,19.6z" />
              <path d="M18.7,27.5l-0.5,2.9h6.6l1.8-10.8L18.7,27.5z" />
              <path d="M13.6,4.9l0.6-3.3H7.5L5.6,12.8L13.6,4.9z" />
              <path d="M18.8,12.8l7.9-7.9l0.6-3.3h-6.6L18.8,12.8z" />
            </svg>
            Открыть в Happ
          </a>
          
          <button
            onClick={handleCopy}
            className="w-full py-4 bg-white text-gray-700 rounded-2xl font-semibold border border-gray-200 active:scale-[0.98] transition-transform flex items-center justify-center gap-2"
          >
            📋 Скопировать ссылку
          </button>
        </div>
        
        <p className="text-xs text-gray-400 mt-6 leading-relaxed">
          Если Happ не открывается — скопируйте ссылку<br/>
          и вставьте через меню "+" в приложении
        </p>
      </div>
    </div>
  )
}
