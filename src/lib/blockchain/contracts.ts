import { createPublicClient, http, Address } from 'viem'
import { mainnet } from 'viem/chains'
import { governorABI } from './abis/governor'

const client = createPublicClient({
  chain: mainnet,
  transport: http()
})

export async function getProposalVotes(
  governorAddress: Address,
  proposalId: bigint
) {
  try {
    const [forVotes, againstVotes, abstainVotes] = await client.multicall({
      contracts: [
        {
          address: governorAddress,
          abi: governorABI,
          functionName: 'proposalVotes',
          args: [proposalId]
        }
      ]
    })

    return {
      for: forVotes,
      against: againstVotes,
      abstain: abstainVotes,
      error: null
    }
  } catch (error) {
    return {
      for: 0n,
      against: 0n,
      abstain: 0n,
      error
    }
  }
}