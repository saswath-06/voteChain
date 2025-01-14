import { useAccount, useNetwork, useSignMessage } from 'wagmi'
import { useCallback } from 'react'

export function useWeb3() {
  const { address, isConnected } = useAccount()
  const { chain } = useNetwork()
  const { signMessageAsync } = useSignMessage()

  const signMessage = useCallback(async (message: string) => {
    try {
      const signature = await signMessageAsync({ message })
      return { signature, error: null }
    } catch (error) {
      return { signature: null, error }
    }
  }, [signMessageAsync])

  return {
    address,
    isConnected,
    chainId: chain?.id,
    chainName: chain?.name,
    signMessage,
  }
}