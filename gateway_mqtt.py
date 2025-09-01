import json
import hashlib
import time
import paho.mqtt.client as mqtt
from blockchain import Blockchain

# MQTT broker configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
JOIN_TOPIC = "lightchain/devices/join"
APPROVE_TOPIC = "lightchain/devices/approve"
CHAIN_TOPIC = "lightchain/chain/response"
CHAIN_REQ_TOPIC = "lightchain/chain/request"

bc = Blockchain()
pending_approvals = {}  # device_id: block_index

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe([(JOIN_TOPIC, 0), (APPROVE_TOPIC, 0), (CHAIN_REQ_TOPIC, 0)])

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    if topic == JOIN_TOPIC:
        data = json.loads(payload)
        device_id = data.get("device_id")
        firmware_hash = data.get("firmware_hash")
        if not device_id or not firmware_hash:
            return
        # Check if device already exists
        for block in bc.chain:
            block_data = block.get("data")
            if isinstance(block_data, dict) and block_data.get("device_id") == device_id:
                if block_data.get("firmware_hash") == firmware_hash:
                    response = {
                        "status": block_data.get("status", "pending"),
                        "message": "Device already registered",
                        "block_index": block["index"]
                    }
                    client.publish(JOIN_TOPIC + f"/response/{device_id}", json.dumps(response))
                    return
        # Register new device
        data["status"] = "pending"
        new_block = bc.create_block(bc.chain[-1]["hash"], data)
        pending_approvals[device_id] = new_block["index"]
        response = {
            "status": "registered (pending)",
            "block_index": new_block["index"],
            "message": "New device registered"
        }
        client.publish(JOIN_TOPIC + f"/response/{device_id}", json.dumps(response))
    elif topic == APPROVE_TOPIC:
        data = json.loads(payload)
        index = data.get("block_index")
        if index is None or index < 1 or index >= len(bc.chain):
            return
        block = bc.chain[index]
        if isinstance(block['data'], dict):
            block['data']['status'] = "approved"
            response = {"status": "approved", "block": block}
            device_id = block['data']['device_id']
            client.publish(APPROVE_TOPIC + f"/response/{device_id}", json.dumps(response))
    elif topic == CHAIN_REQ_TOPIC:
        # Send whole chain
        response = {
            "length": len(bc.chain),
            "chain": bc.chain
        }
        client.publish(CHAIN_TOPIC, json.dumps(response))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()