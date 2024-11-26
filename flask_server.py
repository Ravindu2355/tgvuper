from flask import Flask, request, jsonify
from task_manager import add_task_to_list, task_list
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

@app.route('/')
def f_home():
    return 'hellow RVX task dl bot',200

@app.route('/tasks')
def f_home():
    return f"Currently {len(task_list)} tasks running!..",200


@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    url = data.get('url')
    chat_id = data.get('chat_id')
    thumbnail_url = data.get('thumbnail_url', None)
    type = data.get('type',None)
    
    if url and chat_id:
        #await add_task_to_list(url, chat_id, thumbnail_url=thumbnail_url, type=type)
        task = {"url": url, "chat_id": chat_id, "thumbnail_url": thumbnail_url, "type": type}
        task_list.append(task)
        return jsonify({"status": "success", "message": f"Task added for URL: {url}"}), 200
    else:
        return jsonify({"status": "error", "message": "Missing url or chat_id"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
