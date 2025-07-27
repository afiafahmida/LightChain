import hashlib
import json
from time import time

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
            'hash': ''
        }
        block['hash'] = self.hash(block)
        self.chain.append(block)
        return block

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

