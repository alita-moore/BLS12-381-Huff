from eth._utils.datatypes import Configurable
from eth.abc import ABC
from eth.vm.computation import BaseComputation
from eth.vm.opcode import as_opcode
from eth_utils import to_canonical_address
from eth.vm.message import Message
from eth.vm import opcode_values
from eth import constants
from eth.chains.mainnet import MainnetChain
from eth.db.atomic import AtomicDB
from eth_utils import to_wei, encode_hex
MOCK_ADDRESS = constants.ZERO_ADDRESS
DEFAULT_INITIAL_BALANCE = to_wei(10000, 'ether')
GENESIS_PARAMS = {
    'parent_hash': constants.GENESIS_PARENT_HASH,
    'uncles_hash': constants.EMPTY_UNCLE_HASH,
    'coinbase': constants.ZERO_ADDRESS,
    'transaction_root': constants.BLANK_ROOT_HASH,
    'receipt_root': constants.BLANK_ROOT_HASH,
    'difficulty': constants.GENESIS_DIFFICULTY,
    'block_number': constants.GENESIS_BLOCK_NUMBER,
    'gas_limit': constants.GENESIS_GAS_LIMIT,
    'extra_data': constants.GENESIS_EXTRA_DATA,
    'nonce': constants.GENESIS_NONCE
}
GENESIS_STATE = {
    MOCK_ADDRESS: {
        "balance": DEFAULT_INITIAL_BALANCE,
        "nonce": 0,
        "code": b'',
        "storage": {}
    }
}
chain = MainnetChain.from_genesis(AtomicDB(), GENESIS_PARAMS, GENESIS_STATE)
def add(computation):
  return 1
add_op = as_opcode(add, "ADD", 1)
def gen_context(chain):
  CANONICAL_ADDRESS_A = to_canonical_address("0x0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6")
  CANONICAL_ADDRESS_B = to_canonical_address("0xcd1722f3947def4cf144679da39c4c32bdc35681")
  state = chain.get_vm().state
  message = Message(
    to=CANONICAL_ADDRESS_A,
    sender=CANONICAL_ADDRESS_B,
    create_address=None,
    value=0,
    data=b'',
    code=b'',
    gas=1000000,
  )
  tx_context = chain.get_vm()._state_class.transaction_context_class(gas_price=1, origin=CANONICAL_ADDRESS_B)
  return state, message, tx_context

state, message, tx = gen_context(chain)
test = chain.get_vm()._state_class.computation_class(state, message, tx)