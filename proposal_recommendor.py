import openai
import json
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ProposalRecommendationSystem:
    def __init__(self, api_key: str):
        """
        Initialize OpenAI client and recommendation system
        """
        openai.api_key = api_key
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def generate_embeddings(self, proposals: List[Dict[str, Any]]) -> np.ndarray:
        """
        Generate TF-IDF embeddings for proposals
        
        Args:
            proposals (List[Dict]): List of proposal dictionaries
        
        Returns:
            Numpy array of embeddings
        """
        # Combine title and description for embedding
        proposal_texts = [
            f"{proposal.get('title', '')} {proposal.get('description', '')}" 
            for proposal in proposals
        ]
        
        # Generate TF-IDF embeddings
        embeddings = self.vectorizer.fit_transform(proposal_texts)
        return embeddings

    def find_similar_proposals(self, 
                                new_proposal: Dict[str, Any], 
                                existing_proposals: List[Dict[str, Any]], 
                                top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar proposals using semantic similarity
        
        Args:
            new_proposal (Dict): The proposal to find similar matches for
            existing_proposals (List[Dict]): List of existing proposals
            top_k (int): Number of top similar proposals to return
        
        Returns:
            List of top similar proposals
        """
        # Generate embeddings
        all_proposals = existing_proposals + [new_proposal]
        embeddings = self.generate_embeddings(all_proposals)
        
        # Compute similarity
        new_proposal_embedding = embeddings[-1]
        existing_embeddings = embeddings[:-1]
        
        similarities = cosine_similarity(new_proposal_embedding, existing_embeddings)[0]
        
        # Get top K similar proposals
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [existing_proposals[i] for i in top_indices]

    def ai_recommend_proposal_modifications(self, 
                                            new_proposal: Dict[str, Any], 
                                            similar_proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use AI to generate recommendations based on similar past proposals
        
        Args:
            new_proposal (Dict): The new proposal to analyze
            similar_proposals (List[Dict]): Similar historical proposals
        
        Returns:
            Dict with AI-generated recommendations
        """
        try:
            # Prepare similar proposals summary
            similar_proposals_summary = self._summarize_similar_proposals(similar_proposals)
            
            # Generate AI recommendation
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an AI advisor specializing in 
                        proposal optimization for organizational governance."""
                    },
                    {
                        "role": "user", 
                        "content": f"""Analyze a new proposal in context of similar 
                        historical proposals and provide comprehensive recommendations.

                        New Proposal Details:
                        {json.dumps(new_proposal, indent=2)}

                        Similar Historical Proposals Summary:
                        {similar_proposals_summary}

                        Provide detailed recommendations including:
                        1. Potential Improvement Suggestions
                        2. Potential Risks or Challenges
                        3. Comparative Analysis with Similar Proposals
                        4. Recommended Modifications

                        Response Format:
                        {{
                            "improvement_suggestions": [str],
                            "potential_risks": [str],
                            "comparative_analysis": str,
                            "recommended_modifications": [str],
                            "success_probability_boost": float
                        }}"""
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=350
            )
            
            # Parse the JSON response
            recommendations = json.loads(response.choices[0].message.content)
            return recommendations
        
        except Exception as e:
            print(f"Proposal Recommendation Error: {e}")
            return {
                "improvement_suggestions": [],
                "potential_risks": [],
                "comparative_analysis": "Recommendation generation failed",
                "recommended_modifications": [],
                "success_probability_boost": 0
            }

    def _summarize_similar_proposals(self, similar_proposals: List[Dict[str, Any]]) -> str:
        """
        Create a summary of similar proposals
        
        Args:
            similar_proposals (List[Dict]): List of similar proposals
        
        Returns:
            Summarized proposals as a string
        """
        summary = []
        for proposal in similar_proposals:
            summary.append({
                "title": proposal.get('title', 'Untitled'),
                "key_points": proposal.get('description', '')[:200] + '...',
                "outcome": proposal.get('outcome', 'Unknown')
            })
        return json.dumps(summary, indent=2)

    def generate_comprehensive_proposal_analysis(self, 
                                                 new_proposal: Dict[str, Any], 
                                                 existing_proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive proposal analysis combining multiple AI techniques
        
        Args:
            new_proposal (Dict): The new proposal to analyze
            existing_proposals (List[Dict]): Existing proposals in the system
        
        Returns:
            Comprehensive proposal analysis
        """
        # Find similar proposals
        similar_proposals = self.find_similar_proposals(new_proposal, existing_proposals)
        
        # Generate AI recommendations
        ai_recommendations = self.ai_recommend_proposal_modifications(
            new_proposal, 
            similar_proposals
        )
        
        # Combine analysis results
        comprehensive_analysis = {
            "new_proposal": new_proposal,
            "similar_proposals": similar_proposals,
            "ai_recommendations": ai_recommendations
        }
        
        return comprehensive_analysis

def main():
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Sample existing proposals
    existing_proposals = [
        {
            "title": "Implement Blockchain Voting",
            "description": "Proposal to integrate blockchain technology for more transparent voting",
            "outcome": "Partially Approved"
        },
        {
            "title": "AI-Powered Governance Tools",
            "description": "Develop AI tools to assist in decision-making processes",
            "outcome": "Approved"
        }
    ]
    
    # New proposal to analyze
    new_proposal = {
        "title": "Enhanced Governance Analytics Platform",
        "description": "Develop a comprehensive platform for tracking and analyzing organizational decisions"
    }
    
    recommender = ProposalRecommendationSystem(os.getenv('OPENAI_API_KEY'))
    
    # Perform comprehensive analysis
    analysis = recommender.generate_comprehensive_proposal_analysis(
        new_proposal, 
        existing_proposals
    )
    
    print(json.dumps(analysis, indent=2))

if __name__ == "__main__":
    main()
