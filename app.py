from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
import os
import json
from dotenv import load_dotenv
import openai
import web3

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')
mongo = PyMongo(app)

# OpenAI Configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

# Web3 Configuration
w3 = web3.Web3(web3.HTTPProvider(os.getenv('ETHEREUM_PROVIDER_URL')))

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app.json_encoder = JSONEncoder

@app.route('/api/proposals', methods=['GET'])
def get_proposals():
    """
    Retrieve all proposals from the database
    """
    try:
        proposals = list(mongo.db.proposals.find())
        return jsonify(proposals), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proposals', methods=['POST'])
def create_proposal():
    """
    Create a new proposal
    """
    try:
        proposal_data = request.json
        
        # AI-powered proposal analysis
        ai_prediction = analyze_proposal_with_ai(proposal_data)
        
        # Add AI prediction to proposal
        proposal_data['ai_prediction'] = ai_prediction
        
        # Save to MongoDB
        result = mongo.db.proposals.insert_one(proposal_data)
        
        return jsonify({
            'message': 'Proposal created successfully',
            'proposal_id': str(result.inserted_id),
            'ai_prediction': ai_prediction
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proposals/<proposal_id>/vote', methods=['POST'])
def vote_on_proposal(proposal_id):
    """
    Process a vote on a specific proposal
    """
    try:
        vote_data = request.json
        
        # Validate blockchain wallet signature
        is_valid_signature = validate_blockchain_signature(vote_data)
        
        if not is_valid_signature:
            return jsonify({'error': 'Invalid voter signature'}), 403
        
        # Update proposal votes in MongoDB
        update_result = mongo.db.proposals.update_one(
            {'_id': ObjectId(proposal_id)},
            {'$inc': {
                f'votes.{vote_data["vote_direction"]}': 1,
                'votes.total_participants': 1
            }}
        )
        
        return jsonify({
            'message': 'Vote recorded successfully',
            'modified_count': update_result.modified_count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_proposal_with_ai(proposal_data):
    """
    Use OpenAI to predict proposal success
    """
    try:
        # Prepare prompt for AI analysis
        prompt = f"""Analyze the potential success of this governance proposal. 
        Provide a numeric probability of success (0-1) based on:
        - Clarity of proposal
        - Potential impact
        - Alignment with organizational goals

        Proposal Details:
        Title: {proposal_data.get('title', 'Untitled')}
        Description: {proposal_data.get('description', 'No description')}

        Response Format:
        Success Probability: [0-1 float]
        Reasoning: [Brief explanation]
        """
        
        # Generate AI prediction
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant analyzing governance proposals."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        # Extract success probability
        ai_response = response.choices[0].message.content
        success_probability = extract_success_probability(ai_response)
        
        return success_probability
    except Exception as e:
        print(f"AI analysis error: {e}")
        return 0.5  # Default 50% if analysis fails

def validate_blockchain_signature(vote_data):
    """
    Validate voter's blockchain signature
    """
    try:
        # Implement signature verification logic
        # This is a placeholder - actual implementation depends on specific blockchain
        signer = w3.eth.account.recover_message(
            vote_data['message'], 
            signature=vote_data['signature']
        )
        
        # Verify signer matches the voting wallet
        return signer.lower() == vote_data['voter_address'].lower()
    except Exception as e:
        print(f"Signature validation error: {e}")
        return False

def extract_success_probability(ai_text):
    """
    Extract success probability from AI-generated text
    """
    try:
        # Look for a float between 0 and 1
        import re
        match = re.search(r'Success Probability:\s*(\d+\.\d+)', ai_text)
        if match:
            return float(match.group(1))
        
        # Fallback parsing if format is different
        match = re.search(r'(\d+\.\d+)', ai_text)
        if match:
            probability = float(match.group(1))
            return max(0, min(1, probability))
        
        return 0.5  # Default if no probability found
    except Exception as e:
        print(f"Probability extraction error: {e}")
        return 0.5

@app.route('/api/analytics', methods=['GET'])
def get_governance_analytics():
    """
    Retrieve comprehensive governance analytics
    """
    try:
        # Aggregate analytics from MongoDB
        analytics = mongo.db.proposals.aggregate([
            {
                '$group': {
                    '_id': None,
                    'total_proposals': {'$sum': 1},
                    'avg_ai_prediction': {'$avg': '$ai_prediction'},
                    'total_votes': {'$sum': '$votes.total_participants'}
                }
            }
        ])
        
        return jsonify(list(analytics)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
