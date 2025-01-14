import { useWeb3Modal } from '@web3modal/wagmi/react'
import { useWeb3 } from '@/hooks/useWeb3'

export function ConnectButton() {
  const { open } = useWeb3Modal()
  const { isConnected, address } = useWeb3()

  if (isConnected && address) {
    return (
      <button
        onClick={() => open()}
        className="px-4 py-2 rounded-lg bg-primary-100 text-primary-900 hover:bg-primary-200 transition-colors"
      >
        {`${address.slice(0, 6)}...${address.slice(-4)}`}
      </button>
    )
  }

  return (
    <button
      onClick={() => open()}
      className="px-4 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-700 transition-colors"
    >
      Connect Wallet
    </button>
  )
}