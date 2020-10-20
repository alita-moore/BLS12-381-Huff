from evm_interface import merge, assemble, setup_computation
from typing import Type
import copy

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
    UPDATED_OPCODES,
)

class CustomComputation(IstanbulComputation):
    opcodes = CUSTOM_OPCODES

class CustomState(IstanbulState):
    computation_class = CustomComputation

class CustomVm(IstanbulVM):
    _state_class: Type[BaseState] = CustomState

code = assemble(
    opcode_values.PUSH1,
    0x1,
    opcode_values.PUSH1,
    0x1,
    SUBTRACT_OPCODE_VALUE
)

computation = setup_computation(CustomVm, code)
comp = computation.apply_message(
        computation.state,
        computation.msg,
        computation.transaction_context,
    )
result = comp.stack_pop1_any()
print(result)