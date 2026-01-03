import { useState, useEffect } from 'react'
import { Header, Stats, TariffCard, Button, BottomNav, ConnectionScreen, ReferralScreen, TermsAgreementModal } from './components'
import { useTelegram } from './hooks/useTelegram'
import { useUser } from './hooks/useUser'
import { tariffs as fallbackTariffs } from './data/tariffs'
import type { Tariff } from './types'

function App() {
  const { firstName, userOS, tg } = useTelegram()
  const { isLoading, error, stats, tariffs, user, createPayment, refreshStats, acceptTerms, toggleAutoRenew, deletePaymentMethod } = useUser()
  
  const [selectedTariff, setSelectedTariff] = useState<Tariff | null>(null)
  const [activeTab, setActiveTab] = useState<'shop' | 'vpn' | 'friends'>('shop')
  const [isPaymentLoading, setIsPaymentLoading] = useState(false)
  const [setupAutoRenewForPayment, setSetupAutoRenewForPayment] = useState(true) // Для чекбокса при оплате
  const [showTermsModal, setShowTermsModal] = useState(false)
  const [pendingPayment, setPendingPayment] = useState<(() => void) | null>(null)

  // Используем тарифы с API или fallback
  const displayTariffs = tariffs.length > 0 ? tariffs : fallbackTariffs

  // Статистика пользователя
  const userStats = stats ? {
    isActive: stats.isActive,
    daysLeft: stats.daysLeft,
    trafficLeftGb: stats.trafficLeftGb,
    totalTrafficGb: stats.totalTrafficGb,
  } : {
    isActive: false,
    daysLeft: 0,
    trafficLeftGb: 0,
    totalTrafficGb: 500,
  }

  // Состояние для ошибки платежа
  const [paymentError, setPaymentError] = useState<string | null>(null)

  // Проверка согласия с условиями перед оплатой
  const handlePayment = async () => {
    console.log('[Payment] Button clicked, selectedTariff:', selectedTariff)
    
    if (!selectedTariff) {
      console.warn('[Payment] No tariff selected')
      return
    }

    // Проверяем, принял ли пользователь условия
    const hasAcceptedTerms = user?.termsAcceptedAt !== null && user?.termsAcceptedAt !== undefined

    if (!hasAcceptedTerms) {
      // Показываем модалку с условиями
      setPendingPayment(() => () => proceedWithPayment(selectedTariff.id))
      setShowTermsModal(true)
      return
    }

    // Если условия уже приняты, сразу переходим к оплате
    await proceedWithPayment(selectedTariff.id)
  }

  // Выполнение оплаты
  const proceedWithPayment = async (tariffId: string) => {
    setIsPaymentLoading(true)
    setPaymentError(null)

    try {
      console.log('[Payment] Creating payment for tariff:', tariffId, 'setupAutoRenew:', setupAutoRenewForPayment)
      const confirmationUrl = await createPayment(tariffId, setupAutoRenewForPayment)
      console.log('[Payment] Got confirmation URL:', confirmationUrl)
      
      if (confirmationUrl) {
        // Открываем страницу оплаты
        if (tg?.openLink) {
          console.log('[Payment] Opening via Telegram')
          tg.openLink(confirmationUrl)
        } else {
          console.log('[Payment] Opening via window.open')
          window.open(confirmationUrl, '_blank')
        }
      } else {
        console.error('[Payment] No confirmation URL received')
        setPaymentError('Не удалось создать платёж. Попробуйте ещё раз.')
      }
    } catch (err) {
      console.error('[Payment] Error:', err)
      setPaymentError(err instanceof Error ? err.message : 'Ошибка при создании платежа')
    } finally {
      setIsPaymentLoading(false)
    }
  }

  // Обработка согласия с условиями
  const handleTermsAgree = async () => {
    try {
      await acceptTerms()
      setShowTermsModal(false)
      
      // Если была отложенная оплата - выполняем её
      if (pendingPayment) {
        pendingPayment()
        setPendingPayment(null)
      }
    } catch (err) {
      console.error('[Terms] Failed to accept terms:', err)
      setPaymentError('Не удалось принять условия. Попробуйте ещё раз.')
    }
  }

  // Обновляем статистику при возврате в приложение
  useEffect(() => {
    if (!tg?.onEvent) return

    const handleResume = () => {
      refreshStats()
    }

    tg.onEvent('viewportChanged', handleResume)
    
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
            <Stats
              {...userStats}
              autoRenewEnabled={user?.autoRenewEnabled || false}
              hasPaymentMethod={user?.hasPaymentMethod || false}
              cardLast4={user?.cardLast4 || null}
              cardBrand={user?.cardBrand || null}
              onAutoRenewToggle={async (enabled) => {
                try {
                  await toggleAutoRenew(enabled)
                } catch (err) {
                  console.error('Failed to toggle auto-renew:', err)
                }
              }}
              onDeleteCard={async () => {
                try {
                  await deletePaymentMethod()
                } catch (err) {
                  console.error('Failed to delete payment method:', err)
                }
              }}
            />
            
            {/* Выбор тарифа */}
            <section className="flex flex-col flex-1">
              <h2 className="text-chocolate text-[20px] font-bold leading-tight tracking-tight mb-4">
                Выберите тариф
              </h2>
              
              <div className="flex flex-col gap-3">
                {displayTariffs.map((tariff) => {
                  const isTrialUsed = tariff.id === 'trial' && user?.trialUsed
                  return (
                    <TariffCard
                      key={tariff.id}
                      tariff={tariff}
                      isSelected={selectedTariff?.id === tariff.id}
                      onSelect={setSelectedTariff}
                      isDisabled={isTrialUsed}
                      disabledReason={isTrialUsed ? 'Уже использован' : undefined}
                    />
                  )
                })}
              </div>
              
              {/* Ошибка платежа */}
              {paymentError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl">
                  <p className="text-red-600 text-sm">{paymentError}</p>
                </div>
              )}

              {/* Чекбокс автопродления */}
              {selectedTariff && (
                <div className="mt-4 p-4 bg-surface-light/50 rounded-2xl">
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={setupAutoRenewForPayment}
                      onChange={(e) => setSetupAutoRenewForPayment(e.target.checked)}
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

      {/* Модальное окно согласия с условиями */}
      <TermsAgreementModal 
        isOpen={showTermsModal}
        onAgree={handleTermsAgree}
      />
    </div>
  )
}

export default App
