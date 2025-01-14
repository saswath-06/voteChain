import { useProposals } from '@/hooks/useProposals';
import { formatEther } from 'viem';

export function ProposalList({ daoAddress }: { daoAddress: string }) {
  const { data, loading, error } = useProposals(daoAddress);

  if (loading) return <div>Loading proposals...</div>;
  if (error) return <div>Error loading proposals: {error.message}</div>;

  return (
    <div className="space-y-4">
      {data?.proposals.map((proposal) => (
        <div key={proposal.id} className="p-4 border rounded-lg">
          <h3 className="text-lg font-medium">{proposal.description}</h3>
          <div className="mt-2 grid grid-cols-3 gap-4">
            <div>
              For: {formatEther(BigInt(proposal.forVotes))}
            </div>
            <div>
              Against: {formatEther(BigInt(proposal.againstVotes))}
            </div>
            <div>
              Abstain: {formatEther(BigInt(proposal.abstainVotes))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}