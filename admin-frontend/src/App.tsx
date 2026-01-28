import { useEffect, useState } from 'react'

const API_URL = import.meta.env.PROD
  ? 'https://oblepiha-app.ru/api'
  : 'http://localhost:8000/api'

function App() {
  const [isAuthorized, setIsAuthorized] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [userName, setUserName] = useState('')
  const [error, setError] = useState('')

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

      const initData = tg.initData
      if (!initData) {
        setError('No init data')
        setIsLoading(false)
        return
      }

      try {
        const response = await fetch(`${API_URL}/admin/me`, {
          headers: {
            'X-Telegram-Init-Data': initData,
          },
        })

        if (response.ok) {
          const data = await response.json()
          setIsAuthorized(true)
          setUserName(data.first_name)
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
  }, [])

  if (isLoading) {
    return (
      <div className="container">
        <p>Загрузка...</p>
      </div>
    )
  }

  if (!isAuthorized) {
    return (
      <div className="container">
        <h1>⛔ Доступ запрещён</h1>
        <p>{error || 'У вас нет прав для просмотра этой страницы.'}</p>
      </div>
    )
  }

  return (
    <div className="container">
      <h1>📊 Аналитика</h1>
      <p>Привет, {userName}!</p>
      <p className="placeholder">Здесь будет аналитика...</p>
    </div>
  )
}

export default App
