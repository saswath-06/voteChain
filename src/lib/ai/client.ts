import OpenAI from 'openai';

export const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  dangerouslyAllowBrowser: true // Note: In production, we'd want to proxy through our backend
});

export type AIAnalysisResult = {
  summary: string;
  impact: string;
  risks: string[];
  recommendations: string[];
  sentiment: 'positive' | 'neutral' | 'negative';
};
