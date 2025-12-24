import { useEffect, useState, useCallback } from 'react'
import { api } from '../api'
import type { UserStats } from '../api'
import type { Tariff } from '../types'

interface UseUserReturn {
  // Состояние загрузки
  isLoading: boolean
  error: string | null
  
  // Данные пользователя
  stats: UserStats | null
  tariffs: Tariff[]
  
  // Методы
  refreshStats: () => Promise<void>
  createPayment: (tariffId: string) => Promise<string | null>
}

export function useUser(): UseUserReturn {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [tariffs, setTariffs] = useState<Tariff[]>([])

  // Загрузка данных при монтировании
  useEffect(() => {
    async function loadData() {
      setIsLoading(true)
      setError(null)

      try {
        // Загружаем параллельно: пользователя, статистику и тарифы
        const [, statsResponse, tariffsResponse] = await Promise.all([
          api.getCurrentUser().catch(err => {
            console.error('Failed to get user:', err)
            return null
          }),
          api.getUserStats().catch(err => {
            console.error('Failed to get stats:', err)
            return null
          }),
          api.getTariffs().catch(err => {
            console.error('Failed to get tariffs:', err)
            return []
          }),
        ])

        if (statsResponse) {
          setStats(statsResponse)
        }
        
        setTariffs(tariffsResponse)
        
      } catch (err) {
        console.error('Failed to load user data:', err)
        setError(err instanceof Error ? err.message : 'Ошибка загрузки данных')
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [])

  // Обновить статистику
  const refreshStats = useCallback(async () => {
    try {
      const newStats = await api.getUserStats()
      setStats(newStats)
    } catch (err) {
      console.error('Failed to refresh stats:', err)
    }
  }, [])

  // Создать платёж
  const createPayment = useCallback(async (tariffId: string): Promise<string | null> => {
    try {
      const payment = await api.createPayment(tariffId)
      return payment.confirmationUrl
    } catch (err) {
      console.error('Failed to create payment:', err)
      setError(err instanceof Error ? err.message : 'Ошибка создания платежа')
      return null
    }
  }, [])

  return {
    isLoading,
    error,
    stats,
    tariffs,
    refreshStats,
    createPayment,
  }
}
