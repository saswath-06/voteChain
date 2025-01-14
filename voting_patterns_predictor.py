import openai
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class VotingPatternPredictor:
    def __init__(self, api_key: str):
        """
        Initialize OpenAI client for voting pattern prediction
        """
        openai.api_key = api_key

    def predict_voting_pattern(self, historical_data: pd.DataFrame, new_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict voting pattern for a new proposal based on historical data
        
        Args:
            historical_data (pd.DataFrame): Historical voting data
            new_proposal (dict): Details of the new proposal
        
        Returns:
            Dict with voting prediction insights
        """
        try:
            # Prepare historical data summary
            data_summary = self._summarize_historical_data(historical_data)
            
            # Prepare proposal details
            proposal_details = self._format_proposal_details(new_proposal)
            
            # Generate AI-powered prediction
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an advanced AI analyzing voting patterns 
                        for organizational governance. Provide a comprehensive 
                        prediction of voting behavior."""
                    },
                    {
                        "role": "user", 
                        "content": f"""Analyze the potential voting pattern for a new proposal 
                        based on historical voting data and proposal characteristics.

                        Historical Data Summary:
                        {data_summary}

                        New Proposal Details:
                        {proposal_details}

                        Provide a detailed prediction including:
                        1. Estimated Voting Success Probability
                        2. Potential Voting Bloc Breakdown
                        3. Factors Influencing Voter Decision
                        4. Recommended Proposal Modifications

                        Response Format:
                        {{
                            "success_probability": float,
                            "voting_bloc_breakdown": {{
                                "supporters": float,
                                "neutral": float,
                                "opponents": float
                            }},
                            "key_influencing_factors": [str],
                            "modification_recommendations": [str],
                            "detailed_analysis": str
                        }}"""
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=350
            )
            
            # Parse the JSON response
            prediction = openai.json.loads(response.choices[0].message.content)
            return prediction
        
        except Exception as e:
            print(f"Voting Pattern Prediction Error: {e}")
            return {
                "success_probability": 0.5,
                "voting_bloc_breakdown": {
                    "supporters": 0.33,
                    "neutral": 0.34,
                    "opponents": 0.33
                },
                "key_influencing_factors": [],
                "modification_recommendations": [],
                "detailed_analysis": "Prediction failed"
            }

    def _summarize_historical_data(self, historical_data: pd.DataFrame) -> str:
        """
        Create a summary of historical voting data
        
        Args:
            historical_data (pd.DataFrame): Historical voting data
        
        Returns:
            Summarized data as a string
        """
        summary = {
            "total_proposals": len(historical_data),
            "avg_success_rate": historical_data['passed'].mean(),
            "most_common_topics": historical_data['topic'].value_counts().head().to_dict(),
            "voting_participation_rate": historical_data['total_votes'].mean(),
        }
        return str(summary)

    def _format_proposal_details(self, proposal: Dict[str, Any]) -> str:
        """
        Format proposal details for AI analysis
        
        Args:
            proposal (dict): Proposal details
        
        Returns:
            Formatted proposal details as a string
        """
        return "\n".join([
            f"{key}: {value}" for key, value in proposal.items()
        ])

def main():
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Create sample historical data
    historical_data = pd.DataFrame({
        'proposal_id': range(1, 51),
        'topic': np.random.choice(['Finance', 'Technology', 'HR', 'Strategy'], 50),
        'passed': np.random.choice([True, False], 50),
        'total_votes': np.random.randint(100, 1000, 50)
    })
    
    # Sample new proposal
    new_proposal = {
        'title': 'Implement AI-Powered Governance Tools',
        'category': 'Technology',
        'budget_impact': 'Moderate',
        'strategic_alignment': 'High'
    }
    
    predictor = VotingPatternPredictor(os.getenv('OPENAI_API_KEY'))
    
    prediction = predictor.predict_voting_pattern(historical_data, new_proposal)
    print(json.dumps(prediction, indent=2))

if __name__ == "__main__":
    main()
