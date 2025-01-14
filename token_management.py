import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')

mongo = PyMongo(app)

class GovernanceTokenManager:
    @classmethod
    def allocate_initial_tokens(cls, user_id: str, allocation_type: str = 'signup') -> dict:
        """
        Allocate initial governance tokens to a user
        """
        allocation_rules = {
            'signup': 100,
            'proposal_creation': 50,
            'successful_proposal': 200,
            'active_voter': 25
        }
        
        token_amount = allocation_rules.get(allocation_type, 0)
        
        try:
            # Update user's token balance
            result = mongo.db.users.update_one(
                {'_id': user_id},
                {'$inc': {'governance_tokens': token_amount},
                 '$push': {
                     'token_history': {
                         'transaction_id': str(uuid.uuid4()),
                         'type': allocation_type,
                         'amount': token_amount,
                         'timestamp': datetime.utcnow()
                     }
                 }
                }
            )
            
            return {
                'allocated_tokens': token_amount,
                'allocation_type': allocation_type,
                'success': result.modified_count > 0
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    @classmethod
    def transfer_tokens(cls, from_user_id: str, to_user_id: str, amount: int) -> dict:
        """
        Transfer governance tokens between users
        """
        try:
            # Check sender's balance
            sender = mongo.db.users.find_one({'_id': from_user_id})
            if not sender or sender.get('governance_tokens', 0) < amount:
                return {
                    'error': 'Insufficient tokens',
                    'success': False
                }
            
            # Perform token transfer
            transfer_result = mongo.db.users.bulk_write([
                # Deduct from sender
                mongo.db.users.update_one(
                    {'_id': from_user_id},
                    {'$inc': {'governance_tokens': -amount},
                     '$push': {
                         'token_history': {
                             'transaction_id': str(uuid.uuid4()),
                             'type': 'token_transfer_out',
                             'amount': -amount,
                             'to_user': to_user_id,
                             'timestamp': datetime.utcnow()
                         }
                     }
                    }
                ),
                # Add to recipient
                mongo.db.users.update_one(
                    {'_id': to_user_id},
                    {'$inc': {'governance_tokens': amount},
                     '$push': {
                         'token_history': {
                             'transaction_id': str(uuid.uuid4()),
                             'type': 'token_transfer_in',
                             'amount': amount,
                             'from_user': from_user_id,
                             'timestamp': datetime.utcnow()
                         }
                     }
                    }
                )
            ])
            
            return {
                'transferred_tokens': amount,
                'success': transfer_result.modified_count == 2
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    @classmethod
    def get_token_history(cls, user_id: str) -> dict:
        """
        Retrieve token transaction history for a user
        """
        try:
            user = mongo.db.users.find_one({'_id': user_id})
            if not user:
                return {
                    'error': 'User not found',
                    'success': False
                }
            
            return {
                'current_balance': user.get('governance_tokens', 0),
                'token_history': user.get('token_history', []),
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }

@app.route('/api/tokens/allocate', methods=['POST'])
def allocate_tokens():
    """
    Endpoint for token allocation
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        allocation_type = data.get('allocation_type', 'signup')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        result = GovernanceTokenManager.allocate_initial_tokens(user_id, allocation_type)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tokens/transfer', methods=['POST'])
def transfer_tokens():
    """
    Endpoint for token transfer
    """
    try:
        data = request.json
        from_user_id = data.get('from_user_id')
        to_user_id = data.get('to_user_id')
        amount = data.get('amount')
        
        if not all([from_user_id, to_user_id, amount]):
            return jsonify({'error': 'All fields are required'}), 400
        
        result = GovernanceTokenManager.transfer_tokens(from_user_id, to_user_id, amount)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tokens/history', methods=['GET'])
def get_token_history():
    """
    Endpoint to retrieve token transaction history
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        result = GovernanceTokenManager.get_token_history(user_id)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
