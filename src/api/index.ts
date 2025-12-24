/**
 * API клиент для работы с бэкендом
 */

import { config } from '../config'
import type { Tariff } from '../types'

// Типы ответов API
export interface UserStats {
  isActive: boolean
  daysLeft: number
  totalDays: number
  trafficLeftGb: number
  totalTrafficGb: number
  subscriptionUrl: string | null
}

export interface UserResponse {
  id: number
  telegramId: number
  telegramUsername: string | null
  firstName: string | null
  isActive: boolean
  subscriptionExpiresAt: string | null
  daysLeft: number
  subscriptionUrl: string | null
  trafficUsedBytes: number
  trafficLimitBytes: number
  referralCode: string | null
}

export interface PaymentResponse {
  paymentId: string
  confirmationUrl: string
  amount: number
  tariffId: string
  tariffName: string
}

export interface PaymentStatus {
  paymentId: string
  status: string
  paid: boolean
}

// Получить initData из Telegram WebApp
function getInitData(): string {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp.initData || ''
  }
  return ''
}

// Базовый fetch с авторизацией
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const initData = getInitData()
  const url = `${config.apiUrl}${endpoint}`
  
  console.log('[API] Request:', options.method || 'GET', url)
  console.log('[API] Has initData:', !!initData, initData ? `(${initData.length} chars)` : '')
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  
  // Добавляем initData в заголовок для авторизации
  if (initData) {
    headers['X-Telegram-Init-Data'] = initData
  } else {
    console.warn('[API] No Telegram initData available - request may fail auth')
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...(options.headers as Record<string, string> || {}),
      },
    })
    
    console.log('[API] Response status:', response.status)
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      console.error('[API] Error response:', error)
      throw new Error(error.detail || `HTTP ${response.status}`)
    }
    
    const data = await response.json()
    console.log('[API] Response data:', data)
    return data
  } catch (err) {
    console.error('[API] Fetch error:', err)
    throw err
  }
}

/**
 * API методы
 */
export const api = {
  /**
   * Получить список тарифов
   */
  async getTariffs(): Promise<Tariff[]> {
    return apiFetch<Tariff[]>('/api/tariffs')
  },
  
  /**
   * Получить данные текущего пользователя
   * Создаёт пользователя если он новый
   */
  async getCurrentUser(): Promise<UserResponse> {
    return apiFetch<UserResponse>('/api/users/me')
  },
  
  /**
   * Получить статистику для главного экрана
   */
  async getUserStats(): Promise<UserStats> {
    return apiFetch<UserStats>('/api/users/me/stats')
  },
  
  /**
   * Создать платёж для покупки тарифа
   */
  async createPayment(tariffId: string): Promise<PaymentResponse> {
    return apiFetch<PaymentResponse>('/api/payments', {
      method: 'POST',
      body: JSON.stringify({ tariff_id: tariffId }),
    })
  },
  
  /**
   * Проверить статус платежа
   */
  async getPaymentStatus(paymentId: string): Promise<PaymentStatus> {
    return apiFetch<PaymentStatus>(`/api/payments/${paymentId}/status`)
  },
}
