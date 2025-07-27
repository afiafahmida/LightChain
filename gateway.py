from flask import Flask, request, jsonify
from time import time
import hashlib

# Simple local blockchain-like structure
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(prev_hash='0', data='Genesis Block')

    def create_block(self, prev_hash, data):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'data': data,
            'prev_hash': prev_hash,
        }
        block['hash'] = self.hash(block)
        self.chain.append(block)
        return block

    def hash(self, block):
        block_string = str(block['index']) + str(block['timestamp']) + str(block['data']) + block['prev_hash']
        return hashlib.sha256(block_string.encode()).hexdigest()

# Init Flask and Blockchain
app = Flask(__name__)
bc = Blockchain()

@app.route("/join", methods=["POST"])
def join():
    data = request.get_json()

    if "device_id" not in data or "firmware_hash" not in data:
        return jsonify({"error": "Missing device_id or firmware_hash"}), 400

    message = data["device_id"] + data["firmware_hash"]
    print(f"📥 Received from device: {data['device_id']}")

    # Optional: Generate a server-side hash for traceability
    signature = hashlib.sha256(message.encode()).hexdigest()

    # Register device in blockchain
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
