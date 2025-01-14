export interface Proposal {
    id: string;
    proposalId: string;
    description: string;
    proposer: {
      id: string;
    };
    status: string;
    forVotes: string;
    againstVotes: string;
    abstainVotes: string;
    startBlock: string;
    endBlock: string;
    quorumVotes: string;
    createdAt: string;
  }
  
  export interface Vote {
    id: string;
    voter: {
      id: string;
    };
    support: boolean;
    weight: string;
    reason: string;
    proposal: Proposal;
  }
  
  export interface ProposalsQueryResult {
    proposals: Proposal[];
  }
  
  export interface VotesQueryResult {
    votes: Vote[];
  }
