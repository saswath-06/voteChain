import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from datetime import datetime
import uuid
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')

mongo = PyMongo(app)

class AuditLogger:
    @classmethod
    def log_event(cls, 
                  user_id: str, 
                  event_type: str, 
                  event_description: str, 
                  additional_metadata: dict = None) -> dict:
        """
        Log an event to the audit trail
        
        Args:
            user_id (str): ID of the user performing the action
            event_type (str): Type of event (e.g., 'proposal_created', 'vote_cast')
            event_description (str): Detailed description of the event
            additional_metadata (dict, optional): Extra information about the event
        
        Returns:
            Dict with logging result
        """
        try:
            # Prepare audit log entry
            audit_log = {
                '_id': str(uuid.uuid4()),
                'user_id': user_id,
                'event_type': event_type,
                'event_description': event_description,
                'timestamp': datetime.utcnow(),
                'ip_address': request.remote_addr if request else None,
                'user_agent': request.user_agent.string if request and request.user_agent else None,
                'additional_metadata': additional_metadata or {}
            }
            
            # Insert log entry
            result = mongo.db.audit_logs.insert_one(audit_log)
            
            return {
                'log_id': str(result.inserted_id),
                'success': result.acknowledged
            }
        except Exception as e:
            print(f"Audit Logging Error: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    @classmethod
    def get_user_audit_trail(cls, user_id: str, days: int = 30) -> dict:
        """
        Retrieve audit trail for a specific user
        
        Args:
            user_id (str): ID of the user
            days (int): Number of past days to retrieve logs for
        
        Returns:
            Dict with user's audit logs
        """
        try:
            # Calculate date threshold
            date_threshold = datetime.utcnow() - timedelta(days=days)
            
            # Retrieve audit logs
            audit_logs = list(mongo.db.audit_logs.find({
                'user_id': user_id,
                'timestamp': {'$gte': date_threshold}
            }).sort('timestamp', -1))
            
            return {
                'audit_logs': audit_logs,
                'total_logs': len(audit_logs),
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    @classmethod
    def analyze_suspicious_activities(cls, user_id: str = None) -> dict:
        """
        Detect potentially suspicious activities
        
        Args:
            user_id (str, optional): Specific user to analyze
        
        Returns:
            Dict with suspicious activity analysis
        """
        try:
            # Aggregate suspicious activity criteria
            pipeline = [
                # Optional user filter
                *([{'$match': {'user_id': user_id}}] if user_id else []),
                
                # Group by event type and count
                {'$group': {
                    '_id': '$event_type',
                    'total_events': {'$sum': 1},
                    'unique_users': {'$addToSet': '$user_id'}
                }},
                
                # Identify potential suspicious patterns
                {'$match': {
                    'total_events': {'$gt': 10}  # More than 10 events of same type
                }},
                
                # Sort by event count
                {'$sort': {'total_events': -1}}
            ]
            
            suspicious_activities = list(mongo.db.audit_logs.aggregate(pipeline))
            
            return {
                'suspicious_activities': suspicious_activities,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }

@app.route('/api/audit/log', methods=['POST'])
def log_event():
    """
    Endpoint to manually log an event
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['user_id', 'event_type', 'event_description']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Log the event
        result = AuditLogger.log_event(
            user_id=data['user_id'],
            event_type=data['event_type'],
            event_description=data['event_description'],
            additional_metadata=data.get('additional_metadata')
        )
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit/trail', methods=['GET'])
def get_audit_trail():
    """
    Retrieve audit trail for a user
    """
    try:
        user_id = request.args.get('user_id')
        days = int(request.args.get('days', 30))
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        result = AuditLogger.get_user_audit_trail(user_id, days)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit/suspicious', methods=['GET'])
def analyze_suspicious_activities():
    """
    Analyze suspicious activities
    """
    try:
        user_id = request.args.get('user_id')
        
        result = AuditLogger.analyze_suspicious_activities(user_id)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5004)
