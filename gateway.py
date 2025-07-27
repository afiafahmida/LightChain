
from flask import Flask, request, jsonify, send_from_directory
from blockchain import Blockchain
from time import time
import hashlib
import os

app = Flask(__name__)
bc = Blockchain()

@app.route("/join", methods=["POST"])
def join():
    data = request.get_json()

    if "device_id" not in data or "firmware_hash" not in data:
        return jsonify({"error": "Missing device_id or firmware_hash"}), 400

    message = data["device_id"] + data["firmware_hash"]
    print(f"📥 Received from device: {data['device_id']}")

    signature = hashlib.sha256(message.encode()).hexdigest()

    block = bc.create_block(prev_hash=bc.chain[-1]['hash'], data={
        "device_id": data["device_id"],
        "firmware_hash": data["firmware_hash"],
        "server_signature": signature,
        "status": "pending"
    })

    return jsonify({
        "status": "registered (pending)",
        "block_index": block["index"],
        "server_signature": signature
    })

@app.route("/approve/<int:index>", methods=["POST"])
def approve(index):
    if index < 1 or index >= len(bc.chain):
        return jsonify({"error": "Invalid block index"}), 404

    block = bc.chain[index]
    if isinstance(block['data'], dict):
        block['data']['status'] = "approved"
        return jsonify({"status": "approved", "block": block})
    else:
        return jsonify({"error": "Block has no device data"}), 400

@app.route("/chain", methods=["GET"])
def chain():
    return jsonify({
        "length": len(bc.chain),
        "chain": bc.chain
    })

@app.route("/dashboard")
def dashboard():
    return send_from_directory('.', 'dashboard_pro.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
