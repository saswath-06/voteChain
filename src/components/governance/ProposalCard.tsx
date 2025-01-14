// src/components/governance/ProposalCard.tsx
import { formatEther } from 'viem'
import { ProposalVotingChart } from '../charts/ProposalVotingChart'

interface ProposalCardProps {
  proposal: {
    id: string
    proposalId: string
    description: string
    status: string
    forVotes: string
    againstVotes: string
    abstainVotes: string
    createdAt: string
  }
}

export function ProposalCard({ proposal }: ProposalCardProps) {
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">
            Proposal #{proposal.proposalId}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Created at {new Date(proposal.createdAt).toLocaleDateString()}
          </p>
        </div>
        <span className={`px-2 py-1 text-sm rounded-full ${
          proposal.status === 'active' 
            ? 'bg-green-100 text-green-800'
            : 'bg-gray-100 text-gray-800'
        }`}>
          {proposal.status}
        </span>
      </div>

      <p className="mt-4 text-gray-700">{proposal.description}</p>

      <div className="mt-6">
        <h4 className="text-sm font-medium text-gray-900">Voting Results</h4>
        <ProposalVotingChart
          forVotes={proposal.forVotes}
          againstVotes={proposal.againstVotes}
          abstainVotes={proposal.abstainVotes}
        />
      </div>
    </div>
  )
}