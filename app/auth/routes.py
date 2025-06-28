from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
# from model.wallet import Wallet 
from database.database import db
from model.user import User
from . import bp
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from itsdangerous import URLSafeTimedSerializer
import datetime
# from model.review import Review
from datetime import datetime, timedelta
import random
import datetime
from dotenv import load_dotenv
import os
from functools import wraps


secret_key = os.getenv("SECRET_KEYS", 'default-secret-key')

app = Flask(__name__)
app.config['secret_key'] = secret_key
serializer = URLSafeTimedSerializer(app.config['secret_key'])

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        # print(auth_header)
        if auth_header:
            try:
                token = auth_header.split()[1]
            except IndexError:
                return jsonify({'error': 'Token format is invalid'}), 400
        else:
            return jsonify({'error':'Token is missing'}), 403

        try:
            jwt.decode(token, app.config['secret_key'], algorithms="HS256")
        except Exception as error:
           return jsonify({'error': 'token is invalid/expired'})
        return f(*args, **kwargs)

    return decorated

@bp.route("/logging", methods=["POST"])
def user_login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password are required"}), 400

    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Invalid email or password"}), 401
    if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return jsonify({"message": "Invalid email or password"}), 401
    token = jwt.encode({'user': user.email,'id': user.id,"role": user.role,'exp': datetime.datetime.utcnow(
                ) + datetime.timedelta(seconds=3600)}, app.config['secret_key'])
    # return jsonify(token)

    return jsonify({
        "message": "Login successful",
        "token": token,
        # "user": user.to_dict()  
    }), 200


@bp.route("/me", methods=["GET"],endpoint="get_profile")
@token_required
def get_current_user():
    auth_header = request.headers.get('Authorization')
    payload = auth_header.split(" ")[1]
    token = jwt.decode(payload, secret_key, algorithms=['HS256'])
    user_id = token["id"]
    user = User.query.get(user_id)
   
    if not user:
            return jsonify({"message": "User not found"}), 404

    return jsonify({
            "user": user.to_dict()
        }), 200


@bp.route("/reset_password", methods=["POST"], endpoint="reset_password")
def reset_password():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Request body is missing"}), 400

    email = data.get("email")
    new_password = data.get("password")

    if not email or not new_password:
        return jsonify({"message": "Email and new password is required"}), 400

    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user.password = hashed_password
    user.updated_at = str(datetime.datetime.now())

    try:
        db.session.commit()
        return jsonify({"message": "Password reset successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to reset password: {str(e)}"}), 500

