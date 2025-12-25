import { config } from '../config'

interface TermsAgreementModalProps {
  isOpen: boolean
  onAgree: () => void
}

export function TermsAgreementModal({ isOpen, onAgree }: TermsAgreementModalProps) {
  if (!isOpen) return null

  const termsUrl = config.termsUrl || '#'

  const handleTermsClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (termsUrl && termsUrl !== '#') {
      // Если это относительный путь, открываем в той же вкладке
      // Если это внешняя ссылка, открываем в новой
      if (termsUrl.startsWith('/')) {
        window.location.href = termsUrl
      } else {
        window.open(termsUrl, '_blank')
      }
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/40 z-40 backdrop-blur-sm"
        onClick={(e) => e.stopPropagation()}
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
          <div className="flex items-center justify-center mb-5">
            <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
              <span className="material-symbols-outlined text-primary text-2xl">
                description
              </span>
            </div>
          </div>

          {/* Content */}
          <div className="mb-6 text-center">
            <p className="text-chocolate text-base leading-relaxed">
              Продолжая, вы согласны с{' '}
              <button
                onClick={handleTermsClick}
                className="text-primary font-semibold underline underline-offset-2 hover:text-[#d54d26] transition-colors"
              >
                условиями пользования
              </button>
            </p>
          </div>

          {/* Action */}
          <button
            onClick={onAgree}
            className="w-full py-4 px-4 bg-primary text-white rounded-xl font-semibold text-base shadow-lg shadow-primary/30 hover:bg-[#d54d26] transition-colors active:scale-[0.98]"
          >
            Согласен
          </button>
        </div>
      </div>
    </>
  )
}

