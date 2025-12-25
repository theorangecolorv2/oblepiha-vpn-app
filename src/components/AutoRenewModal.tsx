interface AutoRenewModalProps {
  isOpen: boolean
  isEnabled: boolean
  onClose: () => void
  onToggle: (enabled: boolean) => void
}

export function AutoRenewModal({ 
  isOpen, 
  isEnabled, 
  onClose, 
  onToggle 
}: AutoRenewModalProps) {
  if (!isOpen) return null

  const handleToggle = () => {
    onToggle(!isEnabled)
  }

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/40 z-40 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div 
          className="bg-surface-light rounded-3xl p-6 max-w-sm w-full shadow-xl pointer-events-auto opacity-0"
          style={{
            animation: 'fadeInZoom 0.2s ease-out forwards'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
                <span className="material-symbols-outlined text-primary text-xl">
                  autorenew
                </span>
              </div>
              <h3 className="text-chocolate text-xl font-bold">
                Автопродление
              </h3>
            </div>
            <button
              onClick={onClose}
              className="text-chocolate/40 hover:text-chocolate/60 transition-colors p-1"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>

          {/* Content */}
          <div className="mb-6">
            {isEnabled ? (
              <>
                <div className="flex items-center gap-2 mb-4 p-3 bg-green-50 rounded-xl border border-green-200">
                  <span className="material-symbols-outlined text-green-600 text-xl">
                    check_circle
                  </span>
                  <span className="text-green-800 text-sm font-medium">
                    Автопродление включено
                  </span>
                </div>
                <p className="text-chocolate/70 text-sm leading-relaxed mb-3">
                  Ваша подписка будет автоматически продлеваться в конце каждого периода оплаты. 
                  Это позволит вам не беспокоиться о продлении и всегда иметь доступ к VPN.
                </p>
                <p className="text-chocolate/50 text-xs leading-relaxed">
                  Вы можете отключить автопродление в любой момент ниже.
                </p>
              </>
            ) : (
              <>
                <div className="flex items-center gap-2 mb-4 p-3 bg-orange-50 rounded-xl border border-orange-200">
                  <span className="material-symbols-outlined text-orange-600 text-xl">
                    info
                  </span>
                  <span className="text-orange-800 text-sm font-medium">
                    Автопродление отключено
                  </span>
                </div>
                <p className="text-chocolate/70 text-sm leading-relaxed mb-3">
                  Ваша подписка не будет продлеваться автоматически. 
                  Когда срок действия истечёт, вам нужно будет продлить её вручную.
                </p>
                <p className="text-chocolate/50 text-xs leading-relaxed">
                  Вы можете включить автопродление в любой момент для удобства.
                </p>
              </>
            )}
          </div>

          {/* Actions */}
          <div className="flex flex-col gap-3">
            {isEnabled ? (
              <button
                onClick={handleToggle}
                className="w-full py-3 px-4 bg-surface-light border-2 border-chocolate/20 text-chocolate/70 rounded-xl font-medium text-sm hover:bg-chocolate/5 hover:border-chocolate/30 transition-colors active:scale-[0.98]"
              >
                Отключить автопродление
              </button>
            ) : (
              <button
                onClick={handleToggle}
                className="w-full py-3 px-4 bg-primary text-white rounded-xl font-semibold text-sm shadow-lg shadow-primary/30 hover:bg-[#d54d26] transition-colors active:scale-[0.98]"
              >
                Включить автопродление
              </button>
            )}
            <button
              onClick={onClose}
              className="w-full py-3 px-4 text-chocolate/60 text-sm font-medium hover:text-chocolate/80 transition-colors active:scale-[0.98]"
            >
              Закрыть
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

