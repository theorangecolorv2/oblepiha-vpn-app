export interface Tariff {
  id: string
  name: string
  description: string
  price: number
  days: number
  icon: 'trial' | 'month' | 'quarter'
}

export interface UserData {
  firstName: string
  isActive: boolean
  daysLeft: number
  trafficUsedGb: number
}

export type VpnStatus = 'active' | 'inactive' | 'connecting'

