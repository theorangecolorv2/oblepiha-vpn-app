type TabId = 'shop' | 'vpn' | 'friends'

interface BottomNavProps {
  activeTab: TabId
  onTabChange: (tab: TabId) => void
}

const tabs: { id: TabId; label: string; icon: string }[] = [
  { id: 'shop', label: 'Подписка', icon: 'shopping_bag' },
  { id: 'vpn', label: 'Подключение', icon: 'power_settings_new' },
  { id: 'friends', label: 'Рефералы', icon: 'group' },
]

export function BottomNav({ activeTab, onTabChange }: BottomNavProps) {
  return (
    <div className="fixed bottom-6 left-0 right-0 px-4 z-50">
      <nav className="mx-auto max-w-sm w-full bg-chocolate text-white rounded-2xl p-2 shadow-xl flex items-center justify-between">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              flex flex-1 flex-col items-center justify-center gap-1 py-2 rounded-xl transition-all
              ${activeTab === tab.id 
                ? 'text-primary' 
                : 'text-white/50 hover:text-white hover:bg-white/10'
              }
            `}
          >
            <span className="material-symbols-outlined">{tab.icon}</span>
            <span className="text-[10px] font-medium leading-none">{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}

export type { TabId }
