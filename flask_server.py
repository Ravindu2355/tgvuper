from flask import Flask, request, jsonify
from task_manager import add_task_to_list
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)
CORS(app)
@app.route('/')
def f_home():
    return 'hellow RVX task dl bot',200

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    url = data.get('url')
    chat_id = data.get('chat_id')
    thumbnail_url = data.get('thumbnail_url', None)
    
    if url and chat_id:
        add_task_to_list(url, chat_id, thumbnail_url)
        return jsonify({"status": "success", "message": f"Task added for URL: {url}"}), 200
    else:
        return jsonify({"status": "error", "message": "Missing url or chat_id"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
