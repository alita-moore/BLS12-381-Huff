from src.MillerLoop.Constants import buffer_f2mul, zero
from src.MillerLoop.F1 import F1
from src.MillerLoop.Huff import Huff
from src.MillerLoop.util import debug_points


class F2:
    def __init__(self, huff: Huff, f1: F1, out=0, x=0, y=0, mod=0):
        self.Huff = huff
        self.F1 = f1
        self.f2add_count = 0
        self.f2sub_count = 0
        self.f2mul_count = 0

        self.out = out
        self.x = x
        self.y = y
        self.mod = mod

    def gen_f2add(self, out, x, y, mod):
        self.f2add_count += 1
        self.Huff.pushln("// f2 add")
        x0 = x
        x1 = x + 48
        y0 = y
        y1 = y + 48
        out0 = out
        out1 = out + 48

        p0 = F1(self.Huff, out0, x0, y0, mod)

        p1 = F1(self.Huff, out1, x1, y1, mod)

        # debugging -- this investigates the repetition of points
        # _F = "F2"
        # _key = "add"
        # _P = [p0, p1]
        debug_points([p0, p1], "F2", "add", self.Huff)

        self.F1 + p0
        self.F1 + p1
        # self.F1.gen_f1add(out0, x0, y0, mod)
        # self.F1.gen_f1add(out1, x1, y1, mod)

    def gen_f2sub(self, out, x, y, mod):
        self.f2sub_count += 1
        self.Huff.pushln("// f2 sub")
        x0 = x
        x1 = x + 48
        y0 = y
        y1 = y + 48
        out0 = out
        out1 = out + 48

        p0 = F1(self.Huff, out0, x0, y0, mod)
        p1 = F1(self.Huff, out1, x1, y1, mod)

        debug_points([p0, p1], "F2", "sub", self.Huff)

        self.F1 - p0
        self.F1 - p1
        # self.F1.gen_f1sub(out0, x0, y0, mod)
        # self.F1.gen_f1sub(out1, x1, y1, mod)

    def gen_f2mul(self, out, x, y, mod):
        self.f2mul_count += 1
        self.Huff.pushln("// f2 mul")
        # get offsets
        x0 = x
        x1 = x + 48
        y0 = y
        y1 = y + 48
        out0 = out
        out1 = out + 48
        # temporary values
        tmp1 = buffer_f2mul
        tmp2 = tmp1 + 48
        tmp3 = tmp2 + 48

        p0 = F1(Huff(), tmp1, x0, y0, mod)
        p1 = F1(Huff(), tmp2, x1, y1, mod)
        p2 = F1(Huff(), out0, tmp1, tmp2, mod)
        p3 = F1(Huff(), tmp1, tmp1, tmp2, mod)
        p4 = F1(Huff(), tmp2, x0, x1, mod)
        p5 = F1(Huff(), tmp3, y0, y1, mod)
        p6 = F1(Huff(), tmp2, tmp2, tmp3, mod)
        p7 = F1(Huff(), out1, tmp2, tmp1, mod)

        P = [p0, p1, p2, p3, p4, p5, p6, p7]
        debug_points(P, "F2", "mul", self.Huff)

        self.F1 * p0
        self.F1 * p1
        # gen_f1sub(tmp3,zero,tmp2,mod)
        # gen_f1add(out0,tmp1,tmp3,mod)
        self.F1 - p2 # above sub,add give same result as just this sub
        self.F1 + p3
        self.F1 + p4
        self.F1 + p5
        self.F1 * p6
        self.F1 - p7

    def gen_f2sqr(self, out, x, mod):
        self.f2mul_count += 1
        self.Huff.pushln("// f2sqr")

        # get offsets
        x0 = x
        x1 = x + 48
        out0 = out
        out1 = out + 48
        tmp0 = buffer_f2mul
        tmp1 = tmp0 + 48

        p0 = F1(Huff(), tmp0, x0, x1, mod)
        p1 = F1(Huff(), tmp1, x0, x1, mod)
        p2 = F1(Huff(), out1, x0, x1, mod)
        p3 = F1(Huff(), out1, out1, out1, mod)
        p4 = F1(Huff(), out0, tmp0, tmp1, mod)

        P = [p0, p1, p2, p3, p4]
        debug_points(P, "F2", "sqr", self.Huff)

        self.F1 + p0
        self.F1 - p1
        self.F1 * p2
        self.F1 + p3
        self.F1 * p4
        # self.F1.gen_f1addd(tmp0, x0, x1, mod)
        # self.F1.gen_f1sub(tmp1, x0, x1, mod)
        # self.F1.gen_f1mul(out1, x0, x1, mod)
        # self.F1.gen_f1add(out1, out1, out1, mod)
        # self.F1.gen_f1mul(out0, tmp0, tmp1, mod)

    def gen_f2neg(self, out, in_, mod):
        # gen_f2sub(out,zero,in_,mod)
        p0 = F1(Huff(), out, mod, in_, mod)
        p1 = F1(Huff(), out + 48, mod, in_ + 48, mod)

        P = [p0, p1]
        debug_points(P, "F2", "neg", self.Huff)

        self.F1 - p0
        self.F1 - p1

    def gen_mul_by_u_plus_1_fp2(self, out, x, mod):
        t = buffer_f2mul  # to prevent clobbering

        p0 = F1(Huff(), t, x, x + 48, mod)
        p1 = F1(Huff(), out + 48, x, x + 48, mod)

        P = [p0, p1]
        debug_points(P, "F2", "gen_mul_by_u_plus_1_fp2", self.Huff)

        self.F1 - p0
        self.F1 + p1
        self.Huff.gen_memcopy(out, t, 48)

    def __add__(self, other):
        _out = other.out
        _x = other.x
        _y = other.y
        _mod = other.mod
        self.gen_f2add(_out, _x, _y, _mod)

    def __sub__(self, other):
        _out = other.out
        _x = other.x
        _y = other.y
        _mod = other.mod
        self.gen_f2sub(_out, _x, _y, _mod)

    def __mul__(self, other):
        _out = other.out
        _x = other.x
        _y = other.y
        _mod = other.mod
        self.gen_f2mul(_out, _x, _y, _mod)

    def __neg__(self):
        _out = self.out
        _x = self.x
        _mod = self.mod
        self.gen_f2neg(_out, _x, _mod)

    def __pow__(self, power):
        if not power == 2:
            raise ArithmeticError("only squaring is supported")
        _out = self.out
        _x = self.x
        _mod = self.mod
        self.gen_f2sqr(_out, _x, _mod)
