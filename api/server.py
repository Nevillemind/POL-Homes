from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json, os, time
from datetime import date

STATIC = os.path.join(os.path.dirname(__file__), '..', 'resident-app')
app = Flask(__name__, static_folder=STATIC, static_url_path='')
CORS(app)
DATA = os.path.join(os.path.dirname(__file__), 'data.json')

def load():
    if not os.path.exists(DATA): return {}
    with open(DATA) as f: return json.load(f)

def save(d):
    with open(DATA, 'w') as f: json.dump(d, f, indent=2, default=str)

@app.route('/')
def index():
    return send_from_directory(STATIC, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    if path.startswith('api/'):
        return jsonify({"error": "not found"}), 404
    file_path = os.path.join(STATIC, path)
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        return send_from_directory(STATIC, path)
    return send_from_directory(STATIC, 'index.html')

@app.route('/api/status')
def status():
    return jsonify({"ok": True, "time": time.time()})

@app.route('/api/announcements')
def announcements():
    db = load()
    return jsonify(db.get('announcements', []))

@app.route('/api/checkin', methods=['POST'])
def checkin():
    db = load()
    entry = {
        'date': str(date.today()),
        'mood': request.json.get('mood',''),
        'notes': request.json.get('notes',''),
        'time': time.strftime('%H:%M')
    }
    db.setdefault('checkins', []).append(entry)
    save(db)
    return jsonify({"ok": True, "entry": entry})

@app.route('/api/meetings', methods=['POST'])
def log_meeting():
    db = load()
    entry = {
        'date': str(date.today()),
        'type': request.json.get('type',''),
        'location': request.json.get('location',''),
        'notes': request.json.get('notes',''),
        'time': time.strftime('%H:%M')
    }
    db.setdefault('meetings', []).append(entry)
    save(db)
    return jsonify({"ok": True, "entry": entry})

@app.route('/api/maintenance', methods=['POST'])
def maintenance():
    db = load()
    entry = {
        'date': str(date.today()),
        'type': request.json.get('type',''),
        'description': request.json.get('description',''),
        'urgency': request.json.get('urgency',''),
        'time': time.strftime('%H:%M')
    }
    db.setdefault('maintenance', []).append(entry)
    save(db)
    return jsonify({"ok": True, "entry": entry})

@app.route('/api/chores', methods=['GET'])
def get_chores():
    db = load()
    return jsonify(db.get('chores', []))

@app.route('/api/chores/<int:chore_id>/toggle', methods=['POST'])
def toggle_chore(chore_id):
    db = load()
    chores = db.get('chores', [])
    for c in chores:
        if c.get('id') == chore_id:
            c['done'] = not c.get('done', False)
            break
    save(db)
    return jsonify({"ok": True, "chores": chores})

@app.route('/api/resident', methods=['GET'])
def resident():
    db = load()
    return jsonify(db.get('resident', {}))

@app.route('/api/today')
def today():
    db = load()
    checkins = db.get('checkins', [])
    meetings = db.get('meetings', [])
    chores = db.get('chores', [])
    today_str = str(date.today())
    return jsonify({
        'checked_in': any(c.get('date') == today_str for c in checkins),
        'meeting_logged': any(m.get('date') == today_str for m in meetings),
        'chores_done': sum(1 for c in chores if c.get('done')),
        'chores_total': len(chores)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8901, debug=False)
