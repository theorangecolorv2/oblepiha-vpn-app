import { useState } from 'react'
import { AutoRenewModal } from './AutoRenewModal'

interface StatsProps {
  isActive: boolean
  daysLeft: number
  trafficLeftGb: number
  totalTrafficGb: number
  autoRenewEnabled?: boolean
  hasPaymentMethod?: boolean
  cardLast4?: string | null
  cardBrand?: string | null
  onAutoRenewToggle?: (enabled: boolean) => void
  onDeleteCard?: () => void
}

export function Stats({
  isActive,
  daysLeft,
  trafficLeftGb,
  totalTrafficGb,
  autoRenewEnabled = false,
  hasPaymentMethod = false,
  cardLast4 = null,
  cardBrand = null,
  onAutoRenewToggle,
  onDeleteCard
}: StatsProps) {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleToggle = (enabled: boolean) => {
    onAutoRenewToggle?.(enabled)
    // Закрываем модалку после переключения, если отключили
    if (!enabled) {
      setIsModalOpen(false)
    }
  }

  return (
    <>
      <section className="mb-5">
        <div className="w-full bg-surface-light rounded-2xl p-4 shadow-soft grid grid-cols-3 divide-x divide-chocolate/10">
          {/* Status */}
          <div className="flex flex-col items-center gap-1.5 px-1">
            <span className="text-chocolate/60 text-xs font-medium uppercase tracking-wider">Статус</span>
            <div className="flex items-center gap-1">
              <span className={`inline-flex rounded-full h-2 w-2 shrink-0 ${isActive ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-chocolate text-[13px] font-bold whitespace-nowrap">
                {isActive ? 'Активен' : 'Не активен'}
              </span>
            </div>
          </div>
          
          {/* Days */}
          <div className="flex flex-col items-center gap-1.5 px-1">
            <span className="text-chocolate/60 text-xs font-medium uppercase tracking-wider">Осталось</span>
            <span className="text-chocolate text-[13px] font-bold whitespace-nowrap">
              {isActive ? `${daysLeft} дн.` : '0 дн.'}
            </span>
          </div>
          
          {/* Traffic */}
          <div className="flex flex-col items-center gap-1.5 px-1">
            <span className="text-chocolate/60 text-xs font-medium uppercase tracking-wider">Трафик</span>
            <span className="text-chocolate text-[13px] font-bold whitespace-nowrap">
              {isActive ? `${trafficLeftGb}/${totalTrafficGb} ГБ` : '0 ГБ'}
            </span>
          </div>
        </div>
        
        {/* Ненавязчивая ссылка на автопродление */}
        {isActive && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="mt-2 w-full text-center text-chocolate/40 hover:text-chocolate/60 text-xs transition-colors active:opacity-70"
          >
            <span className="inline-flex items-center gap-1">
              <span className="material-symbols-outlined text-sm">autorenew</span>
              Автопродление
            </span>
          </button>
        )}
      </section>

      {/* Модальное окно автопродления */}
      <AutoRenewModal
        isOpen={isModalOpen}
        isEnabled={autoRenewEnabled}
        hasPaymentMethod={hasPaymentMethod}
        cardLast4={cardLast4}
        cardBrand={cardBrand}
        onClose={() => setIsModalOpen(false)}
        onToggle={handleToggle}
        onDeleteCard={() => {
          onDeleteCard?.()
          setIsModalOpen(false)
        }}
      />
    </>
  )
}
