from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Replace 'mongodb://localhost:27017/' with your MongoDB connection string if different
client = MongoClient('mongodb://localhost:27017/')
db = client['github_events']

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == 'push':
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = datetime.utcnow()
        db.events.insert_one({
            'event': 'push',
            'author': author,
            'to_branch': to_branch,
            'timestamp': timestamp
        })

    elif event_type == 'pull_request':
        action = data['action']
        if action == 'opened' or action == 'closed':
            author = data['pull_request']['user']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            timestamp = datetime.utcnow()
            db.events.insert_one({
                'event': action,
                'author': author,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'timestamp': timestamp
            })

    return '', 200

@app.route('/events', methods=['GET'])
def get_events():
    events = list(db.events.find().sort('timestamp', -1))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify({'events': events})

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(port=5000)
