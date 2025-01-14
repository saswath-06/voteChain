import { openai } from './client';
import type { AIAnalysisResult } from './client';
import type { Proposal } from '@/types/graphql';

const ANALYSIS_PROMPT = `Analyze this DAO proposal and provide:
1. A concise summary (2-3 sentences)
2. Potential impact on the DAO
3. Key risks or concerns
4. Voting recommendations with reasoning
5. Overall sentiment (positive/neutral/negative)

Proposal:`;

export async function analyzeProposal(proposal: Proposal): Promise<AIAnalysisResult> {
  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: "You are a DAO governance expert analyzing proposals. Be concise and objective."
        },
        {
          role: "user",
          content: `${ANALYSIS_PROMPT}\n${proposal.description}`
        }
      ],
      temperature: 0.3,
    });

    const response = completion.choices[0].message.content;
    return parseAnalysisResponse(response);
  } catch (error) {
    console.error('Error analyzing proposal:', error);
    throw error;
  }
}

function parseAnalysisResponse(response: string): AIAnalysisResult {
  // Simple parsing implementation - could be made more robust
  const sections = response.split('\n\n');
  
  return {
    summary: sections[0]?.replace('Summary: ', '') ?? '',
    impact: sections[1]?.replace('Impact: ', '') ?? '',
    risks: sections[2]?.replace('Risks: ', '').split('\n- ').filter(Boolean) ?? [],
    recommendations: sections[3]?.replace('Recommendations: ', '').split('\n- ').filter(Boolean) ?? [],
    sentiment: determineSentiment(sections[4] ?? ''),
  };
}

function determineSentiment(sentimentText: string): AIAnalysisResult['sentiment'] {
  const text = sentimentText.toLowerCase();
  if (text.includes('positive')) return 'positive';
  if (text.includes('negative')) return 'negative';
  return 'neutral';
}