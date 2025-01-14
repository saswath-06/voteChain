import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from datetime import datetime
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')

mongo = PyMongo(app)

class NotificationManager:
    @classmethod
    def create_notification(cls, user_id: str, notification_type: str, message: str, related_id: str = None) -> dict:
        """
        Create a new notification for a user
        """
        try:
            notification = {
                '_id': str(uuid.uuid4()),
                'user_id': user_id,
                'type': notification_type,
                'message': message,
                'related_id': related_id,
                'is_read': False,
                'created_at': datetime.utcnow()
            }
            
            # Insert notification into database
            result = mongo.db.notifications.insert_one(notification)
            
            return {
                'notification_id': str(result.inserted_id),
                'success': result.acknowledged
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    @classmethod
    def send_email_notification(cls, recipient_email: str, subject: str, body: str) -> dict:
        """
        Send email notification using SMTP
        """
        try:
            # Email configuration
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            sender_email = os.getenv('SENDER_EMAIL')
            sender_password = os.getenv('SENDER_PASSWORD')

            # Create message
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = recipient_email
            message['Subject'] = subject
            
            # Add body to email
            message.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            return {
                'success': True,
                'message': 'Email sent successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def get_user_notifications(cls, user_id: str, mark_as_read: bool = False) -> dict:
        """
        Retrieve notifications for a specific user
        """
        try:
            # Find notifications for the user
            notifications = list(mongo.db.notifications.find({'user_id': user_id}).sort('created_at', -1))
            
            # Optionally mark notifications as read
            if mark_as_read:
                mongo.db.notifications.update_many(
                    {'user_id': user_id, 'is_read': False},
                    {'$set': {'is_read': True}}
                )
            
            return {
                'notifications': notifications,
                'unread_count': mongo.db.notifications.count_documents({'user_id': user_id, 'is_read': False}),
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    @classmethod
    def notify_proposal_events(cls, proposal_id: str, event_type: str):
        """
        Generate notifications for proposal-related events
        """
        try:
            # Retrieve proposal details
            proposal = mongo.db.proposals.find_one({'_id': proposal_id})
            if not proposal:
                return {'error': 'Proposal not found', 'success': False}
            
            # Determine notification message based on event type
            notification_types = {
                'created': f"New proposal '{proposal['title']}' has been submitted",
                'voting_started': f"Voting has started for proposal '{proposal['title']}'",
                'voting_ended': f"Voting has ended for proposal '{proposal['title']}'",
                'approved': f"Proposal '{proposal['title']}' has been approved",
                'rejected': f"Proposal '{proposal['title']}' has been rejected"
            }
            
            message = notification_types.get(event_type, "Proposal update")
            
            # Find users interested in this proposal or all governance updates
            interested_users = mongo.db.users.find({
                '$or': [
                    {'interested_proposals': proposal_id},
                    {'governance_notifications': True}
                ]
            })
            
            # Create notifications for each interested user
            notifications = []
            for user in interested_users:
                notification = cls.create_notification(
                    user_id=str(user['_id']),
                    notification_type=f'proposal_{event_type}',
                    message=message,
                    related_id=proposal_id
                )
                notifications.append(notification)
                
                # Optionally send email
                if user.get('email_notifications', False):
                    cls.send_email_notification(
                        recipient_email=user['email'],
                        subject=f"Proposal Update: {proposal['title']}",
                        body=message
                    )
            
            return {
                'notifications_created': len(notifications),
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """
    Retrieve user notifications
    """
    try:
        user_id = request.args.get('user_id')
        mark_as_read = request.args.get('mark_as_read', 'false').lower() == 'true'
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        result = NotificationManager.get_user_notifications(user_id, mark_as_read)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/proposal', methods=['POST'])
def notify_proposal_event():
    """
    Generate notifications for proposal events
    """
    try:
        data = request.json
        proposal_id = data.get('proposal_id')
        event_type = data.get('event_type')
        
        if not all([proposal_id, event_type]):
            return jsonify({'error': 'Proposal ID and event type are required'}), 400
        
        result = NotificationManager.notify_proposal_events(proposal_id, event_type)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)
