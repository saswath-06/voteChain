import { Address } from 'viem'

export interface ProposalVotes {
  for: bigint
  against: bigint
  abstain: bigint
  error: Error | null
}

export interface Web3State {
  address: Address | undefined
  isConnected: boolean
  chainId: number | undefined
  chainName: string | undefined
}
