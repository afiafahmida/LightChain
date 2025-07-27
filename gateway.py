from flask import Flask, request, jsonify
from blockchain import Blockchain
from time import time
import hashlib

app = Flask(__name__)
bc = Blockchain()

@app.route("/dashboard")
def dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route("/join", methods=["POST"])
def join():
    data = request.get_json()

    if "device_id" not in data or "firmware_hash" not in data:
        return jsonify({"error": "Missing device_id or firmware_hash"}), 400

    message = data["device_id"] + data["firmware_hash"]
    print(f"📥 Received from device: {data['device_id']}")

    # Optional: generate server-side hash
    signature = hashlib.sha256(message.encode()).hexdigest()

    block = bc.create_block(prev_hash=bc.chain[-1]['hash'], data={
        "device_id": data["device_id"],
        "firmware_hash": data["firmware_hash"],
        "server_signature": signature
    })

    return jsonify({
        "status": "registered",
        "block_index": block["index"],
        "server_signature": signature
    })

@app.route("/chain", methods=["GET"])
def chain():
    return jsonify({
        "length": len(bc.chain),
        "chain": bc.chain
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
