import openai
import json
from typing import Dict, List

class ProposalSentimentAnalyzer:
    def __init__(self, api_key: str):
        """
        Initialize OpenAI client for sentiment analysis
        """
        openai.api_key = api_key

    def analyze_proposal_sentiment(self, proposal_text: str) -> Dict[str, float]:
        """
        Perform comprehensive sentiment analysis on a proposal
        
        Args:
            proposal_text (str): Full text of the proposal to analyze
        
        Returns:
            Dict containing sentiment scores
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an advanced sentiment analysis AI 
                        specialized in evaluating governance proposals. 
                        Provide detailed sentiment analysis with numeric scores."""
                    },
                    {
                        "role": "user", 
                        "content": f"""Perform a comprehensive sentiment analysis 
                        on the following proposal text. Provide scores from -1 (very negative) 
                        to 1 (very positive) for the following dimensions:
                        1. Overall Sentiment
                        2. Potential Impact
                        3. Innovation Level
                        4. Clarity of Proposal
                        5. Community Alignment

                        Proposal Text:
                        {proposal_text}

                        Response Format:
                        {{
                            "overall_sentiment": float,
                            "potential_impact": float,
                            "innovation_level": float,
                            "clarity": float,
                            "community_alignment": float,
                            "detailed_analysis": str
                        }}"""
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.6,
                max_tokens=300
            )
            
            # Parse the JSON response
            analysis = json.loads(response.choices[0].message.content)
            return analysis
        
        except Exception as e:
            print(f"Sentiment Analysis Error: {e}")
            return {
                "overall_sentiment": 0,
                "potential_impact": 0,
                "innovation_level": 0,
                "clarity": 0,
                "community_alignment": 0,
                "detailed_analysis": "Analysis failed"
            }

    def batch_analyze_proposals(self, proposals: List[str]) -> List[Dict[str, float]]:
        """
        Analyze multiple proposals in batch
        
        Args:
            proposals (List[str]): List of proposal texts
        
        Returns:
            List of sentiment analysis results
        """
        return [self.analyze_proposal_sentiment(proposal) for proposal in proposals]

def main():
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    analyzer = ProposalSentimentAnalyzer(os.getenv('OPENAI_API_KEY'))
    
    sample_proposal = """
    We propose implementing a new governance mechanism 
    that increases transparency and reduces decision-making time 
    by 40% through the use of advanced blockchain technologies 
    and AI-powered analytics.
    """
    
    result = analyzer.analyze_proposal_sentiment(sample_proposal)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
