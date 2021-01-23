from src.MillerLoop.Constants import buffer_f12mul, buffer_f6mul
from src.MillerLoop.F2 import F2
from src.MillerLoop.F6 import F6
from src.MillerLoop.Huff import Huff


class F12:
    def __init__(self, huff: Huff, f2: F2, f6: F6):
        self.Huff = huff
        self.F6 = f6
        self.F2 = f2
        self.f12add_count = 0
        self.f12sub_count = 0
        self.f12mul_count = 0

    def gen_f12add(self, out, x, y, mod):
        self.f12add_count += 1
        self.Huff.pushln("// f6 add")
        x0 = x
        x1 = x0 + 288
        y0 = y
        y1 = y0 + 288
        out0 = out
        out1 = out0 + 288
        self.F6.gen_f6add(out0, x0, y0, mod)
        self.F6.gen_f6add(out1, x1, y1, mod)

    def gen_f12sub(self, out, x, y, mod):
        self.f12sub_count += 1
        self.Huff.pushln("// f6 add")
        x0 = x
        x1 = x0 + 288
        y0 = y
        y1 = y0 + 288
        out0 = out
        out1 = out0 + 288
        self.F6.gen_f6sub(out0, x0, y0, mod)
        self.F6.gen_f6sub(out1, x1, y1, mod)

    def gen_f12mul(self, out, x, y, mod):
        self.f12mul_count += 1
        self.Huff.pushln("// f12 mul")
        x0 = x
        x1 = x0 + 288
        y0 = y
        y1 = y0 + 288
        out0 = out
        out00 = out0
        out01 = out00 + 96
        out02 = out01 + 96
        out1 = out0 + 288
        # temporary variables
        t0 = buffer_f12mul
        t00 = t0
        t01 = t00 + 96
        t02 = t01 + 96
        t1 = t0 + 288
        t10 = t1
        t11 = t10 + 96
        t12 = t11 + 96
        t2 = t1 + 288
        # debugging
        self.F6.gen_f6mul(out0, x0, y0, mod)
        self.F6.gen_f6mul(out1, x1, y1, mod)
        self.F6.gen_f6mul(t0, x0, y0, mod)
        self.F6.gen_f6mul(t1, x1, y1, mod)
        # out1
        self.F6.gen_f6add(t2, x0, x1, mod)
        self.F6.gen_f6add(out1, y0, y1, mod)
        self.F6.gen_f6mul(out1, out1, t2, mod)
        self.F6.gen_f6sub(out1, out1, t0, mod)
        self.F6.gen_f6sub(out1, out1, t1, mod)
        # out0
        self.F2.gen_mul_by_u_plus_1_fp2(t12, t12, mod)
        self.F2.gen_f2add(out00, t00, t12, mod)
        self.F2.gen_f2add(out01, t01, t10, mod)
        self.F2.gen_f2add(out02, t02, t11, mod)

    def gen_f12sqr(self, out, x, mod):
        # gen_f12mul(out,x,x,mod)		# TODO: optimize
        self.Huff.pushln("// f12 sqr")
        x0 = x
        x00 = x0
        x01 = x00 + 96
        x02 = x01 + 96
        x1 = x0 + 288
        x10 = x1
        x11 = x10 + 96
        x12 = x11 + 96
        out0 = out
        out00 = out0
        out01 = out00 + 96
        out02 = out01 + 96
        out1 = out0 + 288
        # temporary variables
        t0 = buffer_f12mul
        t00 = t0
        t01 = t00 + 96
        t02 = t01 + 96
        t1 = t0 + 288
        t10 = t1
        t11 = t10 + 96
        t12 = t11 + 96

        self.F6.gen_f6add(t0, x0, x1, mod)

        # debugging
        # gen_memcopy(out0,t0,288)
        # gen_memcopy(out1,t0,288)

        self.F2.gen_mul_by_u_plus_1_fp2(t12, x12, mod)
        self.F2.gen_f2add(t10, x00, t12, mod)
        self.F2.gen_f2add(t11, x01, x10, mod)
        self.F2.gen_f2add(t12, x02, x11, mod)

        self.F6.gen_f6mul(t0, t0, t1, mod)
        self.F6.gen_f6mul(t1, x0, x1, mod)

        self.F6.gen_f6add(out1, t1, t1, mod)

        self.F6.gen_f6sub(out0, t0, t1, mod)

        self.F2.gen_mul_by_u_plus_1_fp2(t12, t12, mod)
        self.F2.gen_f2sub(out00, out00, t12, mod)
        self.F2.gen_f2sub(out01, out01, t10, mod)
        self.F2.gen_f2sub(out02, out02, t11, mod)

    def gen_f12_conjugate(self, x, mod):
        x1 = x + 288
        self.F6.gen_f6neg(x1, x1, mod)

    # f6 and f12 optimizations for custom operations

    def gen_mul_by_0y0_fp6(self, out, x, y, mod):
        # out is f6, x is f6, y is f2
        x0 = x
        x1 = x0 + 96
        x2 = x1 + 96
        y0 = y
        y1 = y0 + 48
        out0 = out
        out1 = out0 + 96
        out2 = out1 + 96
        t = buffer_f6mul
        self.F2.gen_f2mul(t, x2, y, mod)
        self.F2.gen_f2mul(out2, x1, y, mod)
        self.F2.gen_f2mul(out1, x0, y, mod)
        self.F2.gen_mul_by_u_plus_1_fp2(out0, t, mod)

    def gen_mul_by_xy0_fp6(self, out, x, y, mod):
        # out if f6, x is f6, y is f6
        x0 = x
        x1 = x0 + 96
        x2 = x1 + 96
        y0 = y
        y1 = y0 + 96
        y2 = y1 + 96
        out0 = out
        out1 = out0 + 96
        out2 = out1 + 96
        t0 = buffer_f6mul
        t1 = t0 + 96
        t2 = t1 + 96  # unused
        t3 = t2 + 96
        t4 = t3 + 96
        t5 = t4 + 96
        self.F2.gen_f2mul(t0, x0, y0, mod)
        self.F2.gen_f2mul(t1, x1, y1, mod)

        self.F2.gen_f2mul(t3, x2, y1, mod)
        self.F2.gen_mul_by_u_plus_1_fp2(t3, t3, mod)

        self.F2.gen_f2add(t4, x0, x1, mod)
        self.F2.gen_f2add(t5, y0, y1, mod)
        self.F2.gen_f2mul(out1, t4, t5, mod)
        self.F2.gen_f2sub(out1, out1, t0, mod)
        self.F2.gen_f2sub(out1, out1, t1, mod)

        self.F2.gen_f2mul(out2, x2, y0, mod)
        self.F2.gen_f2add(out2, out2, t1, mod)

        self.F2.gen_f2add(out0, t3, t0, mod)

    def gen_mul_by_xy00z0_fp12(self, out: int, x: int, y: int, mod: int):
        # out is f12, x is f12, y is f6
        x0 = x
        x1 = x0 + 288
        y0 = y
        y1 = y0 + 96
        y2 = y1 + 96
        out0 = out
        out00 = out0
        out01 = out00 + 96
        out02 = out01 + 96
        out1 = out + 288
        t0 = buffer_f12mul
        t00 = t0
        t01 = t00 + 96
        t02 = t01 + 96
        t1 = t0 + 288
        t10 = t1
        t11 = t10 + 96
        t12 = t11 + 96
        t2 = t1 + 288
        t20 = t2
        t21 = t2 + 96
        self.gen_mul_by_xy0_fp6(t0, x0, y, mod)
        self.gen_mul_by_0y0_fp6(t1, x1, y2, mod)
        self.Huff.gen_memcopy(t20, y0, 96)
        self.F2.gen_f2add(t21, y1, y2, mod)
        self.F6.gen_f6add(out1, x0, x1, mod)
        self.gen_mul_by_xy0_fp6(out1, out1, t2, mod)
        self.F6.gen_f6sub(out1, out1, t0, mod)
        self.F6.gen_f6sub(out1, out1, t1, mod)
        self.F2.gen_mul_by_u_plus_1_fp2(t12, t12, mod)
        self.F2.gen_f2add(out00, t00, t12, mod)
        self.F2.gen_f2add(out01, t01, t10, mod)
        self.F2.gen_f2add(out02, t02, t11, mod)
