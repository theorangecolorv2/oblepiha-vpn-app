import { useEffect, useState, useCallback } from 'react'
import { api } from '../api'
import type { UserStats, UserResponse } from '../api'
import type { Tariff } from '../types'

interface UseUserReturn {
  // Состояние загрузки
  isLoading: boolean
  error: string | null
  
  // Данные пользователя
  stats: UserStats | null
  tariffs: Tariff[]
  user: UserResponse | null
  
  // Методы
  refreshStats: () => Promise<void>
  createPayment: (tariffId: string, setupAutoRenew?: boolean) => Promise<string | null>
  acceptTerms: () => Promise<void>
  refreshUser: () => Promise<void>
}

export function useUser(): UseUserReturn {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [tariffs, setTariffs] = useState<Tariff[]>([])
  const [user, setUser] = useState<UserResponse | null>(null)

  // Загрузка данных при монтировании
  useEffect(() => {
    async function loadData() {
      setIsLoading(true)
      setError(null)

      try {
        // Загружаем параллельно: пользователя, статистику и тарифы
        const [userResponse, statsResponse, tariffsResponse] = await Promise.all([
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

        if (userResponse) {
          setUser(userResponse)
        }

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
  const createPayment = useCallback(async (tariffId: string, setupAutoRenew = false): Promise<string | null> => {
    console.log('[useUser] createPayment called with tariffId:', tariffId, 'setupAutoRenew:', setupAutoRenew)
    try {
      const payment = await api.createPayment(tariffId, setupAutoRenew)
      console.log('[useUser] Payment created:', payment)
      return payment.confirmationUrl
    } catch (err) {
      console.error('[useUser] Failed to create payment:', err)
      const errorMessage = err instanceof Error ? err.message : 'Ошибка создания платежа'
      setError(errorMessage)
      throw err // Пробрасываем ошибку наверх для обработки в handlePayment
    }
  }, [])

  // Принять условия пользования
  const acceptTerms = useCallback(async () => {
    try {
      await api.acceptTerms()
      // Обновляем данные пользователя после принятия условий
      const updatedUser = await api.getCurrentUser()
      setUser(updatedUser)
    } catch (err) {
      console.error('[useUser] Failed to accept terms:', err)
      throw err
    }
  }, [])

  // Обновить данные пользователя
  const refreshUser = useCallback(async () => {
    try {
      const updatedUser = await api.getCurrentUser()
      setUser(updatedUser)
    } catch (err) {
      console.error('[useUser] Failed to refresh user:', err)
    }
  }, [])

  return {
    isLoading,
    error,
    stats,
    tariffs,
    user,
    refreshStats,
    createPayment,
    acceptTerms,
    refreshUser,
  }
}
