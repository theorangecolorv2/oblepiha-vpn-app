import { useState, useEffect } from 'react'
import { api } from '../api'
import { STRINGS } from '../constants'
import { config } from '../config'
import type { ReferralStats } from '../types'
import { EarnMoreModal } from './EarnMoreModal'

function StatCard({ value, label }: { value: number; label: string }) {
  return (
    <div className="bg-surface-light rounded-2xl p-4 text-center shadow-soft">
      <div className="text-2xl font-bold text-chocolate">{value}</div>
      <div className="text-xs text-chocolate/60 mt-1">{label}</div>
    </div>
  )
}

export function ReferralScreen() {
  const [stats, setStats] = useState<ReferralStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [copied, setCopied] = useState(false)
  const [showEarnMoreModal, setShowEarnMoreModal] = useState(false)

  useEffect(() => {
    api.getReferralStats()
      .then(setStats)
      .catch(err => console.error('[Referral] Failed to load stats:', err))
      .finally(() => setIsLoading(false))
  }, [])

  const handleShare = () => {
    if (!stats) return

    const text = 'Попробуйте Облепиха VPN — быстрый и надёжный VPN'
    const tg = window.Telegram?.WebApp

    if (tg?.openTelegramLink) {
      // Шаринг через Telegram
      tg.openTelegramLink(
        `https://t.me/share/url?url=${encodeURIComponent(stats.referralLink)}&text=${encodeURIComponent(text)}`
      )
    } else {
      // Fallback: копируем ссылку
      handleCopy()
    }
  }

  const handleCopy = async () => {
    if (!stats) return

    try {
      await navigator.clipboard.writeText(stats.referralLink)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('[Referral] Failed to copy:', err)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-chocolate/60">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="flex flex-col">
      {/* Заголовок */}
      <div className="text-center mb-6">
        <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
          <span className="material-symbols-outlined text-[32px] text-primary">
            group_add
          </span>
        </div>
        <h2 className="text-2xl font-bold text-chocolate mb-2">
          {STRINGS.REFERRAL_TITLE}
        </h2>
        <p className="text-chocolate/60 text-sm">
          {STRINGS.REFERRAL_SUBTITLE}
        </p>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <StatCard
          value={stats?.totalInvited || 0}
          label={STRINGS.REFERRAL_STATS_INVITED}
        />
        <StatCard
          value={stats?.totalPurchased || 0}
          label={STRINGS.REFERRAL_STATS_PURCHASED}
        />
        <StatCard
          value={stats?.totalBonusDays || 0}
          label={STRINGS.REFERRAL_STATS_EARNED}
        />
      </div>

      {/* Описание */}
      <div className="bg-primary/5 rounded-2xl p-4 mb-6">
        <p className="text-chocolate/80 text-sm leading-relaxed">
          {STRINGS.REFERRAL_DESCRIPTION}
        </p>
      </div>

      {/* Кнопки */}
      <div className="flex flex-col gap-3">
        <button
          onClick={handleShare}
          className="w-full py-4 px-6 bg-primary text-white rounded-2xl font-semibold text-lg flex items-center justify-center gap-2 shadow-lg shadow-primary/30 active:scale-[0.98] transition-all"
        >
          <span className="material-symbols-outlined text-[20px]">share</span>
          {STRINGS.REFERRAL_SHARE_BUTTON}
        </button>

        <button
          onClick={handleCopy}
          className="w-full py-4 px-6 bg-background-light text-chocolate rounded-2xl font-semibold text-lg flex items-center justify-center gap-2 hover:bg-white active:scale-[0.98] transition-all"
        >
          <span className="material-symbols-outlined text-[20px]">
            {copied ? 'check' : 'content_copy'}
          </span>
          {copied ? STRINGS.REFERRAL_LINK_COPIED : STRINGS.REFERRAL_COPY_BUTTON}
        </button>
      </div>

      {/* Кнопка "Хочу заработать" */}
      <div className="mt-8 text-center">
        <button
          onClick={() => setShowEarnMoreModal(true)}
          className="text-primary text-sm font-semibold hover:underline"
        >
          {STRINGS.REFERRAL_EARN_MORE} →
        </button>
      </div>

      {/* Модальное окно */}
      <EarnMoreModal
        isOpen={showEarnMoreModal}
        onClose={() => setShowEarnMoreModal(false)}
        supportUrl={config.supportTg}
      />
    </div>
  )
}
