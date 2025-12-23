import type { Tariff } from '../types'

export const tariffs: Tariff[] = [
  {
    id: 'trial',
    name: '3 дня',
    description: 'Пробный',
    price: 10,
    days: 3,
    icon: 'trial',
  },
  {
    id: 'month',
    name: '1 Месяц',
    description: 'Самый популярный',
    price: 199,
    days: 30,
    icon: 'month',
  },
  {
    id: 'quarter',
    name: '3 Месяца',
    description: 'Выгодно',
    price: 549,
    days: 90,
    icon: 'quarter',
  },
]

