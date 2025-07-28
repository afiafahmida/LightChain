
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
    device_id = data.get("device_id")
    firmware_hash = data.get("firmware_hash")

    if not device_id or not firmware_hash:
        return jsonify({"error": "Missing required fields"}), 400

    # Check if device is already in the chain
    for block in bc.chain:
        block_data = block.get("data")
        if isinstance(block_data, dict) and block_data.get("device_id") == device_id:
            # If firmware hash matches
            if block_data.get("firmware_hash") == firmware_hash:
                return jsonify({
                    "status": block_data.get("status", "pending"),
                    "message": "Device already registered",
                    "block_index": block["index"]
                })

    # Device not found — create new pending block
    data["status"] = "pending"
    new_block = bc.create_block(bc.chain[-1]["hash"], data)

    return jsonify({
        "status": "registered (pending)",
        "block_index": new_block["index"],
        "message": "New device registered"
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
