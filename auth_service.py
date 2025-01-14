import os
import jwt
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
app.config['MONGO_URI'] = os.getenv('MONGODB_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

mongo = PyMongo(app)
bcrypt = Bcrypt(app)

class AuthService:
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Password validation:
        - At least 8 characters
        - Contains uppercase and lowercase letters
        - Contains at least one number
        - Contains at least one special character
        """
        return (
            len(password) >= 8 and
            re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'\d', password) and
            re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        )

    @classmethod
    def generate_token(cls, user_id: str) -> str:
        """
        Generate JWT token
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    @classmethod
    def verify_token(cls, token: str) -> dict:
        """
        Verify JWT token
        """
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    User registration endpoint
    """
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        wallet_address = data.get('wallet_address')

        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if not AuthService.validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not AuthService.validate_password(password):
            return jsonify({'error': 'Password does not meet requirements'}), 400

        # Check if user already exists
        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create user document
        user_doc = {
            'email': email,
            'password': hashed_password,
            'wallet_address': wallet_address,
            'created_at': datetime.utcnow(),
            'governance_tokens': 0,
            'role': 'member'
        }

        # Insert user
        result = mongo.db.users.insert_one(user_doc)

        # Generate token
        token = AuthService.generate_token(str(result.inserted_id))

        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user_id': str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    User login endpoint
    """
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Find user
        user = mongo.db.users.find_one({'email': email})
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        # Verify password
        if not bcrypt.check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Generate token
        token = AuthService.generate_token(str(user['_id']))

        return jsonify({
            'token': token,
            'user_id': str(user['_id']),
            'email': user['email'],
            'wallet_address': user.get('wallet_address')
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify-token', methods=['POST'])
def verify_token():
    """
    Token verification endpoint
    """
    try:
        token = request.json.get('token')
        if not token:
            return jsonify({'error': 'Token is required'}), 400

        payload = AuthService.verify_token(token)
        
        if 'error' in payload:
            return jsonify(payload), 401

        # Fetch user details
        user = mongo.db.users.find_one({'_id': payload['user_id']})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user_id': str(user['_id']),
            'email': user['email'],
            'wallet_address': user.get('wallet_address'),
            'governance_tokens': user.get('governance_tokens', 0)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/profile', methods=['GET'])
def get_user_profile():
    """
    Retrieve user profile
    """
    try:
        # Get token from Authorization header
        token = request.headers.get('Authorization', '').split(' ')[-1]
        
        # Verify token
        payload = AuthService.verify_token(token)
        if 'error' in payload:
            return jsonify(payload), 401

        # Fetch user details
        user = mongo.db.users.find_one({'_id': payload['user_id']})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Prepare user profile
        profile = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'wallet_address': user.get('wallet_address'),
            'governance_tokens': user.get('governance_tokens', 0),
            'role': user.get('role', 'member'),
            'created_at': user['created_at']
        }

        return jsonify(profile), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
