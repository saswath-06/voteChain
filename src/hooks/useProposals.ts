import { useQuery } from '@apollo/client';
import { PROPOSAL_VOTES_QUERY } from '@/lib/graphql/queries';
import type { VotesQueryResult } from '@/types/graphql';

export function useProposalVotes(
  proposalId: string,
  {
    first = 1000,
    skip = 0,
  } = {}
) {
  return useQuery<VotesQueryResult>(PROPOSAL_VOTES_QUERY, {
    variables: {
      proposalId,
      first,
      skip,
    },
    notifyOnNetworkStatusChange: true,
  });
}
