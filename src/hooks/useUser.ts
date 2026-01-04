import { useEffect, useState, useCallback } from 'react'
import { api } from '../api'
import type { UserStats, UserResponse } from '../api'
import type { Tariff } from '../types'
import { mockUserData } from '../config'

// Проверка наличия Telegram initData
function hasTelegramAuth(): boolean {
  return !!(typeof window !== 'undefined' && window.Telegram?.WebApp?.initData)
}

interface UseUserReturn {
  // Состояние загрузки
  isLoading: boolean
  error: string | null

  // Данные пользователя
  stats: UserStats | null
  tariffs: Tariff[]
  user: UserResponse | null

  // Mock режим (для скриншотов без Telegram)
  isMockMode: boolean

  // Методы
  refreshStats: () => Promise<void>
  createPayment: (tariffId: string) => Promise<string | null>
  acceptTerms: () => Promise<void>
  refreshUser: () => Promise<void>
  toggleAutoRenew: (enabled: boolean) => Promise<void>
  deletePaymentMethod: () => Promise<void>
}

export function useUser(): UseUserReturn {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [tariffs, setTariffs] = useState<Tariff[]>([])
  const [user, setUser] = useState<UserResponse | null>(null)

  // Флаг: используем моковые данные (нет Telegram auth)
  const useMockData = !hasTelegramAuth()

  // Загрузка данных при монтировании
  useEffect(() => {
    async function loadData() {
      setIsLoading(true)
      setError(null)

      // Если нет Telegram auth - используем моковые данные
      if (useMockData) {
        console.log('[useUser] No Telegram auth, using mock data')
        setUser(mockUserData.user as UserResponse)
        setStats(mockUserData.stats)

        // Тарифы всё равно грузим с сервера (они публичные)
        try {
          const tariffsResponse = await api.getTariffs()
          setTariffs(tariffsResponse)
        } catch (err) {
          console.error('Failed to get tariffs:', err)
          setTariffs([])
        }

        setIsLoading(false)
        return
      }

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
  }, [useMockData])

  // Обновить статистику
  const refreshStats = useCallback(async () => {
    if (useMockData) {
      console.log('[useUser] Mock mode: refreshStats skipped')
      return
    }
    try {
      const newStats = await api.getUserStats()
      setStats(newStats)
    } catch (err) {
      console.error('Failed to refresh stats:', err)
    }
  }, [useMockData])

  // Создать платёж (всегда с сохранением способа оплаты - пользователь соглашается в виджете YooKassa)
  const createPayment = useCallback(async (tariffId: string): Promise<string | null> => {
    console.log('[useUser] createPayment called with tariffId:', tariffId)
    try {
      const payment = await api.createPayment(tariffId, true) // Всегда true - согласие в виджете YooKassa
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
    if (useMockData) {
      console.log('[useUser] Mock mode: acceptTerms - updating mock user')
      setUser(prev => prev ? { ...prev, termsAcceptedAt: new Date().toISOString() } : prev)
      return
    }
    try {
      await api.acceptTerms()
      // Обновляем данные пользователя после принятия условий
      const updatedUser = await api.getCurrentUser()
      setUser(updatedUser)
    } catch (err) {
      console.error('[useUser] Failed to accept terms:', err)
      throw err
    }
  }, [useMockData])

  // Обновить данные пользователя
  const refreshUser = useCallback(async () => {
    if (useMockData) {
      console.log('[useUser] Mock mode: refreshUser skipped')
      return
    }
    try {
      const updatedUser = await api.getCurrentUser()
      setUser(updatedUser)
    } catch (err) {
      console.error('[useUser] Failed to refresh user:', err)
    }
  }, [useMockData])

  // Переключить автопродление
  const toggleAutoRenew = useCallback(async (enabled: boolean) => {
    if (useMockData) {
      console.log('[useUser] Mock mode: toggleAutoRenew', enabled)
      setUser(prev => prev ? { ...prev, autoRenewEnabled: enabled } : prev)
      return
    }
    try {
      if (enabled) {
        await api.enableAutoRenew()
      } else {
        await api.disableAutoRenew()
      }
      const updatedUser = await api.getCurrentUser()
      setUser(updatedUser)
    } catch (err) {
      console.error('[useUser] Failed to toggle auto-renew:', err)
      throw err
    }
  }, [useMockData])

  // Удалить способ оплаты
  const deletePaymentMethod = useCallback(async () => {
    if (useMockData) {
      console.log('[useUser] Mock mode: deletePaymentMethod')
      setUser(prev => prev ? {
        ...prev,
        hasPaymentMethod: false,
        paymentMethodType: null,
        cardLast4: null,
        cardBrand: null,
        sbpPhone: null,
        autoRenewEnabled: false,
      } : prev)
      return
    }
    try {
      await api.deletePaymentMethod()
      const updatedUser = await api.getCurrentUser()
      setUser(updatedUser)
    } catch (err) {
      console.error('[useUser] Failed to delete payment method:', err)
      throw err
    }
  }, [useMockData])

  return {
    isLoading,
    error,
    stats,
    tariffs,
    user,
    isMockMode: useMockData,
    refreshStats,
    createPayment,
    acceptTerms,
    refreshUser,
    toggleAutoRenew,
    deletePaymentMethod,
  }
}
