# Library imports
from uuid import uuid4

# Custom libraries and classes
from utils.formatting_util import print_spacer
from blockchain.blockchain import Blockchain
from utils.verification import Verification

class Node:
    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'JAMES'
        self.blockchain = Blockchain(self.id)

    def get_user_choice(self):
        """ Returns the users choice as string """

        return input("Your choice: ")

    def print_blockchain(self):
        """ Print contents of blockchain to screen """

        for block in self.blockchain.chain:
            print('Outputting Block: ', block)
        else:
            print_spacer()

    def get_transaction_value(self):
        tx_recipient = input('Enter the transaction recipient: ')
        tx_amount = float(input("Your transaction amount please: "))
        return (tx_recipient, tx_amount)

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print_spacer()
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain')
            print('4: Verify transactions')
            print('q: To quit')

            user_choice = self.get_user_choice()

            print_spacer()

            if not Verification.verify_chain(self.blockchain.chain):
                print('Invalid blockchain')
                waiting_for_input = False

            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                # Add transaction amount to blockchain
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Added transaction')
                else:
                    print('Transaction failed - insufficient funds')
                print(self.blockchain.get_open_transactions())

            elif user_choice == '2':
                self.blockchain.mine_block()
                    
            elif user_choice == '3':
                self.print_blockchain()

            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid')
                else:
                    print('There are invalid transactions')

            elif user_choice == 'q':
                waiting_for_input = False
                
            else:
                print('Input was invalid, please pick a value from the list!')

            print('Balance of {}: {:6.2f}'.format(self.id, self.blockchain.get_balance()))

        else:
            print('User left!')