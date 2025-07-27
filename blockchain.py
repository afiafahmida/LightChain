import hashlib
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
        }
        block['hash'] = self.hash(block)
        self.chain.append(block)
        return block

    def hash(self, block):
        block_string = str(block['index']) + str(block['timestamp']) + str(block['data']) + block['prev_hash']
        return hashlib.sha256(block_string.encode()).hexdigest()
