import type { Tariff } from '../types'

interface TariffCardProps {
  tariff: Tariff
  isSelected: boolean
  onSelect: (tariff: Tariff) => void
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

export function TariffCard({ tariff, isSelected, onSelect }: TariffCardProps) {
  return (
    <button
      onClick={() => onSelect(tariff)}
      className={`
        group w-full bg-surface-light rounded-2xl p-5 flex items-center justify-between 
        shadow-soft transition-all relative active:scale-[0.98] duration-200
        ${isSelected
          ? 'border-2 border-primary' 
          : 'border-2 border-transparent hover:bg-white'
        }
      `}
    >
      <div className="flex items-center gap-4">
        <TariffIcon type={tariff.icon} isHighlighted={isSelected} />
        <div className="text-left">
          <p className="text-chocolate text-lg font-semibold">{tariff.name}</p>
          <p className="text-chocolate/60 text-sm">{tariff.description}</p>
        </div>
      </div>
      
      <div className="text-right">
        <p className="text-chocolate text-xl font-bold">{tariff.price}₽</p>
      </div>
    </button>
  )
}
