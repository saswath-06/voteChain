// src/components/providers/Web3Provider.tsx
import { createWeb3Modal, defaultWagmiConfig } from '@web3modal/wagmi/react'
import { WagmiConfig } from 'wagmi'
import { arbitrum, mainnet } from 'viem/chains'
import { PropsWithChildren } from 'react'

if (!process.env.NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID) {
  throw new Error('Missing NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID')
}

const projectId = process.env.NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID

const metadata = {
  name: 'DAO Dashboard',
  description: 'Governance analytics platform for DAOs',
  url: 'https://dao-dashboard.com',
  icons: ['https://avatars.githubusercontent.com/u/37784886']
}

const chains = [mainnet, arbitrum]
const wagmiConfig = defaultWagmiConfig({ chains, projectId, metadata })

createWeb3Modal({ wagmiConfig, projectId, chains })

export function Web3Provider({ children }: PropsWithChildren) {
  return <WagmiConfig config={wagmiConfig}>{children}</WagmiConfig>
}