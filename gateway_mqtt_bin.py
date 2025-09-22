import json
import paho.mqtt.client as mqtt
import os

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
FIRMWARE_TOPIC = "lightchain/devices/firmware"

# Dictionary: device_id -> {"chunks": {}, "total": N}
devices = {}

def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected to MQTT broker with code {rc}")
    client.subscribe(FIRMWARE_TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    device_id = data["device_id"]
    index = data["index"]
    total = data["total"]
    hex_data = data["data"]

    # Initialize device entry if first time
    if device_id not in devices:
        devices[device_id] = {"chunks": {}, "total": total}
        print(f"📡 Receiving firmware from {device_id}, expecting {total} chunks")

    devices[device_id]["chunks"][index] = bytes.fromhex(hex_data)

    print(f"📥 {device_id} -> chunk {index+1}/{total}")

    # Check if all chunks are received
    if len(devices[device_id]["chunks"]) == total:
        filename = f"{device_id}_firmware.bin"
        with open(filename, "wb") as f:
            for i in range(total):
                f.write(devices[device_id]["chunks"][i])
        print(f"🎉 Firmware reassembly complete for {device_id}: saved as {filename}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
