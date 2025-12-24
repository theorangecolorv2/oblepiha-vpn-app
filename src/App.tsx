import { useState, useEffect } from 'react'
import { Header, Stats, TariffCard, Button, BottomNav, ConnectionScreen, ReferralScreen } from './components'
import { useTelegram } from './hooks/useTelegram'
import { useUser } from './hooks/useUser'
import { tariffs as fallbackTariffs } from './data/tariffs'
import type { Tariff } from './types'

function App() {
  const { firstName, userOS, tg, isReady } = useTelegram()
  const { isLoading, error, stats, tariffs, createPayment, refreshStats } = useUser()
  
  const [selectedTariff, setSelectedTariff] = useState<Tariff | null>(null)
  const [activeTab, setActiveTab] = useState<'shop' | 'vpn' | 'friends'>('shop')
  const [isPaymentLoading, setIsPaymentLoading] = useState(false)

  // Используем тарифы с API или fallback
  const displayTariffs = tariffs.length > 0 ? tariffs : fallbackTariffs

  // Статистика пользователя
  const userStats = stats ? {
    isActive: stats.isActive,
    daysLeft: stats.daysLeft,
    totalDays: stats.totalDays,
    trafficLeftGb: stats.trafficLeftGb,
    totalTrafficGb: stats.totalTrafficGb,
  } : {
    isActive: false,
    daysLeft: 0,
    totalDays: 30,
    trafficLeftGb: 0,
    totalTrafficGb: 200,
  }

  // Обработка оплаты
  const handlePayment = async () => {
    if (!selectedTariff) return
    
    setIsPaymentLoading(true)
    
    try {
      const confirmationUrl = await createPayment(selectedTariff.id)
      
      if (confirmationUrl) {
        // Открываем страницу оплаты
        if (tg) {
          // В Telegram открываем через openLink
          tg.openLink(confirmationUrl)
        } else {
          // В браузере просто открываем
          window.open(confirmationUrl, '_blank')
        }
      }
    } catch (err) {
      console.error('Payment error:', err)
    } finally {
      setIsPaymentLoading(false)
    }
  }

  // Обновляем статистику при возврате в приложение
  useEffect(() => {
    if (!tg) return

    const handleResume = () => {
      // Обновляем статистику когда пользователь возвращается в приложение
      refreshStats()
    }

    // Telegram WebApp events
    tg.onEvent?.('viewportChanged', handleResume)
    
    return () => {
      tg.offEvent?.('viewportChanged', handleResume)
    }
  }, [tg, refreshStats])

  // Рендер контента в зависимости от активной вкладки
  const renderContent = () => {
    // Показываем загрузку
    if (isLoading && !stats) {
      return (
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="text-chocolate/60">Загрузка...</div>
        </div>
      )
    }

    // Показываем ошибку
    if (error && !stats) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
          <div className="text-red-500">{error}</div>
          <Button onClick={() => window.location.reload()}>
            Попробовать снова
          </Button>
        </div>
      )
    }

    switch (activeTab) {
      case 'shop':
        return (
          <>
            <Header firstName={firstName} />
            <Stats {...userStats} />
            
            {/* Выбор тарифа */}
            <section className="flex flex-col flex-1">
              <h2 className="text-chocolate text-[20px] font-bold leading-tight tracking-tight mb-4">
                Выберите тариф
              </h2>
              
              <div className="flex flex-col gap-3">
                {displayTariffs.map((tariff) => (
                  <TariffCard
                    key={tariff.id}
                    tariff={tariff}
                    isSelected={selectedTariff?.id === tariff.id}
                    onSelect={setSelectedTariff}
                  />
                ))}
              </div>
              
              {/* Кнопка оплаты */}
              <div className="mt-5">
                <Button 
                  onClick={handlePayment}
                  disabled={!selectedTariff || isPaymentLoading}
                >
                  {isPaymentLoading
                    ? 'Создание платежа...'
                    : selectedTariff 
                      ? `Оплатить ${selectedTariff.price}₽` 
                      : 'Выберите тариф'
                  }
                </Button>
              </div>
            </section>
          </>
        )
      
      case 'vpn':
        return (
          <ConnectionScreen 
            userOS={userOS} 
            subscriptionUrl={stats?.subscriptionUrl || null}
            isActive={stats?.isActive || false}
          />
        )
      
      case 'friends':
        return <ReferralScreen />
      
      default:
        return null
    }
  }

  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden bg-background-light font-display text-chocolate antialiased selection:bg-primary/30">
      {/* Background Pattern/Gradient */}
      <div className="fixed inset-0 pointer-events-none z-[-1] opacity-40 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-orange-100/40 via-transparent to-transparent" />
      
      {/* Основной контент */}
      <main className="px-5 pt-5 pb-36 max-w-md mx-auto w-full">
        {renderContent()}
      </main>
      
      {/* Нижняя навигация */}
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
    </div>
  )
}

export default App
