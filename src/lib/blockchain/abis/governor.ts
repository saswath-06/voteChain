export const governorABI = [
    {
      inputs: [{ internalType: 'uint256', name: 'proposalId', type: 'uint256' }],
      name: 'proposalVotes',
      outputs: [
        { internalType: 'uint256', name: 'againstVotes', type: 'uint256' },
        { internalType: 'uint256', name: 'forVotes', type: 'uint256' },
        { internalType: 'uint256', name: 'abstainVotes', type: 'uint256' }
      ],
      stateMutability: 'view',
      type: 'function'
    }
  ] as const
