from src.MillerLoop.Constants import buffer_f6mul
from src.MillerLoop.F2 import F2
from src.MillerLoop.Huff import Huff


class F6:
    def __init__(self, huff: Huff, f2: F2):
        self.Huff = huff
        self.F2 = f2
        self.f6add_count = 0
        self.f6sub_count = 0
        self.f6mul_count = 0

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
        self.F2.gen_f2add(out0, x0, y0, mod)
        self.F2.gen_f2add(out1, x1, y1, mod)
        self.F2.gen_f2add(out2, x2, y2, mod)

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
        self.F2.gen_f2sub(out0, x0, y0, mod)
        self.F2.gen_f2sub(out1, x1, y1, mod)
        self.F2.gen_f2sub(out2, x2, y2, mod)

    def gen_f6neg(self, out, x, mod):
        # gen_f6sub(out,f6zero,x,mod)
        # gen_f6sub(out,mod,x,mod)
        x0 = x
        x1 = x0 + 96
        x2 = x1 + 96
        out0 = out
        out1 = out0 + 96
        out2 = out1 + 96
        self.F2.gen_f2neg(out0, x0, mod)
        self.F2.gen_f2neg(out1, x1, mod)
        self.F2.gen_f2neg(out2, x2, mod)

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
        # algorithm
        self.F2.gen_f2mul(t0, x0, y0, mod)
        self.F2.gen_f2mul(t1, x1, y1, mod)
        self.F2.gen_f2mul(t2, x2, y2, mod)
        # out0
        self.F2.gen_f2add(t4, x1, x2, mod)
        self.F2.gen_f2add(t5, y1, y2, mod)
        self.F2.gen_f2mul(t3, t4, t5, mod)
        self.F2.gen_f2sub(t3, t3, t1, mod)
        self.F2.gen_f2sub(t3, t3, t2, mod)
        self.F2.gen_mul_by_u_plus_1_fp2(t3, t3, mod)
        # gen_f2add(out0,t3,t0,mod)	# below
        # out1
        self.F2.gen_f2add(t4, x0, x1, mod)
        self.F2.gen_f2add(t5, y0, y1, mod)
        self.F2.gen_f2mul(out1, t4, t5, mod)
        self.F2.gen_f2sub(out1, out1, t0, mod)
        self.F2.gen_f2sub(out1, out1, t1, mod)
        self.F2.gen_mul_by_u_plus_1_fp2(t4, t2, mod)
        self.F2.gen_f2add(out1, out1, t4, mod)
        # out2
        self.F2.gen_f2add(t4, x0, x2, mod)
        self.F2.gen_f2add(t5, y0, y2, mod)
        self.F2.gen_f2mul(out2, t4, t5, mod)
        self.F2.gen_f2sub(out2, out2, t0, mod)
        self.F2.gen_f2sub(out2, out2, t2, mod)
        self.F2.gen_f2add(out2, out2, t1, mod)

        self.F2.gen_f2add(out0, t3, t0, mod)

    def gen_f6sqr(self, out, x, mod):
        self.gen_f6mul(out, x, x, mod)  # TODO: optimize
