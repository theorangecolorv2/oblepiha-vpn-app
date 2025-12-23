interface StatsProps {
  isActive: boolean
  daysLeft: number
  totalDays: number
  trafficLeftGb: number
  totalTrafficGb: number
}

export function Stats({ isActive, daysLeft, totalDays, trafficLeftGb, totalTrafficGb }: StatsProps) {
  return (
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
          <span className="text-chocolate/60 text-xs font-medium uppercase tracking-wider">Дней</span>
          <span className="text-chocolate text-[13px] font-bold whitespace-nowrap">
            {isActive ? `${daysLeft}/${totalDays}` : '0'}
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
    </section>
  )
}
