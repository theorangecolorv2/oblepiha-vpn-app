import { useEffect, useState, useCallback } from 'react'

const API_URL = import.meta.env.PROD
  ? 'https://oblepiha-app.ru/api'
  : 'http://localhost:8000/api'

interface TopReferrer {
  telegram_id: number
  username: string | null
  first_name: string | null
  referral_count: number
}

interface Stats {
  active_subscriptions: number
  new_users_today: number
  trials_today: number
  expiring_today: number
  expiring_tomorrow: number
  auto_renew_enabled: number
  channel_bonus_today: number
  channel_bonus_total: number
  referrals_total: number
  top_referrers: TopReferrer[]
  trial_users_total: number
  trial_converted: number
  trial_conversion_percent: number
  total_users: number
  generated_at: string
}

type Tab = 'overview' | 'details'

function App() {
  const [isAuthorized, setIsAuthorized] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState('')
  const [initData, setInitData] = useState('')
  const [stats, setStats] = useState<Stats | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('overview')

  const fetchStats = useCallback(async (token: string) => {
    try {
      const response = await fetch(`${API_URL}/admin/stats`, {
        headers: { 'X-Telegram-Init-Data': token },
      })
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (e) {
      console.error('Failed to fetch stats:', e)
    }
  }, [])

  const handleRefresh = async () => {
    if (!initData || isRefreshing) return
    setIsRefreshing(true)
    await fetchStats(initData)
    setIsRefreshing(false)
  }

  useEffect(() => {
    const checkAccess = async () => {
      const tg = window.Telegram?.WebApp
      if (!tg) {
        setError('Telegram WebApp not available')
        setIsLoading(false)
        return
      }

      tg.ready()
      tg.expand()

      const token = tg.initData
      if (!token) {
        setError('No init data')
        setIsLoading(false)
        return
      }

      setInitData(token)

      try {
        const response = await fetch(`${API_URL}/admin/me`, {
          headers: { 'X-Telegram-Init-Data': token },
        })

        if (response.ok) {
          setIsAuthorized(true)
          await fetchStats(token)
        } else if (response.status === 403) {
          setError('Доступ запрещён')
        } else {
          setError(`Ошибка: ${response.status}`)
        }
      } catch (e) {
        setError(`Ошибка сети: ${e}`)
      }

      setIsLoading(false)
    }

    checkAccess()
  }, [fetchStats])

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p>Загрузка...</p>
      </div>
    )
  }

  if (!isAuthorized) {
    return (
      <div className="error-container">
        <h1>⛔</h1>
        <p>{error || 'У вас нет прав для просмотра этой страницы.'}</p>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p>Загрузка статистики...</p>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="header">
        <h1>📊 Аналитика</h1>
        <button
          className={`refresh-btn ${isRefreshing ? 'loading' : ''}`}
          onClick={handleRefresh}
          disabled={isRefreshing}
        >
          <span className="icon">↻</span>
          {isRefreshing ? 'Обновление...' : 'Обновить'}
        </button>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Обзор
        </button>
        <button
          className={`tab ${activeTab === 'details' ? 'active' : ''}`}
          onClick={() => setActiveTab('details')}
        >
          Детали
        </button>
      </div>

      {activeTab === 'overview' ? (
        <OverviewTab stats={stats} />
      ) : (
        <DetailsTab stats={stats} />
      )}

      <div className="footer">
        Обновлено: {stats.generated_at}
      </div>
    </div>
  )
}

function OverviewTab({ stats }: { stats: Stats }) {
  return (
    <>
      {/* Основные метрики */}
      <div className="stats-grid">
        <div className="stat-card highlight">
          <div className="stat-label">Активных подписок</div>
          <div className="stat-value">{stats.active_subscriptions}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Всего юзеров</div>
          <div className="stat-value">{stats.total_users}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Новых сегодня</div>
          <div className="stat-value">{stats.new_users_today}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Триалов сегодня</div>
          <div className="stat-value">{stats.trials_today}</div>
        </div>
      </div>

      {/* Истекающие подписки */}
      <div className="section">
        <div className="section-title">⏰ Истекающие подписки</div>
        <div className="expiring-cards">
          <div className={`expiring-card ${stats.expiring_today > 0 ? 'danger' : ''}`}>
            <div className="expiring-icon">🔴</div>
            <div className="expiring-count">{stats.expiring_today}</div>
            <div className="expiring-label">Сегодня</div>
          </div>
          <div className={`expiring-card ${stats.expiring_tomorrow > 0 ? 'warning' : ''}`}>
            <div className="expiring-icon">🟡</div>
            <div className="expiring-count">{stats.expiring_tomorrow}</div>
            <div className="expiring-label">Завтра</div>
          </div>
        </div>
      </div>

      {/* Конверсия */}
      <div className="section">
        <div className="section-title">📈 Конверсия Trial → Платный</div>
        <div className="conversion-container">
          <div className="conversion-header">
            <span className="conversion-label">Процент конверсии</span>
            <span className="conversion-value">{stats.trial_conversion_percent}%</span>
          </div>
          <div className="conversion-bar">
            <div
              className="conversion-fill"
              style={{ width: `${Math.min(stats.trial_conversion_percent, 100)}%` }}
            />
          </div>
          <div className="conversion-details">
            <span>Всего триалов: {stats.trial_users_total}</span>
            <span>Конвертировано: {stats.trial_converted}</span>
          </div>
        </div>
      </div>
    </>
  )
}

function DetailsTab({ stats }: { stats: Stats }) {
  const getRankClass = (index: number) => {
    if (index === 0) return 'gold'
    if (index === 1) return 'silver'
    if (index === 2) return 'bronze'
    return ''
  }

  return (
    <>
      {/* Дополнительные метрики */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Автопродления</div>
          <div className="stat-value">{stats.auto_renew_enabled}</div>
          <div className="stat-subtitle">включено</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Рефералов</div>
          <div className="stat-value">{stats.referrals_total}</div>
          <div className="stat-subtitle">всего</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Бонус за канал</div>
          <div className="stat-value">{stats.channel_bonus_today}</div>
          <div className="stat-subtitle">сегодня</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Бонус за канал</div>
          <div className="stat-value">{stats.channel_bonus_total}</div>
          <div className="stat-subtitle">всего</div>
        </div>
      </div>

      {/* Топ рефереров */}
      <div className="section">
        <div className="section-title">🏆 Топ-5 рефереров</div>
        <div className="referrers-table">
          {stats.top_referrers.length > 0 ? (
            stats.top_referrers.map((referrer, index) => (
              <div key={referrer.telegram_id} className="referrer-row">
                <div className={`referrer-rank ${getRankClass(index)}`}>
                  {index + 1}
                </div>
                <div className="referrer-info">
                  <div className="referrer-name">
                    {referrer.first_name || 'Пользователь'}
                  </div>
                  <div className="referrer-username">
                    {referrer.username ? `@${referrer.username}` : `ID: ${referrer.telegram_id}`}
                  </div>
                </div>
                <div className="referrer-count">{referrer.referral_count}</div>
              </div>
            ))
          ) : (
            <div className="no-data">Пока нет рефереров</div>
          )}
        </div>
      </div>
    </>
  )
}

export default App
