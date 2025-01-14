// src/components/views/DashboardView.tsx
import { useAccount } from 'wagmi'
import { useQuery } from '@apollo/client'
import { GET_PROPOSALS } from '@/lib/graphql/queries'
import { ProposalCard } from '../governance/ProposalCard'
import { ConnectButton } from '../web3/ConnectButton'

export function DashboardView() {
  const { address, isConnected } = useAccount()
  const { data, loading, error } = useQuery(GET_PROPOSALS, {
    variables: {
      daoAddress: process.env.NEXT_PUBLIC_DEFAULT_DAO_ADDRESS,
      first: 10,
      skip: 0
    },
    skip: !isConnected
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">DAO Dashboard</h1>
            </div>
            <div className="flex items-center">
              <ConnectButton />
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!isConnected ? (
          <div className="text-center py-12">
            <h2 className="text-xl font-medium text-gray-900">
              Connect your wallet to view DAO proposals
            </h2>
          </div>
        ) : loading ? (
          <div className="animate-pulse space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-48 bg-gray-200 rounded-lg" />
            ))}
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">Error loading proposals: {error.message}</p>
          </div>
        ) : (
          <div className="space-y-6">
            {data?.proposals.map((proposal) => (
              <ProposalCard key={proposal.id} proposal={proposal} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
