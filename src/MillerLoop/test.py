import sys

from src.MillerLoop.Constants import buffer_inputs
from src.MillerLoop.Huff import Huff
from src.MillerLoop import F1, F2, F6, F12, CurveOperations
from src.MillerLoop.MillerLoop import MillerLoop


def gen_test_case_values(huff: Huff):
    # from casey
    inE1 = bytearray.fromhex(
        "0b83dfefb120fab7665a607d749ef1765fbb3cc0ba5827a20a135402c09d987c701ddb5b60f0f5495026817e8ab6ea2e")[
           ::-1]
    inE1 += bytearray.fromhex(
        "15c82e5362493d173e96edb436e396a30b9d3ae5d1a2633c375cfbbf3aed34bbc30448ec6b8102ab2f8da4486d23a717")[
            ::-1]
    huff.gen_memstore(buffer_inputs, inE1)
    inE2 = bytearray.fromhex(
        "16fc2f7ff7eb01f34e97a5d5274390ee168f32ff5803597da434b40fa7778793eaac8cc3e8f0d75f3bf55889258ebea7")[
           ::-1]
    inE2 += bytearray.fromhex(
        "183aa5f5b84721a4efdfc5a759ec88792e3080b8f9207d02eca66082d6076569b84b95e05b3a4b95697909f1dda69d8d")[
            ::-1]
    inE2 += bytearray.fromhex(
        "002e5c809b03e98d5406ae13e3aa6e477b4aa0a0cedef70dafdd5f0b0c2c64152f52837f92870d0c57b21dd62e9ead91")[
            ::-1]
    inE2 += bytearray.fromhex(
        "039dc3bb023f737d7c60f62b4e669843817fe1ed0751a7b750d02c9df5ee87758e7fe7d6fd614b5fe013f35e6fd9ae4d")[
            ::-1]
    huff.gen_memstore(buffer_inputs + 96, inE2)


_huff = Huff()
_F1 = F1.F1(_huff)
_F2 = F2.F2(_huff, _F1)
_F6 = F6.F6(_huff, _F2)
_F12 = F12.F12(_huff, _F2, _F6)
Operations = CurveOperations.CurveOperations(_huff, _F1, _F2, _F6, _F12)
_MillerLoop = MillerLoop(_huff, Operations, _F1, _F12)

# gen_test_case_values(_huff)
_MillerLoop.gen_pairing()
original_stdout = sys.stdout
with open('MillerLoop.huff', 'w') as file:
    sys.stdout = file
    for line in _huff.lines:
        print(line)
    sys.stdout = original_stdout

original = ''.join(open('original.huff', 'r').readlines())
current = ''.join(open('MillerLoop.huff', 'r').readlines())
print(original == current)
