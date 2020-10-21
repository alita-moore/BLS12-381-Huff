from evm_interface import merge, assemble, setup_computation, instantiate_vm
from typing import Type
import copy
from typing import NewType, Callable, TypeVar, Union, Type, AnyStr
import copy
import re
import binascii
from abc import ABCMeta, abstractmethod

from eth_hash.auto import keccak
from eth.vm.message import Message
from eth.vm import opcode_values
from eth.consensus import ConsensusContext
from eth.rlp.headers import BlockHeader
from eth.db.chain import ChainDB
from eth.db.atomic import AtomicDB
from eth.vm.chain_context import ChainContext
from collections.abc import Mapping
from eth import constants
from eth.vm.computation import BaseComputation
from eth.vm.forks.istanbul import IstanbulVM
from eth.vm.forks.istanbul.computation import IstanbulComputation
from eth.vm.forks.istanbul.opcodes import ISTANBUL_OPCODES
from eth.vm.forks.istanbul.state import IstanbulState
from eth.vm.opcode import as_opcode
from eth.vm.state import BaseState
from eth.vm import opcode_values

SUBTRACT_OPCODE_VALUE = 0xa5
SUBTRACT_MNEMONIC = 'SUBTRACT'

def sub(computation: BaseComputation) -> None:
    left, right = computation.stack_pop_ints(2)

    result = (2*left - right) & constants.UINT_256_MAX

    computation.stack_push_int(result)

UPDATED_OPCODES = {
    SUBTRACT_OPCODE_VALUE: as_opcode(
        logic_fn=sub,
        mnemonic=SUBTRACT_MNEMONIC,
        gas_cost=constants.GAS_LOW,
    )
}

CUSTOM_OPCODES = merge(
  copy.deepcopy(ISTANBUL_OPCODES),
  UPDATED_OPCODES
)

class CustomComputation(IstanbulComputation):
    opcodes = CUSTOM_OPCODES

class CustomState(IstanbulState):
    computation_class = CustomComputation

class CustomVm(IstanbulVM):
    _state_class: Type[BaseState] = CustomState

class EVM():
  def __init__(self):
    self.VM = instantiate_vm(CustomVm)
    self.computation = setup_computation(self.VM, b"")
  def execute(self, code):
    pass
  
  def PUSH1(self, val):
    print(val)
    code = assemble(opcode_values.PUSH1, val)
    comp = setup_computation(self.VM, code)
    self.computation = self.computation.apply_message(
      self.computation.state,
      comp.msg,
      self.computation.transaction_context
    )
    print([raw_val for val_type, raw_val in self.computation._stack.values])
    # comp.opcodes[opcode_values.PUSH1](self.computation)
    # self.execute(code)
  def SUBTRACT(self):
    self.computation.opcodes[opcode_values.SUB](self.computation)
    # self.execute(code)
  def POP1(self):
    return self.computation.stack_pop1_any()

evm = EVM()
evm.PUSH1(b'\x01')
evm.PUSH1(b'\x02')
evm.SUBTRACT()
result = evm.POP1()
print(result)