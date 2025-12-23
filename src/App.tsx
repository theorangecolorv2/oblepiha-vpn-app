import { useState } from 'react'
import { Header, Stats, TariffCard, Button, BottomNav, ConnectionScreen, ReferralScreen } from './components'
import { useTelegram } from './hooks/useTelegram'
import { tariffs } from './data/tariffs'
import type { Tariff } from './types'

function App() {
  const { firstName, userOS } = useTelegram()
  const [selectedTariff, setSelectedTariff] = useState<Tariff | null>(null)
  const [activeTab, setActiveTab] = useState<'shop' | 'vpn' | 'friends'>('shop')

  // TODO: Заменить на данные из API
  const userStats = {
    isActive: false,
    daysLeft: 0,
    totalDays: 30,
    trafficLeftGb: 0,
    totalTrafficGb: 200,
  }

  const handlePayment = () => {
    if (!selectedTariff) return
    // TODO: Интеграция с оплатой
    console.log('Оплата тарифа:', selectedTariff)
  }

  // Рендер контента в зависимости от активной вкладки
  const renderContent = () => {
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
                {tariffs.map((tariff) => (
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
                  disabled={!selectedTariff}
                >
                  {selectedTariff 
                    ? `Оплатить ${selectedTariff.price}₽` 
                    : 'Выберите тариф'
                  }
                </Button>
              </div>
            </section>
          </>
        )
      
      case 'vpn':
        return <ConnectionScreen userOS={userOS} />
      
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
