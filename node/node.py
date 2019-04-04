import json

from flask import Flask
from flask_cors import CORS

from wallet.wallet import Wallet
from blockchain.blockchain import Blockchain

app = Flask(__name__)
CORS(app)

class Node:
    def __init__(self):
        self.app = app
        self.wallet = Wallet()         
        self.blockchain = Blockchain(self.wallet.public_key)

    def start(self):
        self.app.run(host='0.0.0.0', port=5000)

    @app.route('/', methods=['GET'])
    def get_ui(self):
        return 'This works'

    @app.route('/chain', methods=['GET'])
    def get_chain(self):
        chain_snapshot = self.blockchain.chain
        return json.dumps(chain_snapshot)