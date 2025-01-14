import { useQuery } from '@apollo/client';
import { PROPOSALS_QUERY } from '@/lib/graphql/queries';
import type { ProposalsQueryResult } from '@/types/graphql';

export function useProposals(
  daoAddress: string,
  {
    first = 10,
    skip = 0,
    orderBy = 'createdAt',
    orderDirection = 'desc',
  } = {}
) {
  return useQuery<ProposalsQueryResult>(PROPOSALS_QUERY, {
    variables: {
      first,
      skip,
      orderBy,
      orderDirection,
      where: {
        dao: daoAddress.toLowerCase(),
      },
    },
    notifyOnNetworkStatusChange: true,
  });
}
