// src/components/charts/ProposalVotingChart.tsx
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { formatEther } from 'viem'

interface VotingChartProps {
  forVotes: string
  againstVotes: string
  abstainVotes: string
}

export function ProposalVotingChart({ forVotes, againstVotes, abstainVotes }: VotingChartProps) {
  const data = [
    { name: 'For', value: Number(formatEther(BigInt(forVotes))), color: '#22c55e' },
    { name: 'Against', value: Number(formatEther(BigInt(againstVotes))), color: '#ef4444' },
    { name: 'Abstain', value: Number(formatEther(BigInt(abstainVotes))), color: '#94a3b8' }
  ]

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            dataKey="value"
            label={({ name, value }) => `${name}: ${value.toFixed(2)}`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}