# Library imports
import json
import functools

# Custom libraries and classes
from blocks.block import Block
from transactions.transaction import Transaction
from utils.hash_util import hash_block, hash_string_256
from utils.verification import Verification

MINING_REWARD = 10

class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 100, 0)
        # Initialising our empty blockchain
        self.chain = [genesis_block]
        # Unhandled (pending) transactions
        self.open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    def save_data(self):
        try:
            with open("blockchain.txt", mode="w") as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.chain]]
                f.write(json.dumps(saveable_chain))
                f.write("\n")
                saveable_txs = [tx.__dict__ for tx in self.open_transactions]
                f.write(json.dumps(saveable_txs))

        except IOError:
            print('Saving failed')

    def load_data(self):
        try:
            with open("blockchain.txt", mode="r") as f:
                file_content = f.readlines()
                
                blockchain = json.loads(file_content[0][:-1])
                # We need to convert  the loaded data because Transactions should use OrderedDict
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                
                self.chain = updated_blockchain

                open_transactions = json.loads(file_content[1])
                # We need to convert  the loaded data because Transactions should use OrderedDict
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                open_transactions = updated_transactions

        except (IOError, IndexError):
            print('Handled exception...')
        finally:
            print('Cleanup!')
        
    def proof_of_work(self):
        """ Increment nonce until hash meets proof of work criteria  """

        last_block = self.chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        
        verifier = Verification()
        while not verifier.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        """Calculate and return the balance for a participant.

        Arguments:
            :participant: The person for whom to calculate the balance.
        """
        participant = self.hosting_node

        tx_sender = [[tx.amount for tx in block.transactions
                    if tx.sender == participant] for block in self.chain]

        open_tx_sender = [tx.amount
                        for tx in self.open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

        tx_recipient = [[tx.amount for tx in block.transactions
                        if tx.recipient == participant] for block in self.chain]

        amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(
            tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Returns last string of blockchain array """

        return self.chain[-1]

    def add_transaction(self, sender, recipient, amount=1.0):
        """ Append next transaction to blockchain as well as last transaction """

        transaction = Transaction(sender, recipient, amount)

        verifier = Verification()
        if verifier.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            self.save_data()
            return True

        return False


    def mine_block(self):
        """ Wrap open transactions into a block and append to blockchain """

        last_block = self.get_last_blockchain_value()
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()

        reward_transaction = Transaction('MINING', self.hosting_node, MINING_REWARD)

        copied_transactions = self.open_transactions[:]
        copied_transactions.append(reward_transaction)

        block = Block(
            len(self.chain),
            hashed_block,
            copied_transactions,
            proof
        ) 

        self.chain.append(block)
        self.open_transactions = []
        self.save_data()
        return True



