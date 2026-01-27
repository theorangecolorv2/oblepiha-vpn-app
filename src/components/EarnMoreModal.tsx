import { STRINGS } from '../constants'

interface EarnMoreModalProps {
  isOpen: boolean
  onClose: () => void
  supportUrl: string
}

export function EarnMoreModal({ isOpen, onClose, supportUrl }: EarnMoreModalProps) {
  if (!isOpen) return null

  const handleContactSupport = () => {
    const tg = window.Telegram?.WebApp
    if (tg?.openTelegramLink) {
      tg.openTelegramLink(supportUrl)
    } else {
      window.open(supportUrl, '_blank')
    }
    onClose()
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="bg-surface-light rounded-3xl w-full max-w-sm p-6 shadow-xl animate-[fadeInZoom_0.2s_ease-out_forwards]"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
              <span className="material-symbols-outlined text-[24px] text-primary">
                payments
              </span>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-chocolate/5 flex items-center justify-center hover:bg-chocolate/10 transition-colors"
            >
              <span className="material-symbols-outlined text-[20px] text-chocolate/60">
                close
              </span>
            </button>
          </div>

          {/* Title */}
          <h3 className="text-xl font-bold text-chocolate mb-3">
            {STRINGS.REFERRAL_EARN_MORE_TITLE}
          </h3>

          {/* Content */}
          <p className="text-chocolate/70 text-sm leading-relaxed mb-6">
            {STRINGS.REFERRAL_EARN_MORE_TEXT}
          </p>

          {/* Button */}
          <button
            onClick={handleContactSupport}
            className="w-full py-4 px-6 bg-primary text-white rounded-2xl font-semibold text-lg flex items-center justify-center gap-2 shadow-lg shadow-primary/30 active:scale-[0.98] transition-all"
          >
            <span className="material-symbols-outlined text-[20px]">chat</span>
            {STRINGS.REFERRAL_EARN_MORE_BUTTON}
          </button>
        </div>
      </div>
    </>
  )
}
