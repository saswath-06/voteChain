import { useState, useCallback } from 'react';
import { analyzeProposal } from '@/lib/ai/proposalAnalysis';
import type { AIAnalysisResult } from '@/lib/ai/client';
import type { Proposal } from '@/types/graphql';

export function useProposalAnalysis() {
  const [analysis, setAnalysis] = useState<AIAnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const analyze = useCallback(async (proposal: Proposal) => {
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const result = await analyzeProposal(proposal);
      setAnalysis(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Analysis failed');
      setError(error);
      throw error;
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  return {
    analysis,
    isAnalyzing,
    error,
    analyze,
  };
}