import hashlib
import json
from time import time
from flask import Flask
from uuid import uuid4

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.new_block(previous_hash="The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.", proof=100)

    def proof_of_work(self, last_proof):
        """
        This method is where you the consensus algorithm is implemented. 
        It takes two parameters including self and last_proof
        """
        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof +=1
        return proof

    def valid_proof(self, last_proof, proof):
        """This method validates the block"""

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == "0000"

    def new_block(self, proof, previous_hash=None):
        """
        Create a new block listing key/value pairs of block information in a JSON object.
        Reset the list of pending transactions & append the newest block to the chain.
        """
        block = {
            # Take the length of our blockchain and add 1 to it.
            'index': len(self.chain) + 1,
            # Stamp the block when it’s created
            'timestamp': time(),
            # Transactions that are sitting in the ‘pending’ list will be included in our new block
            'transactions': self.pending_transactions,
            # A proof is a random number which is very difficult to find unless you have dedicated high-performance machines running around-the-clock.
            'proof': proof,
            # A hashed version of most recent approved block
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.pending_transactions = []
        self.chain.append(block)
        return block

    @property
    def last_block(self):
        """
        Search the blockchain for the most recent block.
        """
        return self.chain[-1]

    def new_transaction(self, sender, recipient, amount):
        """
        Add a transaction with relevant info to the 'blockpool' - list of pending tx's.
        """
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.pending_transactions.append(transaction)
        # Return the index of the block to which our new transaction will be added.
        return self.last_block['index'] + 1

    def hash(self, block):
        """
        Receive one block.
        Turn it into a string, turn that into Unicode (for hashing).
        Hash with SHA256 encryption, then translate the Unicode into a hexidecimal string.
        """
        string_object = json.dumps(block, sort_keys=True)

        # Convert the string into bytes for the hash function.
        block_string = string_object.encode()
        raw_hash = hashlib.sha256(block_string)

        # Return the encoded data in hexadecimal format.
        hex_hash = raw_hash.hexdigest()

        return hex_hash


# Creating the app node
app = Flask(__name__)
node_identifier = str(uuid4()).replace('-','')

# Initializing blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])

def mine():
    """Here we make the proof of work algorithm work"""
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # rewarding the miner for his contribution. 0 specifies new coin has been mined
    blockchain.new_transaction(
        sender="0",
        recipient = node_identifier,
        amount = 1,
    )

    # now create the new block and add it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'The new block has been forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash' : block['previous_hash']
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])

def new_transaction():
    values = request.get_json()
    
    # Checking if the required data is there or not
    required = ['sender','recipient','amount']
    
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Creaing a new transaction 
    index = blockchain.new_transaction(values['sender'], values['recipient', values['amount']])
    response = {'message': f'Transaction is scheduled to be added to Block No. {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])

def full_chain():
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain)
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)


# blockchain = Blockchain()
t1 = blockchain.new_transaction("Satoshi", "Mike", '5 BTC')
t2 = blockchain.new_transaction("Mike", "Satoshi", '1 BTC')
t3 = blockchain.new_transaction("Satoshi", "Hal", '5 BTC')
blockchain.new_block(12345)

t4 = blockchain.new_transaction("Mike", "Alice", '1 BTC')
t5 = blockchain.new_transaction("Alice", "Bob", '0.5 BTC')
t6 = blockchain.new_transaction("Bob", "Mike", '0.5 BTC')
blockchain.new_block(6789)

print("Genesis block: ", blockchain.chain)
