import { gql } from '@apollo/client';

export const PROPOSALS_QUERY = gql`
  query GetProposals($first: Int!, $skip: Int!, $orderBy: String!, $orderDirection: String!, $where: Proposal_filter) {
    proposals(
      first: $first
      skip: $skip
      orderBy: $orderBy
      orderDirection: $orderDirection
      where: $where
    ) {
      id
      proposalId
      description
      status
      forVotes
      againstVotes
      abstainVotes
      startBlock
      endBlock
      quorumVotes
      createdAt
      proposer {
        id
      }
    }
  }
`;

export const PROPOSAL_VOTES_QUERY = gql`
  query GetProposalVotes($proposalId: String!, $first: Int!, $skip: Int!) {
    votes(
      first: $first
      skip: $skip
      where: { proposal: $proposalId }
    ) {
      id
      voter {
        id
      }
      support
      weight
      reason
    }
  }
`;

export const DAO_STATS_QUERY = gql`
  query GetDaoStats($daoAddress: String!) {
    dao(id: $daoAddress) {
      id
      proposalCount
      totalVotes
      activeProposals
      quorum
      votingPeriod
      votingDelay
    }
  }
`;

export const GET_PROPOSALS = gql`
  query GetProposals($daoAddress: String!, $first: Int!, $skip: Int!) {
    proposals(
      where: { dao: $daoAddress }
      first: $first
      skip: $skip
      orderBy: createdAt
      orderDirection: desc
    ) {
      id
      proposalId
      description
      status
      forVotes
      againstVotes
      abstainVotes
      startBlock
      endBlock
      createdAt
      proposer {
        id
      }
    }
  }
`;
