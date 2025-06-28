from flask_sqlalchemy import SQLAlchemy
from database.database import db

class PDFDocument(db.Model):
    __tablename__ = 'pdf_documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    mimetype = db.Column(db.String(100), nullable=False)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, filename, data, mimetype, coach_id):
        self.filename = filename
        self.data = data
        self.mimetype = mimetype
        self.coach_id = coach_id
        