from database.database import db
from sqlalchemy.exc import IntegrityError
import datetime

class OtpEmail(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    email_id = db.Column(db.String(100), nullable=False)
    
    otp_email = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)