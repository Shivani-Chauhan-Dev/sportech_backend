from database.database import db
from model.otp_email import OtpEmail
from flask import Flask, request, jsonify
from . import bp
import random
import datetime 
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def send_otp_email(email):
    otp = random.randint(100000,999999)
    new_otp = OtpEmail(email_id=email,otp_email=otp)
    db.session.add(new_otp)
    db.session.commit()

    print(f"OTP for {email} is {otp}")
    sender_email_id = os.getenv("SENDER_ID")
    sender_password = os.getenv("SENDER_PASSWORD")  # Use an App Password if 2FA is enabled
    

    EMAIL_SUBJECT = "Your OTP for an Exciting Sports Journey Awaits!"

    # Email body
    body = f"""Dear Customer,

        Welcome to ATASports, your trusted partner in achieving excellence and thrilling sports experiences!
        To ensure your smooth and secure journey with us, we need to verify your identity.

        Your One-Time Password (OTP):
        [ {otp} ]

        This OTP is valid for the next 5 minutes, so let's get you back to chasing your sports dreams!

        For your security, please do not share this OTP with anyone. ATASports is committed to safeguarding your privacy and data security, ensuring your sports journey is as secure as it is exciting.

        If you didn't request this OTP, kindly reach out to us at support@atasports.com or contact our customer care at +919411636065.

        We look forward to supporting you in achieving your goals and creating unforgettable sports moments!

        Best Regards,  
        Team ATASports  
        Your Companion in Every Sporting Victory  
        www.atasports.com"""

    
    msg = f"Subject: {EMAIL_SUBJECT}\n\n{body}"

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.set_debuglevel(1)
    s.starttls()
    s.login(sender_email_id, sender_password)
    s.sendmail(sender_email_id, email, msg)
    s.quit()

    return otp



@bp.route("/send_otp_email",methods=["POST"])
def send_otp():
    data = request.get_json()
    email_id = data.get("email_id")

    if email_id:
        send_otp_email(email_id)
        return jsonify({"message": "OTP sent successfully"}), 200
    else:
        return jsonify({"message": "email_id is required"}), 400
    

@bp.route("/verify_email", methods=["POST"], endpoint="verify_email")
def verify_otp():
    data = request.get_json()
    email_id = data.get("email_id")
    otp_email = data.get("otp_email")

    valid_otp = OtpEmail.query.filter_by(email_id=email_id, otp_email=otp_email).first()
    if valid_otp:
        valid_time = datetime.datetime.utcnow() - valid_otp.created_at
        if valid_time.total_seconds() <= 120:

            db.session.delete(valid_otp)
            db.session.commit()
            return jsonify({"message": "OTP verified successfully"}), 200
        else:
            return jsonify({"message": "OTP has expired"}), 400
    else:
        return jsonify({"message": "Invalid OTP"}), 400