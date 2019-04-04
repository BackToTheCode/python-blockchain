# Library imports
import functools
import datetime
from collections import OrderedDict
import json
import pickle

# Custom libraries and classes
from utils.hash_util import hash_block, hash_string_256
from utils.formatting_util import print_spacer
from blocks.block import Block
from transactions.transaction import Transaction
from utils.verification import Verification
from node.node import Node
# from old_node.node import Node

blockchain = []
open_transactions = []
owner = 'James'
participants = { 'Max', 'Anna' }

# Starting conditions
node = Node()
node.start()
# node.listen_for_input()


