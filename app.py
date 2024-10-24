from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from prompt import prompt

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/greet', methods=['POST'])
def greet():
    data = request.get_json()
    topic = data.get('topic')

    print(request)
    print(data)
    
    # Create a response message
    message = response(topic)
    response_message = {
        'message': message
    }
    
    return jsonify(response_message)


def response(topic):
    # Fetches API key from the .env file
    api_key = os.getenv("OPENAI_API_KEY")

    # Send an API call to OpenAI to generate a response
    client = OpenAI(api_key=api_key)

    # Awaits chatgpt for its response
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        # Testing messages
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Tell me everything you know about this topic: {topic}" }
    ]
    )
    
    # Returns the part of the dictionary that only contains the text
    print(response)
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(port=5000, debug=True) # Runs on port 5000 be default
