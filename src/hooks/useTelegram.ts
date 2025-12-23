import { useEffect, useState } from 'react'
import { config, devUser } from '../config'

export type UserOS = 'ios' | 'android' | 'windows'

// Определение ОС из Telegram или browser
function detectOS(tgPlatform?: string): UserOS {
  // Если есть платформа от Telegram
  if (tgPlatform) {
    if (tgPlatform === 'ios' || tgPlatform === 'macos') return 'ios'
    if (tgPlatform === 'android') return 'android'
    if (tgPlatform === 'tdesktop') {
      // tdesktop может быть на Windows, Mac или Linux - пробуем определить по navigator
      if (typeof navigator !== 'undefined') {
        const userAgent = navigator.userAgent.toLowerCase()
        if (userAgent.includes('win')) return 'windows'
        if (userAgent.includes('mac')) return 'ios'
      }
      return 'windows'
    }
    // weba, webk - веб версии, определяем по userAgent
    if (tgPlatform === 'weba' || tgPlatform === 'webk') {
      if (typeof navigator !== 'undefined') {
        const userAgent = navigator.userAgent.toLowerCase()
        if (userAgent.includes('iphone') || userAgent.includes('ipad') || userAgent.includes('mac')) return 'ios'
        if (userAgent.includes('win')) return 'windows'
      }
      return 'android'
    }
  }

  // Fallback определение по navigator
  if (typeof navigator !== 'undefined') {
    const userAgent = navigator.userAgent.toLowerCase()
    if (userAgent.includes('iphone') || userAgent.includes('ipad') || userAgent.includes('mac')) return 'ios'
    if (userAgent.includes('win')) return 'windows'
  }

  // По умолчанию Android
  return 'android'
}

// Хук для работы с Telegram Web App
export function useTelegram() {
  const [isReady, setIsReady] = useState(false)
  
  const tg = typeof window !== 'undefined' ? window.Telegram?.WebApp : null

  useEffect(() => {
    if (tg) {
      tg.ready()
      tg.expand()
      setIsReady(true)
    } else if (config.devMode) {
      setIsReady(true)
    }
  }, [tg])

  // Получаем имя пользователя из Telegram или тестовые данные
  const user = tg?.initDataUnsafe?.user
  const firstName = user?.first_name || (config.devMode ? devUser.firstName : 'Гость')

  // Определяем ОС пользователя
  const userOS = detectOS(tg?.platform)

  return {
    tg,
    isReady,
    firstName,
    user,
    userOS,
  }
}

