import functools
import datetime
from collections import OrderedDict
from hash_util import hash_block, hash_string_256
import json
# import pickle

MINING_REWARD = 10
blockchain = []
open_transactions = []
owner = 'James'
participants = { 'Max' }

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
                updated_block = {
                    'previous_hash': block['previous_hash'],
                    'index': block['index'],
                    'proof': block['proof'],
                    'transactions': [OrderedDict(
                        [('sender', tx['sender']),
                        ('recipient', tx['recipient']),
                        ('amount', tx['amount'])
                    ]) for tx in block['transactions']]
                }
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
        genesis_block = {
            'previous_hash': '',
            'index': 0,
            'transactions': [],
            'proof': 100
        }
        blockchain = [genesis_block]
        open_transactions = []
    

load_data()

def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    # print(guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
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
    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of transactions that were already included in blocks of the blockchain
    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == participant] for block in blockchain]
    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of open transactions (to avoid double spending)
    open_tx_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    # This fetches received coin amounts of transactions that were already included in blocks of the blockchain
    # We ignore open transactions here because you shouldn't be able to spend coins before the transaction was confirmed + included in a block
    tx_recipient = [[tx['amount'] for tx in block['transactions']
                     if tx['recipient'] == participant] for block in blockchain]
    amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(
        tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    # Return the total balance
    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns last string of blockchain array """
    return blockchain[-1]


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Append next transaction to blockchain as well as last transaction """

    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }

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
    return input("Your choice: ")


def mine_block():
    # Fetch latest block
    last_block = get_last_blockchain_value()

    # Hash said block
    hashed_block = hash_block(last_block)

    # Should not include reward transaction
    proof = proof_of_work()

    # Miners should be rewarded
    reward_transaction = {
        'sender': 'MINING',
        'recipient': owner,
        'amount': MINING_REWARD
    }

    reward_transaction = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])

    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)

    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    }

    blockchain.append(block)
    return True


def print_blockchain():
    for block in blockchain:
        print('Outputting Block: ', block)
    else:
        print('-' * 20)


def print_spacer():
    print('\n' * 0)
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


waiting_for_input = True

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
