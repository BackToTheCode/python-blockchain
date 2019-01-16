# Library imports
import functools
import datetime
from collections import OrderedDict
import json
import pickle

# Custom libraries and classes
from utils.hash_util import hash_block, hash_string_256
from utils.formatting_util import print_spacer
from classes.block import Block


MINING_REWARD = 10
blockchain = []
open_transactions = []
owner = 'James'
participants = { 'Max', 'Anna' }

def save_data():
    try:
        with open("blockchain.txt", mode="w") as f:
            f.write(json.dumps(blockchain))
            f.write("\n")
            f.write(json.dumps(open_transactions))
    except IOError:
        print('Saving failed')
    # with open("blockchain.b", mode="wb") as f:
    #     save_data = {
    #         'chain': blockchain,
    #         'ot': open_transactions
    #     }
    #     f.write(pickle.dumps(save_data))


def load_data():
    
    # with open("blockchain.b", mode='rb') as f:
        # file_content = pickle.loads(f.read())
        # global blockchain
        # global open_transactions
        # blockchain = file_content['chain']
        # open_transactions = file_content['ot']
        # print(file_content)

    global blockchain
    global open_transactions
    try:
        with open("blockchain.txt", mode="r") as f:
            file_content = f.readlines()
            blockchain = json.loads(file_content[0])
            updated_blockchain = []
            for block in blockchain:
                converted_tx = [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']),('amount', tx['amount'])])]
                updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                updated_blockchain.append(updated_block)
            
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = OrderedDict(
                    [('sender', tx['sender']),
                    ('recipient', tx['recipient']),
                    ('amount', tx['amount'])]
                )
                updated_transactions.append(updated_transaction)

            open_transactions = updated_transactions

    except (IOError, IndexError):
        print('File not found!')
        genesis_block = Block(0, '', [], 100, 0)
        blockchain = [genesis_block]
        open_transactions = []
    

def valid_proof(transactions, last_hash, proof):
    """ Validate whether hash is valid by meeting PoW criteria """

    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    return guess_hash[0:2] == '00'


def proof_of_work():
    """ Increment nonce until hash meets proof of work criteria  """

    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    """Calculate and return the balance for a participant.

    Arguments:
        :participant: The person for whom to calculate the balance.
    """
    tx_sender = [[tx['amount'] for tx in block.transactions
                  if tx['sender'] == participant] for block in blockchain]

    open_tx_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

    tx_recipient = [[tx['amount'] for tx in block.transactions
                     if tx['recipient'] == participant] for block in blockchain]

    amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(
        tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

    return amount_received - amount_sent


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Append next transaction to blockchain as well as last transaction """

    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)])

    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True

    return False


def get_transaction_value():
    tx_recipient = input('Enter the transaction recipient: ')
    tx_amount = float(input("Your transaction amount please: "))
    return (tx_recipient, tx_amount)


def get_user_choice():
    """ Returns the users choice as string """

    return input("Your choice: ")


def get_last_blockchain_value():
    """ Returns last string of blockchain array """

    return blockchain[-1]


def mine_block():
    """ Wrap open transactions into a block and append to blockchain """

    last_block = get_last_blockchain_value()
    hashed_block = hash_block(last_block)
    proof = proof_of_work()

    reward_transaction = OrderedDict([
        ('sender', 'MINING'), 
        ('recipient', owner), 
        ('amount', MINING_REWARD)
    ])

    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)

    block = Block(
        len(blockchain),
        hashed_block,
        copied_transactions,
        proof
    ) 

    blockchain.append(block)
    return True


def print_blockchain():
    """ Print contents of blockchain to screen """

    for block in blockchain:
        print('Outputting Block: ', block)
    else:
        print('-' * 20)


def verify_chain():
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        # select all transactions bar the reward one.
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid')
            print(block)
            return False

    return True

# Starting conditions
waiting_for_input = True
load_data()

while waiting_for_input:
    print_spacer()
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain')
    print('4: Output participants')
    print('5: Verify transactions')
    print('h: Manipulate the blockchain')
    print('q: To quit')

    user_choice = get_user_choice()

    print('-' * 20)

    if not verify_chain():
        print('Invalid blockchain')
        waiting_for_input = False

    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if (add_transaction(recipient, amount=amount)):
            print('Added transaction')
        else:
            print('Transaction failed - insufficient funds')
        print(open_transactions)

    elif user_choice == '2':
        # time = datetime.datetime.now().time()
        # # print(time)
        if mine_block():
            open_transactions = []
            save_data()

    elif user_choice == '3':
        print_blockchain()

    elif user_choice == '4':
        print(participants)

    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid')
        else:
            print('There are invalid transactions')

    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Chris', 'recipient': 'Max', 'amount': 100}]
            }

    elif user_choice == 'q':
        waiting_for_input = False
        
    else:
        print('Input was invalid, please pick a value from the list!')

    print('Balance of {}: {:6.2f}'.format('James', get_balance('James')))

else:
    print('User left!')
