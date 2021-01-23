from src.MillerLoop.Constants import buffer_f2mul
from src.MillerLoop.F1 import F1
from src.MillerLoop.Huff import Huff


class F2:
    def __init__(self, huff: Huff, f1: F1):
        self.Huff = huff
        self.F1 = f1
        self.f2add_count = 0
        self.f2sub_count = 0
        self.f2mul_count = 0

    def gen_f2add(self, out, x, y, mod):
        self.f2add_count += 1
        self.Huff.pushln("// f2 add")
        x0 = x
        x1 = x + 48
        y0 = y
        y1 = y + 48
        out0 = out
        out1 = out + 48

        a = F1(self.Huff, out0, x0, y0, mod)
        b = F1(self.Huff, out1, x1, y1, mod)
        a + b
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
        self.F1.gen_f1sub(out0, x0, y0, mod)
        self.F1.gen_f1sub(out1, x1, y1, mod)

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

        self.F1.gen_f1mul(tmp1, x0, y0, mod)
        self.F1.gen_f1mul(tmp2, x1, y1, mod)
        # gen_f1sub(tmp3,zero,tmp2,mod)
        # gen_f1add(out0,tmp1,tmp3,mod)
        self.F1.gen_f1sub(out0, tmp1, tmp2, mod)  # above sub,add give same result as just this sub
        self.F1.gen_f1add(tmp1, tmp1, tmp2, mod)
        self.F1.gen_f1add(tmp2, x0, x1, mod)
        self.F1.gen_f1add(tmp3, y0, y1, mod)
        self.F1.gen_f1mul(tmp2, tmp2, tmp3, mod)
        self.F1.gen_f1sub(out1, tmp2, tmp1, mod)

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
        self.F1.gen_f1add(tmp0, x0, x1, mod)
        self.F1.gen_f1sub(tmp1, x0, x1, mod)
        self.F1.gen_f1mul(out1, x0, x1, mod)
        self.F1.gen_f1add(out1, out1, out1, mod)
        self.F1.gen_f1mul(out0, tmp0, tmp1, mod)

    def gen_f2neg(self, out, in_, mod):
        # gen_f2sub(out,zero,in_,mod)
        self.F1.gen_f1sub(out, mod, in_, mod)
        self.F1.gen_f1sub(out + 48, mod, in_ + 48, mod)

    def gen_mul_by_u_plus_1_fp2(self, out, x, mod):
        t = buffer_f2mul  # to prevent clobbering
        self.F1.gen_f1sub(t, x, x + 48, mod)
        self.F1.gen_f1add(out + 48, x, x + 48, mod)
        self.Huff.gen_memcopy(out, t, 48)
