
from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

DB_FILE = 'db.json'

def read_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def write_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    phone = data.get('phone')
    db = read_db()
    user = db.get(phone)

    if user:
        return jsonify({"message": "Login successful", "balance": user["balance"]})
    else:
        db[phone] = {"balance": 0.0, "transactions": []}
        write_db(db)
        return jsonify({"message": "New user created", "balance": 0.0})

@app.route('/api/add_money', methods=['POST'])
def add_money():
    data = request.json
    phone = data.get('phone')
    amount = float(data.get('amount'))

    db = read_db()
    if phone in db:
        db[phone]["balance"] += amount
        db[phone]["transactions"].append({"type": "credit", "amount": amount})
        write_db(db)
        return jsonify({"message": "Money added", "balance": db[phone]["balance"]})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/send_money', methods=['POST'])
def send_money():
    data = request.json
    phone = data.get('phone')
    to = data.get('to')
    amount = float(data.get('amount'))

    db = read_db()
    if phone not in db or to not in db:
        return jsonify({"error": "User not found"}), 404

    if db[phone]["balance"] < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    db[phone]["balance"] -= amount
    db[to]["balance"] += amount

    db[phone]["transactions"].append({"type": "debit", "to": to, "amount": amount})
    db[to]["transactions"].append({"type": "credit", "from": phone, "amount": amount})

    write_db(db)
    return jsonify({"message": "Money sent", "balance": db[phone]["balance"]})

@app.route('/api/history', methods=['POST'])
def get_history():
    data = request.json
    phone = data.get('phone')
    db = read_db()
    if phone in db:
        return jsonify({"transactions": db[phone]["transactions"]})
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
