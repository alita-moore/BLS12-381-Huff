from src.MillerLoop.Constants import f1zero
from src.MillerLoop.Huff import Huff

class F1_:
    def __init__(self, out=0, x=0, y=0, mod=0):
        self.out = out
        self.x = x
        self.y = y
        self.mod = mod

class F1:
    def __init__(self, huff: Huff, out=0, x=0, y=0, mod=0):
        self.out = out
        self.x = x
        self.y = y
        self.mod = mod
        self.Huff = huff
        self.addmod384_count = 0
        self.submod384_count = 0
        self.mulmodmont384_count = 0

    def gen_f1add(self, out, x, y, mod):
        self.Huff.gen_evm384_offsets(out, x, y, mod, "addmod384")
        self.addmod384_count += 1

    def gen_f1sub(self, out, x, y, mod):
        self.Huff.gen_evm384_offsets(out, x, y, mod, "submod384")
        self.submod384_count += 1

    def gen_f1mul(self, out, x, y, mod):
        self.Huff.gen_evm384_offsets(out, x, y, mod, "mulmodmont384")
        self.mulmodmont384_count += 1

    def gen_f1neg(self, out, x, mod):
        self.Huff.gen_evm384_offsets(out, f1zero, x, mod, "submod384")
        self.submod384_count += 1

    def __add__(self, other):
        self.gen_f1add(self.out, self.x, self.y, self.mod)
        _out = other.out
        _x = other.x
        _y = other.y
        _mod = other.mod
        self.gen_f1add(_out, _x, _y, _mod)





