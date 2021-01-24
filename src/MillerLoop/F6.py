from src.MillerLoop.Constants import buffer_f6mul
from src.MillerLoop.F2 import F2
from src.MillerLoop.F1 import F1
from src.MillerLoop.Huff import Huff
from src.MillerLoop.util import debug_points


class F6:
    def __init__(self, huff: Huff, f2: F2, out=0, x=0, y=0, mod=0):
        self.Huff = huff
        self.F2 = f2
        self.f6add_count = 0
        self.f6sub_count = 0
        self.f6mul_count = 0
        self.out = out
        self.x = x
        self.y = y
        self.mod = mod

    def gen_f6add(self, out, x, y, mod):
        self.f6add_count += 1
        self.Huff.pushln("// f6 add")
        x0 = x
        x1 = x0 + 96
        x2 = x1 + 96
        y0 = y
        y1 = y0 + 96
        y2 = y1 + 96
        out0 = out
        out1 = out0 + 96
        out2 = out1 + 96

        _F1 = F1(Huff())
        p0 = F2(Huff(), _F1, out0, x0, y0, mod)
        p1 = F2(Huff(), _F1, out1, x1, y1, mod)
        p2 = F2(Huff(), _F1, out2, x2, y2, mod)

        P = [p0, p1, p2]
        debug_points(P, "F6", "add", self.Huff)

        self.F2 + p0
        self.F2 + p1
        self.F2 + p2
        # self.F2.gen_f2add(out0, x0, y0, mod)
        # self.F2.gen_f2add(out1, x1, y1, mod)
        # self.F2.gen_f2add(out2, x2, y2, mod)

    def gen_f6sub(self, out, x, y, mod):
        self.f6sub_count += 1
        self.Huff.pushln("// f6 sub")
        x0 = x
        x1 = x0 + 96
        x2 = x1 + 96
        y0 = y
        y1 = y0 + 96
        y2 = y1 + 96
        out0 = out
        out1 = out0 + 96
        out2 = out1 + 96

        _F1 = F1(Huff())
        p0 = F2(Huff(), _F1, out0, x0, y0, mod)
        p1 = F2(Huff(), _F1, out1, x1, y1, mod)
        p2 = F2(Huff(), _F1, out2, x2, y2, mod)

        P = [p0, p1, p2]
        debug_points(P, "F6", "sub", self.Huff)

        self.F2 - p0
        self.F2 - p1
        self.F2 - p2

        # self.F2.gen_f2sub(out0, x0, y0, mod)
        # self.F2.gen_f2sub(out1, x1, y1, mod)
        # self.F2.gen_f2sub(out2, x2, y2, mod)

    def gen_f6neg(self, out, x, mod):
        # gen_f6sub(out,f6zero,x,mod)
        # gen_f6sub(out,mod,x,mod)
        x0 = x
        x1 = x0 + 96
        x2 = x1 + 96
        out0 = out
        out1 = out0 + 96
        out2 = out1 + 96

        _huff = self.Huff
        _F1 = F1(self.Huff)
        p0 = F2(_huff, _F1, out0, x0, 0, mod)
        p1 = F2(_huff, _F1, out1, x1, 0, mod)
        p2 = F2(_huff, _F1, out2, x2, 0, mod)

        P = [p0, p1, p2]
        debug_points(P, "F6", "neg", self.Huff)

        -p0
        -p1
        -p2

    def gen_f6mul(self, out, x, y, mod):
        self.f6mul_count += 1
        self.Huff.pushln("// f6 add")
        x0 = x
        x1 = x0 + 96
        x2 = x1 + 96
        y0 = y
        y1 = y0 + 96
        y2 = y1 + 96
        out0 = out
        out1 = out0 + 96
        out2 = out1 + 96
        # temporary variables
        t0 = buffer_f6mul
        t1 = t0 + 96
        t2 = t1 + 96
        t3 = t2 + 96
        t4 = t3 + 96
        t5 = t4 + 96

        _F1 = F1(Huff())
        p0 = F2(Huff(), _F1, t0, x0, y0, mod)
        p1 = F2(Huff(), _F1, t1, x1, y1, mod)
        p2 = F2(Huff(), _F1, t2, x2, y2, mod)
        p3 = F2(Huff(), _F1, t4, x1, x2, mod)
        p4 = F2(Huff(), _F1, t5, y1, y2, mod)
        p5 = F2(Huff(), _F1, t3, t4, t5, mod)
        p6 = F2(Huff(), _F1, t3, t3, t1, mod)
        p7 = F2(Huff(), _F1, t3, t3, t2, mod)
        p8 = F2(Huff(), _F1, t4, x0, x1, mod)
        p9 = F2(Huff(), _F1, t5, y0, y1, mod)
        p10 = F2(Huff(), _F1, out1, t4, t5, mod)
        p11 = F2(Huff(), _F1, out1, out1, t0, mod)
        p12 = F2(Huff(), _F1, out1, out1, t1, mod)
        p13 = F2(Huff(), _F1, out1, out1, t4, mod)
        p14 = F2(Huff(), _F1, t4, x0, x2, mod)
        p15 = F2(Huff(), _F1, t5, y0, y2, mod)
        p16 = F2(Huff(), _F1, out2, t4, t5, mod)
        p17 = F2(Huff(), _F1, out2, out2, t0, mod)
        p18 = F2(Huff(), _F1, out2, out2, t2, mod)
        p19 = F2(Huff(), _F1, out2, out2, t1, mod)
        p20 = F2(Huff(), _F1, out0, t3, t0, mod)

        P = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20]
        debug_points(P, "F6", "mul", self.Huff)

        # algorithm
        self.F2 * p0
        self.F2 * p1
        self.F2 * p2
        # out0
        self.F2 + p3
        self.F2 + p4
        self.F2 * p5
        self.F2 - p6
        self.F2 - p7
        self.F2.gen_mul_by_u_plus_1_fp2(t3, t3, mod)
        # out1
        self.F2 + p8
        self.F2 + p9
        self.F2 * p10
        self.F2 - p11
        self.F2 - p12
        self.F2.gen_mul_by_u_plus_1_fp2(t4, t2, mod)
        self.F2 + p13
        # out2
        self.F2 + p14
        self.F2 + p15
        self.F2 * p16
        self.F2 - p17
        self.F2 - p18
        self.F2 + p19
        self.F2 + p20

        # algorithm
        # self.F2.gen_f2mul(t0, x0, y0, mod) # 0
        # self.F2.gen_f2mul(t1, x1, y1, mod) # 1
        # self.F2.gen_f2mul(t2, x2, y2, mod) # 2
        # out0
        # self.F2.gen_f2add(t4, x1, x2, mod) # 3
        # self.F2.gen_f2add(t5, y1, y2, mod) # 4
        # self.F2.gen_f2mul(t3, t4, t5, mod) # 5
        # self.F2.gen_f2sub(t3, t3, t1, mod) # 6
        # self.F2.gen_f2sub(t3, t3, t2, mod) # 7
        # self.F2.gen_mul_by_u_plus_1_fp2(t3, t3, mod)
        # gen_f2add(out0,t3,t0,mod)	# below
        # out1
        # self.F2.gen_f2add(t4, x0, x1, mod) # 8
        # self.F2.gen_f2add(t5, y0, y1, mod) # 9
        # self.F2.gen_f2mul(out1, t4, t5, mod) # 10
        # self.F2.gen_f2sub(out1, out1, t0, mod) # 11
        # self.F2.gen_f2sub(out1, out1, t1, mod) # 12
        # self.F2.gen_mul_by_u_plus_1_fp2(t4, t2, mod)
        # self.F2.gen_f2add(out1, out1, t4, mod) # 13
        # out2
        # self.F2.gen_f2add(t4, x0, x2, mod) # 14
        # self.F2.gen_f2add(t5, y0, y2, mod) # 15
        # self.F2.gen_f2mul(out2, t4, t5, mod) # 16
        # self.F2.gen_f2sub(out2, out2, t0, mod) # 17
        # self.F2.gen_f2sub(out2, out2, t2, mod) # 18
        # self.F2.gen_f2add(out2, out2, t1, mod) # 19

        # self.F2.gen_f2add(out0, t3, t0, mod) # 20

    def gen_f6sqr(self, out, x, mod):
        self.gen_f6mul(out, x, x, mod)  # TODO: optimize

    def __add__(self, other):
        _out = other.out
        _x = other.x
        _y = other.y
        _mod = other.mod
        self.gen_f6add(_out, _x, _y, _mod)

    def __sub__(self, other):
        _out = other.out
        _x = other.x
        _y = other.y
        _mod = other.mod
        self.gen_f6sub(_out, _x, _y, _mod)

    def __mul__(self, other):
        _out = other.out
        _x = other.x
        _y = other.y
        _mod = other.mod
        self.gen_f6mul(_out, _x, _y, _mod)

    def __neg__(self):
        _out = self.out
        _x = self.x
        _mod = self.mod
        self.gen_f6neg(_out, _x, _mod)
