from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import datetime
from model.user import User
from database.database import db
from model.services import Services
from app.auth.routes import token_required,secret_key
from . import bp
import bcrypt
import jwt



@bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    current_date = str(datetime.datetime.now())

    required_common_fields = ["role", "email", "password", "name", "dob", "address", "phone"]

    # Check required fields
    if not data or not all(data.get(field) for field in required_common_fields):
        return jsonify({"message": "Missing required fields"}), 400

    # Check role value
    if data["role"] not in ["coach", "athlete"]:
        return jsonify({"message": "Invalid role, must be 'coach' or 'athlete'"}), 400

    # Check if email already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "User with this email already exists"}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt(14)).decode("utf-8")

    # Prepare payload for model
    payload = {
        "role": data["role"],
        "email": data["email"],
        "password": hashed_password,
        "phone": data.get("phone"),
        "name": data.get("name"),
        "dob": data.get("dob"),
        "address": data.get("address"),
        "created_at": current_date,
        "updated_at": current_date,
        "detail_experience": data.get("detail_experience"),
        "languages": data.get("languages"),
        "age": data.get("age"),
        "gender": data.get("gender"),
        "detail_health": data.get("detail_health"),
        "domains": data.get("domains")  # For coach role
    }

    # Create user
    user = User.create_user(payload)

    if user:
        return jsonify({
            "message": f"{data['role'].capitalize()} registered successfully",
            "user": user.to_dict()
        }), 201
    else:
        return jsonify({"message": "Registration failed"}), 500
    

# @bp.route("/user/update-profile", methods=["PUT"])
# @token_required
# def update_user_profile():
#     auth_header = request.headers.get('Authorization')
#     token = auth_header.split()[1]
    
#     try:
#         decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
#         user_id = decoded_token.get("id")
#         role = decoded_token.get("role")
#     except jwt.ExpiredSignatureError:
#         return jsonify({"message": "Token has expired"}), 401
#     except jwt.InvalidTokenError:
#         return jsonify({"message": "Invalid token"}), 401

#     user = User.query.get(user_id)

#     if not user:
#         return jsonify({"message": "User not found"}), 404

#     data = request.get_json()

#     # Update common fields
#     user.email = data.get("email", user.email)
#     user.phone = data.get("phone", user.phone)
#     user.name = data.get("name", user.name)
#     user.dob = data.get("dob", user.dob)
#     user.address = data.get("address", user.address)

#     # Password Update (if provided)
#     if data.get("password"):
#         hashed_password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
#         user.password = hashed_password

#     # Role-specific updates
#     if role == "coach":
#         user.detail_experience = data.get("detail_experience", user.detail_experience)
#         user.coach_languages = data.get("coach_languages", user.coach_languages)
#         user.coach_age = data.get("coach_age", user.coach_age)
#         user.gender = data.get("gender", user.gender)

#         # Update domains (services)
#         if data.get("domains"):
#             user.services.clear()  # Remove old services
#             for domain_name in data["domains"]:
#                 cleaned_service = domain_name.strip().lower()
#                 service = Services.query.filter_by(services=cleaned_service).first()
#                 if not service:
#                     service = Services(services=cleaned_service)
#                     db.session.add(service)
#                     db.session.flush()
#                 user.services.append(service)

#     elif role == "athlete":
#         user.detail_health = data.get("detail_health", user.detail_health)

#     user.updated_at = datetime.utcnow()

#     try:
#         db.session.commit()
#         return jsonify({"message": "Profile updated successfully", "user": user.to_dict()}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"message": f"Failed to update profile: {str(e)}"}), 500


@bp.route("/user/update_profile", methods=["PUT"])
@token_required
def update_user_profile():
    auth_header = request.headers.get('Authorization')
    token = auth_header.split()[1]
    
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = decoded_token.get("id")
        role = decoded_token.get("role")
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()

    if data.get("email"):
        user.email = data["email"]
    if data.get("phone"):
        user.phone = data["phone"]
    if data.get("name"):
        user.name = data["name"]
    if data.get("dob"):
        user.dob = data["dob"]
    if data.get("address"):
        user.address = data["address"]

    if data.get("password"):
        hashed_password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.password = hashed_password

    #  Coach fields
    if role == "coach":
        if data.get("detail_experience"):
            user.detail_experience = data["detail_experience"]
        if data.get("languages"):
            user.languages = data["languages"]
        if data.get("age"):
            user.age = data["age"]
        if data.get("gender"):
            user.gender = data["gender"]

        if data.get("domains"):
            user.services.clear()  # Clear old services
            domain_list = [d.strip().lower() for d in data["domains"].split(",")]  # CSV string like "fitness,yoga"
            for domain_name in domain_list:
                service = Services.query.filter_by(services=domain_name).first()
                if not service:
                    service = Services(services=domain_name)
                    db.session.add(service)
                    db.session.flush()
                user.services.append(service)

    # Athlete fields
    elif role == "athlete":
        if data.get("detail_health"):
            user.detail_health = data["detail_health"]

    
    user.updated_at = str(datetime.datetime.now())

    try:
        db.session.commit()
        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to update profile: {str(e)}"}), 500

@bp.route("/profile", methods=["GET"])
@token_required
def get_user_profile():
    auth_header = request.headers.get('Authorization')
    token = auth_header.split()[1]
    
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = decoded_token.get("id")
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "message": "User profile fetched successfully",
        "user": user.to_dict()
    }), 200



@bp.route("/user/all", methods=["GET"])
@token_required
def get_all_users_by_role():
    role = request.args.get('role')

    if role not in ["coach", "athlete"]:
        return jsonify({"message": "Invalid role. Use 'coach' or 'athlete'."}), 400

    users = User.query.filter_by(role=role).all()

    if not users:
        return jsonify({"message": f"No {role}s found."}), 404

    users_data = [user.to_dict() for user in users]

    return jsonify({
        "message": f"List of all {role}s",
        "users": users_data
    }), 200

@bp.route('/get_coaches_by_service/<int:service_id>', methods=['GET'], endpoint='get_coaches_by_service')
@token_required
def get_coaches_by_service(service_id):
    try:
        service = Services.query.get(service_id)
        if not service:
            return jsonify({'success': False, 'message': 'Service not found'}), 404

        coaches = service.users
        coach_list = []
        for coach in coaches:
            coach_list.append({
                "id": coach.id,
                "name": coach.name,
                "phone": coach.phone,
                "dob": coach.dob,
                "address": coach.address,
                "email": coach.email,
                "detail_experience": coach.detail_experience
                
            })

        return jsonify({'success': True, 'coaches': coach_list}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500