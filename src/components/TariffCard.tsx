import type { Tariff } from '../types'

interface TariffCardProps {
  tariff: Tariff
  isSelected: boolean
  onSelect: (tariff: Tariff) => void
  isDisabled?: boolean
  disabledReason?: string
}

// Иконки для разных тарифов
function TariffIcon({ type, isHighlighted }: { type: Tariff['icon']; isHighlighted?: boolean }) {
  const iconName = type === 'trial' ? 'timer' : 'calendar_month'
  const bgClass = isHighlighted 
    ? 'bg-primary/10 text-primary' 
    : 'bg-background-light text-chocolate'
  
  return (
    <div className={`flex items-center justify-center w-11 h-11 rounded-xl ${bgClass}`}>
      <span className="material-symbols-outlined text-[28px]">{iconName}</span>
    </div>
  )
}

export function TariffCard({ tariff, isSelected, onSelect, isDisabled, disabledReason }: TariffCardProps) {
  return (
    <button
      onClick={() => !isDisabled && onSelect(tariff)}
      disabled={isDisabled}
      className={`
        group w-full bg-surface-light rounded-2xl p-5 flex items-center justify-between
        shadow-soft transition-all relative duration-200
        ${isDisabled
          ? 'opacity-50 cursor-not-allowed'
          : 'active:scale-[0.98]'
        }
        ${isSelected && !isDisabled
          ? 'border-2 border-primary'
          : 'border-2 border-transparent hover:bg-white'
        }
      `}
    >
      <div className="flex items-center gap-4">
        <TariffIcon type={tariff.icon} isHighlighted={isSelected && !isDisabled} />
        <div className="text-left">
          <p className="text-chocolate text-lg font-semibold">{tariff.name}</p>
          <p className="text-chocolate/60 text-sm">
            {isDisabled && disabledReason ? disabledReason : tariff.description}
          </p>
        </div>
      </div>

      <div className="text-right">
        <p className="text-chocolate text-xl font-bold">{tariff.price}₽</p>
      </div>
    </button>
  )
}
