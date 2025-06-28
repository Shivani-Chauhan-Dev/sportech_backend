from flask import Flask
from flask import Blueprint
from database.database import db
from flask_cors import CORS
from app.user import bp as user_bp
from app.sport import bp as services_bp
from app.review import bp as review_bp
# from app.survey import bp as survey_bp
# from app.wallet import bp as wallet_bp
from app.chat import bp as chat_bp
from app.auth import bp as auth_bp
from app.verify_otp import bp as verify_otp_bp
from app.image import bp as image_bp
from app.aichat import bp as ai_chat
from app.meetings import bp as meeting
from app.pdf import bp as pdf
from dotenv import load_dotenv
import os
import logging

load_dotenv()
# Function to create the Flask app
def create_app():
    app = Flask(__name__)
    # app.secret_key = "your_secret_key"
    app.secret_key = os.getenv("SECRET_KEY")
    # app.config['SECRET_KEY'] = 'your_jwt_secret_key'
    app.config["SECRET_KEY"] = os.getenv("SECRETS_KEY")

    # CORS(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    # CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    # Configuring the database URI
    # app.config["SQLALCHEMY_DATABASE_URI"] =os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:shivanichauhan@localhost:5000/apps"
    # app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://sport_tech_dk1b_user:BNhGxhvPlrXHxrygf8CwEbvwIoxv5myg@dpg-d1b7fsodl3ps73ec9000-a.singapore-postgres.render.com:5432/sport_tech_dk1b"
    
    # Initialize the database with the app
    db.init_app(app)
    
    # Create tables (if they don't exist)
    with app.app_context():
        db.create_all()
    
    # Register blueprints

    app.register_blueprint(user_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(review_bp)
    # app.register_blueprint(survey_bp)
    # app.register_blueprint(wallet_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(verify_otp_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(ai_chat)
    app.register_blueprint(meeting)
    app.register_blueprint(pdf)

    # if not os.path.exists('logs'):
    #     os.makedirs('logs')

    # logging.basicConfig(
    #     filename='logs/backend.log',
    #     level=logging.INFO,
    #     format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
    # )



    return app  # Ensure the app is returned so it can be run
app = create_app() 
# Main block to run the app
if __name__ == '__main__':
    # app = create_app()  # Create the app
    app.run(debug=True, port=5004)  # Run the app on port 5004
