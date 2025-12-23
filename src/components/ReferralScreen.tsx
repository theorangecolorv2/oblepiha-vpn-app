import { STRINGS } from '../constants'

export function ReferralScreen() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4">
      {/* Иконка в работе */}
      <div className="w-20 h-20 rounded-full bg-chocolate/5 flex items-center justify-center mb-6">
        <span className="material-symbols-outlined text-[40px] text-chocolate/40">
          engineering
        </span>
      </div>
      
      {/* Заголовок */}
      <h2 className="text-xl font-bold text-chocolate mb-2 text-center">
        {STRINGS.REFERRAL_TITLE}
      </h2>
      
      {/* Описание */}
      <p className="text-chocolate/60 text-center text-sm max-w-xs mb-6">
        {STRINGS.REFERRAL_DESCRIPTION}
      </p>
      
      {/* Бейдж "Скоро" */}
      <div className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-primary/10 text-primary">
        <span className="material-symbols-outlined text-[18px]">schedule</span>
        <span className="text-sm font-semibold">{STRINGS.COMING_SOON}</span>
      </div>
    </div>
  )
}

