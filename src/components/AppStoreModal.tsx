import { config } from '../config'

interface AppStoreModalProps {
  isOpen: boolean
  onClose: () => void
}

export function AppStoreModal({ isOpen, onClose }: AppStoreModalProps) {
  if (!isOpen) return null

  const handleGlobal = () => {
    window.open(config.happDownload.ios, '_blank')
    onClose()
  }

  const handleRussia = () => {
    window.open(config.happDownload.iosRu, '_blank')
    onClose()
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-end justify-center animate-fade-in"
      onClick={onClose}
    >
      <div
        className="bg-white w-full max-w-md rounded-t-3xl p-6 pb-8 animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-bold text-chocolate">Выберите App Store</h3>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-chocolate/5 flex items-center justify-center"
            >
              <span className="material-symbols-outlined text-chocolate/50 text-xl">close</span>
            </button>
          </div>

          <button
            onClick={handleGlobal}
            className="w-full p-4 bg-chocolate/5 hover:bg-chocolate/10 active:scale-[0.98] rounded-2xl flex items-center gap-4 transition-all"
          >
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center text-white">
              <span className="material-symbols-outlined text-2xl">language</span>
            </div>
            <div className="flex flex-col items-start">
              <span className="font-semibold text-chocolate">App Store Global</span>
              <span className="text-xs text-chocolate/50">Для аккаунтов не из РФ</span>
            </div>
          </button>

          <button
            onClick={handleRussia}
            className="w-full p-4 bg-chocolate/5 hover:bg-chocolate/10 active:scale-[0.98] rounded-2xl flex items-center gap-4 transition-all"
          >
            <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center text-white text-2xl">
              🇷🇺
            </div>
            <div className="flex flex-col items-start">
              <span className="font-semibold text-chocolate">App Store Россия</span>
              <span className="text-xs text-chocolate/50">Для российских аккаунтов</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}
