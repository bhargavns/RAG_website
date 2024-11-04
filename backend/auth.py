from flask import Blueprint, request, jsonify, session
from models import User, db, BlacklistedToken
from functools import wraps
import datetime
import jwt
import os
import logging

auth = Blueprint('auth', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@auth.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    result = jsonify(
        {
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "created_at": new_user.created_at
            }
        })

    return result, 201

@auth.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    logger.info(f"Login attempted with {username}")
    if user and user.check_password(password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, os.environ.get('SECRET_KEY'))
        logger.info("Authorized")
        return jsonify({"token": token}), 200
    else:
        logger.info("Failed to match username and password")
        return jsonify({"message": "Invalid username or password"}), 401

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # Check if the token is blacklisted
            if BlacklistedToken.query.filter_by(token=token).first():
                return jsonify({'message': 'Token has been blacklisted'}), 401
            data = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth.route("/protected")
@token_required
def protected(current_user):
    return jsonify({"message": f"This is a protected route, {current_user.username}"})

@auth.route("/logout")
@token_required
def logout(current_user):
    token = request.headers.get('Authorization')
    
    # Add the token to a blacklist
    blacklisted_token = BlacklistedToken(token=token)
    db.session.add(blacklisted_token)
    db.session.commit()

    return jsonify({"message": "Logged out successfully"}), 200
    

