from evm_interface import merge, assemble, setup_computation, instantiate_vm
from typing import Type
import copy

from eth.vm import opcode_values as OP
from eth import constants
from eth.vm.computation import BaseComputation
from eth.vm.forks.istanbul import IstanbulVM
from eth.vm.forks.istanbul.computation import IstanbulComputation
from eth.vm.forks.istanbul.opcodes import ISTANBUL_OPCODES
from eth.vm.forks.istanbul.state import IstanbulState
from eth.vm.opcode import as_opcode
from eth.vm.state import BaseState
from eth.exceptions import InsufficientStack

SUBTRACT_OPCODE_VALUE = 0xa5
SUBTRACT_MNEMONIC = 'SUBTRACT'


def sub(computation: BaseComputation) -> None:
    left, right = computation.stack_pop_ints(2)

    result = (left - right) & constants.UINT_256_MAX

    computation.stack_push_int(result)


UPDATED_OPCODES = {
    OP.SUB: as_opcode(
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
        self.code = bytearray()

    def _get_stack(self):
        return [raw_val for val_type, raw_val in self.computation._stack.values]

    def _pop_stack(self):
        stack = bytearray()
        while True:
            try:
                stack.extend(self.pop1())
            except InsufficientStack:
                stack.reverse()
                return stack

    def _assemble(self, *instructions):
        for instruction in instructions:
            self.code.extend(self._to_byte(instruction))

    def _to_byte(self, val):
        if isinstance(val, int):
            return bytes([val])
        else:
            return val

    def _apply_message(self, code):
        comp = setup_computation(self.VM, code)
        self.computation = comp.apply_message(
              comp.state,
              comp.msg,
              comp.transaction_context
        )

    def execute(self):
        code = assemble(self.code)
        self._apply_message(code)
        stack = self._pop_stack()
        self._apply_message(code)
        return stack # return final state

    def push1(self, val):
        self._assemble([OP.PUSH1, val])
        print("PUSH %s" % val)
        print(assemble(self.code))

    def subtract(self):
        print("SUBTRACT")
        self._assemble([OP.SUB])
        print(assemble(self.code))

    def pop1(self):
        return self._to_byte(self.computation.stack_pop1_any())


evm = EVM()
evm.push1(0x01)
evm.push1(0x02)
evm.push1(0x01)
evm.push1(0x02)
evm.push1(0x01)
evm.push1(0x02)
evm.subtract()

print(evm.execute())
