# gateway.py
from flask import Flask, request, jsonify
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from blockchain import Blockchain

app = Flask(__name__)
bc = Blockchain()

# Load public key from file
with open("esp32_pub.pem", "r") as f:
    pub_key = ECC.import_key(f.read())

@app.route("/join", methods=["POST"])
def join():
    data = request.get_json()
    message = data["device_id"] + data["firmware_hash"]
    sig = bytes.fromhex(data["signature"])
    
    h = SHA256.new(message.encode())
    verifier = DSS.new(pub_key, 'fips-186-3')
    
    try:
        verifier.verify(h, sig)
        bc.create_block(bc.chain[-1]["hash"], data)
        return jsonify({"status": "verified", "block_index": len(bc.chain)})
    except:
        return jsonify({"status": "verification_failed"}), 403

app.run(host="0.0.0.0", port=5000)
