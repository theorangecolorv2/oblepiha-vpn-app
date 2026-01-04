interface AutoRenewModalProps {
  isOpen: boolean
  isEnabled: boolean
  hasPaymentMethod: boolean
  paymentMethodType: string | null
  cardLast4: string | null
  cardBrand: string | null
  sbpPhone: string | null
  onClose: () => void
  onToggle: (enabled: boolean) => void
  onDeletePaymentMethod: () => void
}

// Получить название типа платёжного метода на русском
function getPaymentMethodName(type: string | null): string {
  switch (type) {
    case 'bank_card': return 'Банковская карта'
    case 'sbp': return 'СБП'
    case 'sber_pay': return 'SberPay'
    case 'tinkoff_bank': return 'T-Pay'
    case 'yoo_money': return 'ЮMoney'
    case 'mir_pay': return 'Mir Pay'
    default: return 'Способ оплаты'
  }
}

// Получить иконку для типа платёжного метода
function getPaymentMethodIcon(type: string | null): string {
  switch (type) {
    case 'bank_card': return 'credit_card'
    case 'sbp': return 'account_balance'
    case 'sber_pay': return 'account_balance'
    case 'tinkoff_bank': return 'account_balance'
    case 'yoo_money': return 'wallet'
    case 'mir_pay': return 'credit_card'
    default: return 'payments'
  }
}

export function AutoRenewModal({
  isOpen,
  isEnabled,
  hasPaymentMethod,
  paymentMethodType,
  cardLast4,
  cardBrand,
  sbpPhone,
  onClose,
  onToggle,
  onDeletePaymentMethod
}: AutoRenewModalProps) {
  if (!isOpen) return null

  const handleToggle = () => {
    onToggle(!isEnabled)
  }

  const handleDeletePaymentMethod = () => {
    const methodName = getPaymentMethodName(paymentMethodType)
    if (confirm(`Вы уверены, что хотите удалить сохранённый способ оплаты (${methodName})? Автопродление будет отключено.`)) {
      onDeletePaymentMethod()
    }
  }

  // Формируем отображение платёжного метода
  const renderPaymentMethodInfo = () => {
    if (paymentMethodType === 'bank_card' && cardLast4 && cardBrand) {
      return `${cardBrand} •••• ${cardLast4}`
    }
    if (paymentMethodType === 'sbp') {
      return sbpPhone ? `СБП •••• ${sbpPhone}` : 'СБП'
    }
    return getPaymentMethodName(paymentMethodType)
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
                  {hasPaymentMethod
                    ? 'Вы можете включить автопродление в любой момент для удобства.'
                    : 'Чтобы включить автопродление, оплатите подписку с галочкой "Подключить автопродление".'}
                </p>
              </>
            )}

            {/* Информация о способе оплаты */}
            {hasPaymentMethod && paymentMethodType && (
              <div className="mt-4 p-3 bg-chocolate/5 rounded-xl border border-chocolate/10">
                <div className="flex items-center gap-2 mb-2">
                  <span className="material-symbols-outlined text-chocolate/60 text-lg">
                    {getPaymentMethodIcon(paymentMethodType)}
                  </span>
                  <span className="text-chocolate/80 text-xs font-medium">
                    Сохранённый способ оплаты
                  </span>
                </div>
                <div className="text-chocolate font-medium text-sm">
                  {renderPaymentMethodInfo()}
                </div>
              </div>
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
                disabled={!hasPaymentMethod}
                className="w-full py-3 px-4 bg-primary text-white rounded-xl font-semibold text-sm shadow-lg shadow-primary/30 hover:bg-[#d54d26] transition-colors active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Включить автопродление
              </button>
            )}

            {/* Кнопка удаления способа оплаты */}
            {hasPaymentMethod && (
              <button
                onClick={handleDeletePaymentMethod}
                className="w-full py-3 px-4 bg-red-50 border-2 border-red-200 text-red-600 rounded-xl font-medium text-sm hover:bg-red-100 hover:border-red-300 transition-colors active:scale-[0.98]"
              >
                Удалить способ оплаты
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

