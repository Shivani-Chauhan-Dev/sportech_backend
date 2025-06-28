from flask import request, jsonify
from datetime import datetime
from model.chat import Chat
from model.user import User
from database.database import db
from . import bp  
from app.auth.routes import token_required,secret_key
import jwt


@bp.route('/chat', methods=['POST'])
@token_required
def create_chat():
    try:
        data = request.json
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        message = data.get('message')

        if not sender_id or not receiver_id or not message:
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        # Check if sender and receiver exist
        sender = User.query.get(sender_id)
        receiver = User.query.get(receiver_id)

        if not sender or not receiver:
            return jsonify({"success": False, "message": "Sender or Receiver not found"}), 404

        new_chat = Chat(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message
        )

        db.session.add(new_chat)
        db.session.commit()

        return jsonify(success=True, chat=new_chat.to_dict()), 201

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


# Get all chats where a user is either sender or receiver (user_id can be coach or athlete)
@bp.route('/chats/user/<int:user_id>', methods=['GET'],endpoint="getallchat")
@token_required
def get_user_chats(user_id):
    try:
        chats = Chat.query.filter(
            (Chat.sender_id == user_id) | (Chat.receiver_id == user_id)
        ).order_by(Chat.timestamp.asc()).all()

        return jsonify(success=True, chats=[chat.to_dict() for chat in chats]), 200

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


# Get all chats between two specific users (like chat history between athlete and coach)
@bp.route('/chat/history', methods=['GET'],endpoint="getchat")
@token_required
def chat_history():
    user1_id = request.args.get('user1_id')
    user2_id = request.args.get('user2_id')

    if not user1_id or not user2_id:
        return jsonify({"error": "Missing user1_id or user2_id"}), 400

    chats = Chat.query.filter(
        ((Chat.sender_id == user1_id) & (Chat.receiver_id == user2_id)) |
        ((Chat.sender_id == user2_id) & (Chat.receiver_id == user1_id))
    ).order_by(Chat.timestamp.asc()).all()

    return jsonify(success=True, chats=[chat.to_dict() for chat in chats]), 200


# Get chat by chat_id
@bp.route('/chat/<int:chat_id>', methods=['GET'],endpoint="get_chat_by_id")
@token_required
def get_chat_by_id(chat_id):
    try:
        chat = Chat.query.get(chat_id)
        if not chat:
            return jsonify(success=False, message="Chat not found"), 404
        return jsonify(success=True, chat=chat.to_dict()), 200
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


# Delete chat by chat_id
@bp.route('/chat/<int:chat_id>', methods=['DELETE'],endpoint="delete_chat")
@token_required
def delete_chat_by_id(chat_id):
    try:
        chat = Chat.query.get(chat_id)
        if not chat:
            return jsonify(success=False, message="Chat not found"), 404
        db.session.delete(chat)
        db.session.commit()
        return jsonify(success=True, message="Chat deleted successfully"), 200
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


# Get chat partner list for a user (like chat list)
@bp.route('/chat_list/<int:user_id>', methods=['GET'],endpoint="chat_list")
@token_required
def chat_list(user_id):
    try:
        # Get distinct users this user has chatted with (either sent or received)
        sent_partners = db.session.query(Chat.receiver_id).filter(Chat.sender_id == user_id)
        received_partners = db.session.query(Chat.sender_id).filter(Chat.receiver_id == user_id)

        partner_ids = {pid for (pid,) in sent_partners.union(received_partners).all()}

        users = User.query.filter(User.id.in_(partner_ids)).all()

        return jsonify(success=True, users=[{
            "id": u.id,
            "name": u.name,
            "role": u.role,
            "email": u.email
        } for u in users]), 200

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
