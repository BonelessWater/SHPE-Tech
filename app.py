from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/greet', methods=['POST'])
def greet():
    data = request.get_json()
    topic = data.get('topic')
    
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
        {"role": "system", "content": """Create engaging, easy-to-understand, and structured educational content that covers key topics in Data Structures and Algorithms. The goal is to break down complex concepts into bite-sized lessons, supported with clear visuals, code examples, and real-world applications. Follow these guidelines:

Scope of Topics:

Data Structures: Arrays, Linked Lists, Stacks, Queues, Hash Tables, Trees (BST, AVL, Heaps), Graphs.
Algorithms: Sorting (Merge Sort, Quick Sort, Bubble Sort), Searching (Binary Search), Recursion, Dynamic Programming, Divide and Conquer, Greedy Algorithms, Graph Algorithms (DFS, BFS, Dijkstra’s, A*), and Backtracking.
Include a Big-O complexity analysis for each algorithm and data structure.
Format:

Provide modular lessons, with topics segmented by difficulty: Beginner, Intermediate, and Advanced.
Code snippets should be available in multiple languages (e.g., Python, C++, Java).
Visualize data structures (e.g., animation of how a linked list is traversed or how merges work in Merge Sort).
Real-World Applications:

For each data structure and algorithm, explain where and how they are used in practical scenarios (e.g., Graphs in Google Maps, Hash Tables in Database Indexing, etc.).
Interactive Elements (Optional):

Include quizzes or coding challenges after each lesson to reinforce learning.
Provide step-by-step walkthroughs of problems on coding platforms like LeetCode, HackerRank, or Codeforces.
Support Diverse Learning Styles:

Include text explanations, flowcharts, and diagrams.
Optional video content: Script ideas for 3-5 minute videos explaining key concepts with visual aids.
Tone and Style:

The tone should be approachable and conversational. Avoid jargon-heavy explanations and make content beginner-friendly.
Focus on building intuitive understanding before diving deep into technical details.
Bonus Features:

Create cheat sheets summarizing key algorithms and data structures.
Provide project ideas where learners can apply what they’ve learned (e.g., Implementing a mini database using a B-Tree, Building a social network graph).
Generate a comprehensive content plan that spans 4-6 weeks of learning and gradually introduces more complex topics."""},
        {"role": "user", "content": f"Tell me everything you know about this topic: {topic}" }
    ]
    )
    
    # Returns the part of the dictionary that only contains the text
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(port=5000, debug=True) # Runs on port 5000 be default
