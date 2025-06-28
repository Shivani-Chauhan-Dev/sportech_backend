from datetime import datetime
from database.database import db

class Chat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy=True))
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_messages', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message": self.message,
            "timestamp": self.timestamp,
            "sender_role": self.sender.role,
            "receiver_role": self.receiver.role
        }

    def __repr__(self):
        return f"<Chat from User {self.sender_id} to User {self.receiver_id}>"

class ChatHistory(db.Model):
    __tablename__ = 'chat_histories'

    id = db.Column(db.Integer, primary_key=True)  
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False) 
    chats = db.relationship('Chat', backref='history', lazy=True)

    def __repr__(self):
        return f"<ChatHistory {self.id}>"