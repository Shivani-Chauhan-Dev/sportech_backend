from dotenv import load_dotenv
import os
from flask import Flask, jsonify, request
from together import Together
from . import bp

load_dotenv()
# Load API key from environment variable
print("TOGETHER_API_KEY:", os.getenv("TOGETHER_API_KEY"))
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=TOGETHER_API_KEY)

def generate_response(user_input):
    """Generates a response using LLaMA API from Together.AI"""
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        return response.choices[0].message.content  # Extract AI response
    except Exception as e:
        return f"Error: {str(e)}"

@bp.route('/api/chat', methods=['POST'])
def chat():
    """Chatbot API endpoint"""
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    response = generate_response(user_input)
    return jsonify({"response": response})
