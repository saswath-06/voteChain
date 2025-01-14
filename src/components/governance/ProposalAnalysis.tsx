import { useProposalAnalysis } from '@/hooks/useProposalAnalysis';
import type { Proposal } from '@/types/graphql';

type Props = {
  proposal: Proposal;
};

export function ProposalAnalysis({ proposal }: Props) {
  const { analysis, isAnalyzing, error, analyze } = useProposalAnalysis();

  return (
    <div className="space-y-4">
      {!analysis && !isAnalyzing && (
        <button
          onClick={() => analyze(proposal)}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Analyze Proposal
        </button>
      )}

      {isAnalyzing && (
        <div className="text-gray-600">Analyzing proposal...</div>
      )}

      {error && (
        <div className="text-red-600">
          Error analyzing proposal: {error.message}
        </div>
      )}

      {analysis && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">AI Analysis</h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="font-medium">Summary</h4>
              <p className="text-gray-700">{analysis.summary}</p>
            </div>

            <div>
              <h4 className="font-medium">Potential Impact</h4>
              <p className="text-gray-700">{analysis.impact}</p>
            </div>

            <div>
              <h4 className="font-medium">Key Risks</h4>
              <ul className="list-disc pl-4">
                {analysis.risks.map((risk, i) => (
                  <li key={i} className="text-gray-700">{risk}</li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-medium">Recommendations</h4>
              <ul className="list-disc pl-4">
                {analysis.recommendations.map((rec, i) => (
                  <li key={i} className="text-gray-700">{rec}</li>
                ))}
              </ul>
            </div>

            <div className="flex items-center gap-2">
              <h4 className="font-medium">Sentiment:</h4>
              <span className={`px-2 py-1 rounded text-sm ${
                analysis.sentiment === 'positive' ? 'bg-green-100 text-green-800' :
                analysis.sentiment === 'negative' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {analysis.sentiment.charAt(0).toUpperCase() + analysis.sentiment.slice(1)}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
