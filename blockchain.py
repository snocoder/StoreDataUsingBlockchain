import datetime
import hashlib
import json
from flask import Flask, jsonify, request, render_template


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0', data={
            'Name': '',
            'Address': '',
            'Blood Group': '',
            'Contact Number': 0
        })

    def create_block(self, proof, previous_hash, data):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'data': data,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if(hash_operation[:4] == '0000'):
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            if(hash_operation[:4] != '0000'):
                return False
            previous_block = block
            block_index += 1
        return True


app = Flask(__name__)

blockchain = Blockchain()


@app.route('/', methods=["GET"])
def index():
    return render_template("index.html")


@app.route('/mine_block', methods=['GET', 'POST'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    username = request.args.get('name')
    address = request.args.get('address')
    bg = request.args.get('bg')
    no = request.args.get('no')
    data = {
        'Name': username,
        'Address': address,
        'Blood Group': bg,
        'Contact Number': no
    }
    block = blockchain.create_block(proof, previous_hash, data)
    return render_template("index.html")


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)
                }
    return (jsonify(response), 200)


@app.route('/is_valid', methods=['GET'])
def is_valid():
    valid = blockchain.is_chain_valid(blockchain.chain)
    if valid:
        response = {'message': 'Chain is valid.'}
    else:
        response = {'message': 'Chain is not valid.'}
    return jsonify(response), 200


app.run(port=5000)
