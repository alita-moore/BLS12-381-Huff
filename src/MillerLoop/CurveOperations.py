from src.MillerLoop import F1
from src.MillerLoop.Constants import buffer_Eadd, f12one, mod, buffer_line, zero, buffer_Edouble
from src.MillerLoop.F12 import F12
from src.MillerLoop.F2 import F2
from src.MillerLoop.F6 import F6
from src.MillerLoop.Huff import Huff


class CurveOperations:
    def __init__(self, huff: Huff, f1: F1, f2: F2, f6: F6, f12: F12):
        self.Huff = huff
        self.F1 = f1
        self.F2 = f2
        self.F6 = f6
        self.F12 = f12

    def gen_Eadd__madd_2001_b(self, f, XYZout, XYZ1, XYZ2, mod):
        self.Huff.pushln("/////////")
        self.Huff.pushln("// Eadd https://hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#addition-add-2001-b")
        # inputs/ouput
        X1 = XYZ1
        Y1 = X1 + int(f[1]) * 48
        Z1 = Y1 + int(f[1]) * 48
        X2 = XYZ2
        Y2 = X2 + int(f[1]) * 48
        Z2 = Y2 + int(f[1]) * 48
        X3 = XYZout
        Y3 = X3 + int(f[1]) * 48
        Z3 = Y3 + int(f[1]) * 48
    # ZZ1 = Z1^2
    # ZZZ1 = Z1*ZZ1
    # ZZ2 = Z2^2
    # ZZZ2 = Z2*ZZ2
    # A = X1*ZZ2
    # B = X2*ZZ1-A
    # c = Y1*ZZZ2
    # d = Y2*ZZZ1-c
    # e = B^2
    # f = B*e
    # g = A*e
    # h = Z1*Z2
    # f2g = 2*g+f
    # X3 = d^2-f2g
    # Z3 = B*h
    # gx = g-X3
    # Y3 = d*gx-c*f
        # temp vars
        ZZ1 = buffer_Eadd
        ZZZ1 = ZZ1 + int(f[1]) * 48
        ZZ2 = ZZZ1 + int(f[1]) * 48
        ZZZ2 = ZZ2 + int(f[1]) * 48
        A = ZZZ2 + int(f[1]) * 48
        B = A + int(f[1]) * 48
        c = B + int(f[1]) * 48
        d = c + int(f[1]) * 48
        e = d + int(f[1]) * 48
        f_ = e + int(f[1]) * 48
        g = f_ + int(f[1]) * 48
        h = g + int(f[1]) * 48
        f2g = h + int(f[1]) * 48
        gx = f2g + int(f[1]) * 48

        self.Huff.pushln("ZZ1 = Z1^2")
        self.F1.self.gen_fmul(f, ZZ1, Z1, Z1, mod)
        self.Huff.pushln("ZZZ1 = Z1*ZZ1")
        self.gen_fmul(f, ZZZ1, Z1, ZZ1, mod)
        self.Huff.pushln("ZZ2 = Z2^2")
        self.gen_fmul(f, ZZ2, Z2, Z2, mod)
        self.Huff.pushln("ZZZ2 = Z2*ZZ2")
        self.gen_fmul(f, ZZZ2, Z2, ZZ2, mod)
        self.Huff.pushln("A = X1*ZZ2")
        self.gen_fmul(f, A, X1, ZZ2, mod)
        self.Huff.pushln("B = X2*ZZ1-A")
        self.gen_fmul(f, B, X2, ZZ1, mod)
        self.gen_fsub(f, B, B, A, mod)
        self.Huff.pushln("c = Y1*ZZZ2")
        self.gen_fmul(f, c, Y1, ZZZ2, mod)
        self.Huff.pushln("d = Y2*ZZZ1-c")
        self.gen_fmul(f, d, Y2, ZZZ1, mod)
        self.gen_fsub(f, d, d, c, mod)
        self.Huff.pushln("e = B^2")
        self.gen_fmul(f, e, B, B, mod)
        self.Huff.pushln("f = B*e")
        self.gen_fmul(f, f_, B, e, mod)
        self.Huff.pushln("g = A*e")
        self.gen_fmul(f, g, A, e, mod)
        self.Huff.pushln("h = Z1*Z2")
        self.gen_fmul(f, h, Z1, Z2, mod)
        self.Huff.pushln("f2g = 2*g+f")
        self.gen_fadd(f, f2g, g, g, mod)
        self.gen_fadd(f, f2g, f2g, f_, mod)
        self.Huff.pushln("X3 = d^2-f2g")
        self.gen_fmul(f, X3, d, d, mod)
        self.gen_fsub(f, X3, X3, f2g, mod)
        self.Huff.pushln("Z3 = B*h")
        self.gen_fmul(f, Z3, B, h, mod)
        self.Huff.pushln("gx = g-X3")
        self.gen_fsub(f, gx, g, X3, mod)
        self.Huff.pushln("Y3 = d*gx-c*f")
        self.gen_fmul(f, Y3, d, g, mod)
        self.gen_fmul(f, c, c, f_, mod)  # clobber c
        self.gen_fsub(f, Y3, Y3, c, mod)

        self.Huff.pushln("// E add")
        self.Huff.pushln("/////////")

    def gen_Eadd__madd_2007_bl(self, f, XYZout, XYZ1, XYZ2, line1, mod):
        self.Huff.pushln("/////////")
        self.Huff.pushln("// Eadd https://hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#addition-madd-2007-bl")
        # for pairing:
        #   line0 is useful for pairings which reuse that intermediate value in this calculation
        #   XYZout and XYZ are both T, and E2 point, and XYZ2 is Q which is affine E2 point

        # inputs/ouput
        X1 = XYZ1
        Y1 = X1 + int(f[1]) * 48
        Z1 = Y1 + int(f[1]) * 48
        X2 = XYZ2
        Y2 = X2 + int(f[1]) * 48
        Z2 = Y2 + int(f[1]) * 48
        X3 = XYZout
        Y3 = X3 + int(f[1]) * 48
        Z3 = Y3 + int(f[1]) * 48

        # temp vars
        Z1Z1 = buffer_Eadd
        U2 = Z1Z1 + int(f[1]) * 48
        S2 = U2 + int(f[1]) * 48
        H = S2 + int(f[1]) * 48
        HH = H + int(f[1]) * 48
        I = HH + int(f[1]) * 48
        J = I + int(f[1]) * 48
        V = J + int(f[1]) * 48
        r = line1 if line1 else V + int(f[1]) * 48

        # Z1Z1 = Z1^2
        self.Huff.pushln("// Z1Z1 = Z1^2")
        self.gen_fsqr(f, Z1Z1, Z1, mod)
        # U2 = X2*Z1Z1
        self.Huff.pushln("// U2 = X2*Z1Z1")
        self.gen_fmul(f, U2, X2, Z1Z1, mod)
        # S2 = Y2*Z1*Z1Z1
        self.Huff.pushln("// S2 = Y2*Z1*Z1Z1")
        self.gen_fmul(f, S2, Y2, Z1, mod)
        self.gen_fmul(f, S2, S2, Z1Z1, mod)
        # H = U2-X1
        self.Huff.pushln("// H = U2-X1")
        self.gen_fsub(f, H, U2, X1, mod)
        # HH = H^2
        self.Huff.pushln("// HH = H^2")
        self.gen_fsqr(f, HH, H, mod)
        # I = 4*HH
        self.Huff.pushln("// I = 4*HH")
        self.gen_fadd(f, I, HH, HH, mod)
        self.gen_fadd(f, I, I, I, mod)
        # J = H*I
        self.Huff.pushln("// J = H*I")
        self.gen_fmul(f, J, H, I, mod)
        # line0 = 2*(S2-Y1)
        self.Huff.pushln("// r = 2*(S2-Y1)")
        self.gen_fsub(f, r, S2, Y1, mod)
        self.gen_fadd(f, r, r, r, mod)
        # V = X1*I
        self.Huff.pushln("// V = X1*I")
        self.gen_fmul(f, V, X1, I, mod)
        # X3 = r^2-J-2*V
        self.Huff.pushln("// X3 = r^2-J-2*V")
        self.gen_fsqr(f, X3, r, mod)
        self.gen_fsub(f, X3, X3, J, mod)
        self.gen_fsub(f, X3, X3, V, mod)
        self.gen_fsub(f, X3, X3, V, mod)
        # Y3 = r*(V-X3)-2*Y1*J
        self.Huff.pushln("// Y3 = r*(V-X3)-2*Y1*J")
        self.gen_fmul(f, J, J, Y1, mod)
        self.gen_fsub(f, Y3, V, X3, mod)
        self.gen_fmul(f, Y3, Y3, r, mod)
        self.gen_fsub(f, Y3, Y3, J, mod)
        self.gen_fsub(f, Y3, Y3, J, mod)
        """
      self.gen_fsub(f,Y3,V,X3,mod)
      self.gen_fmul(f,Y3,r,Y3,mod)
      self.gen_fmul(f,V,Y1,J,mod)	# overwriting V
      self.gen_fsub(f,Y3,Y3,V,mod)
      self.gen_fsub(f,Y3,Y3,V,mod)
      """
        # Z3 = (Z1+H)^2-Z1Z1-HH
        self.Huff.pushln("// Z3 = (Z1+H)^2-Z1Z1-HH")
        self.gen_fadd(f, Z3, Z1, H, mod)
        self.gen_fsqr(f, Z3, Z3, mod)
        self.gen_fsub(f, Z3, Z3, Z1Z1, mod)
        self.gen_fsub(f, Z3, Z3, HH, mod)

        self.Huff.pushln("// E add")
        self.Huff.pushln("/////////")

        return I, J, r  # these are useful for pairing

    def gen_Edouble__dbl_2009_alnr(self, f, XYZout, XYZ, line0, mod):
        # XYZout is E2 point, XYZ is E2 point		(note: for our pairing algorithm, T=XYZout=XYZ)
        # line is an extra f2 point, not part of dbl operation, but useful for pairing's line evaluation
        self.Huff.pushln("///////////")
        self.Huff.pushln("// Edouble https://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#doubling-dbl-2009-alnr")

        # inputs/ouput
        X1 = XYZ
        Y1 = X1 + int(f[1]) * 48
        Z1 = Y1 + int(f[1]) * 48
        X3 = XYZout
        Y3 = X3 + int(f[1]) * 48
        Z3 = Y3 + int(f[1]) * 48
        # self.Huff.pushln("gen_Edouble__dbl_2009_alnr(",X1,Y1,Z1,X3,Y3,Z3,")")

        """
      A = X1^2
      B = Y1^2
      ZZ = Z1^2
      C = B^2
      D = 2*((X1+B)^2-A-C)
      E = 3*A
      F = E^2
      X3 = F-2*D
      Y3 = E*(D-X3)-8*C
      Z3 = (Y1+Z1)^2-B-ZZ
      """
        A = buffer_Edouble
        B = A + int(f[1]) * 48
        ZZ = B + int(f[1]) * 48
        C = ZZ + int(f[1]) * 48
        D = C + int(f[1]) * 48
        E = D + int(f[1]) * 48
        F = E + int(f[1]) * 48

        self.Huff.pushln("// A = X1^2")
        self.gen_fsqr(f, A, X1, mod)
        self.Huff.pushln("// B = Y1^2")
        self.gen_fsqr(f, B, Y1, mod)
        self.Huff.pushln("// ZZ = Z1^2")
        self.gen_fsqr(f, ZZ, Z1, mod)
        self.Huff.pushln("// C = B^2")
        self.gen_fsqr(f, C, B, mod)
        self.Huff.pushln("// D = 2*((X1+B)^2-A-C)")
        self.gen_fadd(f, D, X1, B, mod)
        self.gen_fsqr(f, D, D, mod)
        self.gen_fsub(f, D, D, A, mod)
        self.gen_fsub(f, D, D, C, mod)
        self.gen_fadd(f, D, D, D, mod)
        self.Huff.pushln("// E = 3*A")
        self.gen_fadd(f, E, A, A, mod)
        self.gen_fadd(f, E, E, A, mod)
        self.Huff.pushln("// F = E^2")
        self.gen_fsqr(f, F, E, mod)
        # note: the following is not part of the dbl, but is useful for line evaluation
        if line0:
            self.Huff.pushln("// line0 = E+X1, this is useful for pairing")
            self.gen_fadd(f, line0, E, X1, mod)
        self.Huff.pushln("// X3 = F-2*D")
        self.gen_fsub(f, X3, F, D, mod)
        self.gen_fsub(f, X3, X3, D, mod)
        self.Huff.pushln("// Z3 = (Y1+Z1)^2-B-ZZ")
        self.gen_fadd(f, Z3, Y1, Z1, mod)
        self.gen_fsqr(f, Z3, Z3, mod)
        self.gen_fsub(f, Z3, Z3, B, mod)
        self.gen_fsub(f, Z3, Z3, ZZ, mod)
        self.Huff.pushln("// Y3 = E*(D-X3)-8*C")
        self.gen_fsub(f, Y3, D, X3, mod)
        self.gen_fmul(f, Y3, E, Y3, mod)
        self.gen_fadd(f, C, C, C, mod)  # overwriting C
        self.gen_fadd(f, C, C, C, mod)
        self.gen_fadd(f, C, C, C, mod)
        self.gen_fsub(f, Y3, Y3, C, mod)
        self.Huff.pushln("// E double")
        self.Huff.pushln("////////////")
        return A, B, E, F, ZZ, X1

    def gen_Edouble__dbl_2009_l(self, f, XYZout, XYZ, mod):
        self.Huff.pushln("///////////")
        self.Huff.pushln("// Edouble https://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#doubling-dbl-2009-l")

        # inputs/ouput
        X1 = XYZ
        Y1 = X1 + int(f[1]) * 48
        Z1 = Y1 + int(f[1]) * 48
        X3 = XYZout
        Y3 = X3 + int(f[1]) * 48
        Z3 = Y3 + int(f[1]) * 48

        """
      A = X1^2
      B = Y1^2
      C = B^2
      D = 2*((X1+B)^2-A-C)
      E = 3*A
      F = E^2
      X3 = F-2*D
      Y3 = E*(D-X3)-8*C
      Z3 = 2*Y1*Z1
      """
        A = buffer_Edouble
        B = A + int(f[1]) * 48
        C = B + int(f[1]) * 48
        D = C + int(f[1]) * 48
        E = D + int(f[1]) * 48
        F = E + int(f[1]) * 48

        self.Huff.pushln("// A = X1^2")
        self.gen_fmul(f, A, X1, X1, mod)
        self.Huff.pushln("// B = Y1^2")
        self.gen_fmul(f, B, Y1, Y1, mod)
        self.Huff.pushln("// C = B^2")
        self.gen_fmul(f, C, B, B, mod)
        self.Huff.pushln("// D = 2*((X1+B)^2-A-C)")
        self.gen_fadd(f, D, X1, B, mod)
        self.gen_fmul(f, D, D, D, mod)
        self.gen_fsub(f, D, D, A, mod)
        self.gen_fsub(f, D, D, C, mod)
        self.gen_fadd(f, D, D, D, mod)
        self.Huff.pushln("// E = 3*A")
        self.gen_fadd(f, F, A, A, mod)
        self.gen_fadd(f, F, F, A, mod)
        self.Huff.pushln("// F = E^2")
        self.gen_fmul(f, F, E, E, mod)
        self.Huff.pushln("// X3 = F-2*D")
        self.gen_fadd(f, X3, D, D, mod)
        self.gen_fsub(f, X3, F, D, mod)
        self.Huff.pushln("// Y3 = E*(D-X3)-8*C")
        self.gen_fsub(f, Y3, D, X3, mod)
        self.gen_fmul(f, Y3, E, Y3, mod)
        self.gen_fadd(f, C, C, C, mod)  # clobber C
        self.gen_fadd(f, C, C, C, mod)
        self.gen_fadd(f, C, C, C, mod)
        self.gen_fsub(f, Y3, Y3, C, mod)
        self.Huff.pushln("// Z3 = 2*Y1*Z1")
        self.gen_fmul(f, Z3, Y1, Z1, mod)
        self.gen_fadd(f, Z3, Z3, Z3, mod)
        self.Huff.pushln("// E double")
        self.Huff.pushln("////////////")

    #########
    # Pairing

    def gen_consts(self):
        # f12 one in mont form
        one = "15f65ec3fa80e4935c071a97a256ec6d77ce5853705257455f48985753c758baebf4000bc40c0002760900000002fffd"
        self.Huff.gen_memstore(f12one, bytearray.fromhex(one)[::-1])
        # prime
        p = "1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab"
        self.Huff.gen_memstore(mod, bytes.fromhex(p)[::-1])
        # inv
        inv = "fdfffcfffcfff389000000000000000000000000000000000000000000000000"
        self.Huff.gen_memstore(mod + 48, bytes.fromhex(inv))

    def gen_line_add(self, line, T, R, Q, mod):
        # line is 3 f2s, T on E2, R on E2, Q on E2 affine
        TZ = T + 192
        QX = Q
        QY = QX + 96
        line0 = line
        line1 = line0 + 96
        line2 = line1 + 96
        # ecadd
        I, J, r = self.gen_Eadd__madd_2007_bl("f2", T, R, Q, line1, mod)
        # line eval
        self.F2.gen_f2mul(I, r, QX, mod)
        self.F2.gen_f2mul(J, QY, TZ, mod)
        self.F2.gen_f2sub(I, I, J, mod)
        self.F2.gen_f2add(line0, I, I, mod)
        # gen_memcopy(line1,r,96)	# already done in the
        self.Huff.gen_memcopy(line2, TZ, 96)

    def gen_line_dbl(self, line, T, Q, mod):
        # line is 3 f2s, T is E2 point, Q E2 point	(note: our pairing algorithm, T=Q)
        line0 = line
        line1 = line0 + 96
        line2 = line1 + 96
        QX = Q
        TZ = T + 192
        # double
        A, B, E, F, ZZ, X1 = self.gen_Edouble__dbl_2009_alnr("f2", T, Q, line0, mod)
        # eval line
        # note: line0=E+QX is already done in alnr function
        self.F2.gen_f2sqr(line0, line0, mod)
        self.F2.gen_f2sub(line0, line0, A, mod)
        self.F2.gen_f2sub(line0, line0, F, mod)
        self.F2.gen_f2add(B, B, B, mod)
        self.F2.gen_f2add(B, B, B, mod)
        self.F2.gen_f2sub(line0, line0, B, mod)
        self.F2.gen_f2mul(line1, E, ZZ, mod)
        self.F2.gen_f2mul(line2, TZ, ZZ, mod)

    def gen_line_by_Px2(self, line, Px2, mod):
        # line is 3 f2s, Px2 is E1 point affine
        Px2X = Px2
        Px2Y = Px2X + 48
        line00 = line
        line01 = line00 + 48
        line10 = line01 + 48
        line11 = line10 + 48
        line20 = line11 + 48
        line21 = line20 + 48
        self.F1.gen_f1mul(line10, line10, Px2X, mod)
        self.F1.gen_f1mul(line11, line11, Px2X, mod)
        self.F1.gen_f1mul(line20, line20, Px2Y, mod)
        self.F1.gen_f1mul(line21, line21, Px2Y, mod)

    def gen_start_dbl(self, out, T, Px2, mod):
        # out is f12 point (ie 2 f6 pts), T is E2 point, Px2 is E1 point (affine)
        out00 = out
        out11 = out + 288 + 96  # ??
        line = buffer_line  # 3 f2 points
        line0 = line
        line2 = line0 + 192
        self.gen_line_dbl(line, T, T, mod)
        self.gen_line_by_Px2(line, Px2, mod)
        self.Huff.gen_memcopy(out, zero, 576)
        self.Huff.gen_memcopy(out00, line0, 192)
        self.Huff.gen_memcopy(out11, line2, 96)

    def gen_add_dbl_loop(self, out, T, Q, Px2, mod):
        line = buffer_line  # 3 f2 points
        self.Huff.pushln("0x3f")  # loop iterator, 63 iters
        # self.Huff.pushln("0x0 0x2 0x3 0x9 0x20 0x10") # jumk
        self.Huff.pushln("miller_loop:")
        self.Huff.pushln("0x1 swap1 sub")  # decrement loop iterator and leave it a top of stack
        self.Huff.pushln("0xd201000000010000 dup2 shr")  # get the next bit by shifting by loop iterator
        self.Huff.pushln("0x1 and")  # get next bit by shifting by loop iterator
        self.Huff.pushln("0x1 xor end_if jumpi")  # skip if next bit was 1 (ie skip if flipped bit is 1)
        self.Huff.pushln("begin_if:")  # if 1 bit, then add
        # self.Huff.pushln("0xffffff pop")
        self.gen_line_add(line, T, T, Q, mod)
        self.gen_line_by_Px2(line, Px2, mod)
        self.F12.gen_mul_by_xy00z0_fp12(out, out, line, mod)
        self.Huff.pushln("end_if:")
        # self.Huff.pushln("0xffffffff pop")
        self.F12.gen_f12sqr(out, out, mod)
        self.gen_line_dbl(line, T, T, mod)
        self.gen_line_by_Px2(line, Px2, mod)
        self.F12.gen_mul_by_xy00z0_fp12(out, out, line, mod)
        self.Huff.pushln("dup1 0x1 lt")  # check if 1 < loop iterator	note: don't iterate on least significant bit
        # self.Huff.pushln("dup1 0x62 lt")          # check if 1 < loop iterator	note: don't iterate on least significant bit
        self.Huff.pushln("miller_loop jumpi")  # if loop iterator > 0, then jump to next iter
        self.Huff.pushln("pop")  # pop loop iterator to leave stack how we found it

    def gen_add_dbl_unrolled(self, out, T, Q, Px2, k, mod):
        line = buffer_line  # 3 f2 points
        """
      gen_line_add(line,T,T,Q,mod)
      gen_line_by_Px2(line,Px2,mod)
      gen_mul_by_xy00z0_fp12(out,out,line,mod)
      """
        # loop init   #TODO
        # put k on stack
        # while(k--)
        for i in range(k):
            self.F12.gen_f12sqr(out, out, mod)
            self.gen_line_dbl(line, T, T, mod)
            self.gen_line_by_Px2(line, Px2, mod)
            self.F12.gen_mul_by_xy00z0_fp12(out, out, line, mod)

    def gen_fsqr(self, f, out, x, mod):
        if f == "f12":
            self.F12.gen_f12sqr(out, x, mod)
        if f == "f6":
            self.F6.gen_f6sqr(out, x, mod)
        if f == "f2":
            self.F2.gen_f2sqr(out, x, mod)
        if f == "f1":
            self.F1.gen_f1sqr(out, x, mod)

    def gen_fadd(self, f, out, x, y, mod):
        if f == "f12":
            self.F12.gen_f12add(out, x, y, mod)
        if f == "f6":
            self.F6.gen_f6add(out, x, y, mod)
        if f == "f2":
            self.F2.gen_f2add(out, x, y, mod)
        if f == "f1":
            self.F1.gen_f1add(out, x, y, mod)

    def gen_fsub(self, f, out, x, y, mod):
        if f == "f12":
            self.F12.gen_f12sub(out, x, y, mod)
        if f == "f6":
            self.F6.gen_f6sub(out, x, y, mod)
        if f == "f2":
            self.F2.gen_f2sub(out, x, y, mod)
        if f == "f1":
            self.F1.gen_f1sub(out, x, y, mod)

    def gen_fmul(self, f, out, x, y, mod):
        if f == "f12":
            self.F12.gen_f12mul(out, x, y, mod)
        if f == "f6":
            self.F6.gen_f6mul(out, x, y, mod)
        if f == "f2":
            self.F2.gen_f2mul(out, x, y, mod)
        if f == "f1":
            self.F1.gen_f1mul(out, x, y, mod)