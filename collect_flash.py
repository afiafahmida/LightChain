# save as collect_flash.py
import json, base64, binascii
from paho.mqtt.client import Client

BROKER="localhost"   # or your broker IP/host
DATA_TOPIC="esp/dump/data"
PROG_TOPIC="esp/dump/progress"
CMD_TOPIC ="esp/dump/start"

bin_path="esp8266_flash.bin"
fp=open(bin_path,"wb")  # we’ll random-access write via memory map alternative
fp.close()

# Keep a map of received chunks
received = {}
total=None
from_offset=0

def on_message(client, userdata, msg):
    global total, from_offset
    if msg.topic == DATA_TOPIC:
        m=json.loads(msg.payload.decode())
        offset=m["offset"]; l=m["len"]; b64=m["data"]; crc=m["crc32"]
        raw=base64.b64decode(b64)
        if len(raw)!=l:
            print("Length mismatch at",offset); return
        # verify CRC32
        calc=binascii.crc32(raw) & 0xffffffff
        if f"{calc:08X}"!=crc:
            print("CRC mismatch at",offset); return
        received[offset]=raw
        print(f"Chunk {offset}-{offset+l} OK, {len(received)} chunks")
    elif msg.topic == PROG_TOPIC:
        p=json.loads(msg.payload.decode())
        if "total" in p: total=p["total"]; from_offset=p.get("from",0)
        if p.get("done"):
            # stitch in order
            with open(bin_path,"r+b") as f:
                cur=from_offset
                while cur < from_offset+total:
                    chunk=received.get(cur)
                    if chunk is None:
                        print("Missing chunk at",cur); return
                    f.seek(cur); f.write(chunk)
                    cur+=len(chunk)
            print("Done. Flash saved to",bin_path)

cli=Client()
cli.on_message=on_message
cli.connect(BROKER,1883,60)
cli.subscribe([(DATA_TOPIC,1),(PROG_TOPIC,1)])
cli.loop_start()

# Trigger a full dump
cmd = json.dumps({"from":0,"size":0})  # size=0 => device chooses full flash
cli.publish(CMD_TOPIC, cmd, qos=1)
input("Dumping... press Enter to quit\n")
