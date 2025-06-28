from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from database.database import db


class Meeting(db.Model):
    __tablename__ = 'meetings'

    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    athlete_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # title = db.Column(db.String(120), nullable=False)
    # description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    # end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined

    coach = db.relationship('User', foreign_keys=[coach_id], backref='coach_meetings')
    athlete = db.relationship('User', foreign_keys=[athlete_id], backref='athlete_meetings')

    # coach = db.relationship('User',backref=db.backref('meetings', lazy=True) )
    # athlete = db.relationship('User',backref=db.backref('meetings', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            # "title": self.title,
            # "description": self.description,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M"),
            # "start_time": self.start_time.isoformat(),
            # "end_time": self.end_time.isoformat(),
            "status": self.status,
            "coach": {
                "id": self.coach.id,
                "name": self.coach.name,
                "role": self.coach.role
            },
            "athlete": {
                "id": self.athlete.id,
                "name": self.athlete.name,
                "role": self.athlete.role
            }
        }
    