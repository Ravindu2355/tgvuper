from flask import Flask, request, jsonify
from app.bot import add_task_to_list
from app.config import FLASK_HOST, FLASK_PORT

# Initialize the Flask application
app = Flask(__name__)

# Flask route to handle adding tasks via POST request
@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    url = data.get('url')
    chat_id = data.get('chat_id')
    thumbnail_url = data.get('thumbnail_url', None)
    
    if url and chat_id:
        # Add the task to the bot's task list
        add_task_to_list(url, chat_id, thumbnail_url)
        return jsonify({"status": "success", "message": f"Task added for URL: {url}"}), 200
    else:
        return jsonify({"status": "error", "message": "Missing url or chat_id"}), 400

# Run the Flask server
if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT)
