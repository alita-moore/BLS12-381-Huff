from src.MillerLoop.Constants import buffer_miller_loop, buffer_output, buffer_inputs, mod, f12one
from src.MillerLoop.CurveOperations import CurveOperations
from src.MillerLoop.F1 import F1
from src.MillerLoop.F12 import F12
from src.MillerLoop.Huff import Huff


class MillerLoop:
    def __init__(self, huff: Huff, curve_operations: CurveOperations, f1: F1, f12: F12):
        self.Huff = huff
        self.CurveOperations = curve_operations
        self.F1 = f1
        self.F12 = f12
        
    def gen_miller_loop(self, out, P, Q, mod):
        # P is E1 point (affine), Q is E2 point (affine)
        PX = P
        PY = PX + 48
        QX = Q
        # temp offsets
        T = buffer_miller_loop  # E2 point
        TX = T
        TY = TX + 96
        TZ = TY + 96
        Px2 = T + 288  # E1 point (affine)
        Px2X = Px2
        Px2Y = Px2 + 48
        # huff module
        self.Huff.pushln("#define macro MILLER_LOOP = takes(0) returns(0) {")
        self.CurveOperations.gen_consts()  # TODO: put this somewhere else
        # prepare some stuff
        self.F1.gen_f1add(Px2X, PX, PX, mod)
        self.F1.gen_f1neg(Px2X, Px2X, mod)
        self.F1.gen_f1add(Px2Y, PY, PY, mod)
        self.Huff.gen_memcopy(TX, QX, 192)
        self.Huff.gen_memcopy(TZ, f12one, 96)
        # execute
        self.CurveOperations.gen_start_dbl(out, T, Px2, mod)
        self.CurveOperations.gen_add_dbl_loop(out, T, Q, Px2, mod)
    
        """
      gen_add_dbl(out,T,Q,Px2,1,mod)
      gen_add_dbl(out,T,Q,Px2,1,mod)
      gen_add_dbl(out,T,Q,Px2,1,mod)
      gen_add_dbl(out,T,Q,Px2,1,mod)
      gen_add_dbl(out,T,Q,Px2,1,mod)
      """
        """
    
      gen_add_dbl(out,T,Q,Px2,2,mod)
      gen_add_dbl(out,T,Q,Px2,3,mod)
      gen_add_dbl(out,T,Q,Px2,9,mod)
      gen_add_dbl(out,T,Q,Px2,32,mod)
      gen_add_dbl(out,T,Q,Px2,16,mod)
      """
        self.F12.gen_f12_conjugate(out, mod)
        self.Huff.pushln("} // MILLER_LOOP")

    def gen_final_exponentiation(self, out, in_):
        pass

    def gen_pairing(self):
        # input
        self.gen_miller_loop(buffer_output, buffer_inputs, buffer_inputs + 96, mod)
        # gen_final_exponentiation(buffer_output,buffer_output)

    def gen_miller_loop_unrolled(self, out, P, Q, mod):
        # P is E1 point (affine), Q is E2 point (affine)
        PX = P
        PY = PX + 48
        QX = Q
        # temp offsets
        T = buffer_miller_loop  # E2 point
        TX = T
        TY = TX + 96
        TZ = TY + 96
        Px2 = T + 288  # E1 point (affine)
        Px2X = Px2
        Px2Y = Px2 + 48
        # huff module
        self.Huff.pushln("#define macro MILLER_LOOP = takes(0) returns(0) {")
        self.CurveOperations.gen_consts()  # TODO: put this somewhere else
        # prepare some stuff
        self.F1.gen_f1add(Px2X, PX, PX, mod)
        self.F1.gen_f1neg(Px2X, Px2X, mod)
        self.F1.gen_f1add(Px2Y, PY, PY, mod)
        self.Huff.gen_memcopy(TX, QX, 192)
        self.Huff.gen_memcopy(TZ, f12one, 96)
        # execute
        self.CurveOperations.gen_start_dbl(out, T, Px2, mod)
        self.CurveOperations.gen_add_dbl_unrolled(out, T, Q, Px2, 2, mod)
        self.CurveOperations.gen_add_dbl_unrolled(out, T, Q, Px2, 3, mod)
        self.CurveOperations.gen_add_dbl_unrolled(out, T, Q, Px2, 9, mod)
        self.CurveOperations.gen_add_dbl_unrolled(out, T, Q, Px2, 32, mod)
        self.CurveOperations.gen_add_dbl_unrolled(out, T, Q, Px2, 16, mod)
    
        self.F12.gen_f12_conjugate(out, mod)
        self.Huff.pushln("} // MILLER_LOOP")

    def gen_pairing_unrolled(self):
        # input
        self.gen_miller_loop_unrolled(buffer_output, buffer_inputs, buffer_inputs + 96, mod)
        # gen_final_exponentiation(buffer_output,buffer_output)
        self.Huff.pushln(self.F1.addmod384_count)
        self.Huff.pushln(self.F1.submod384_count)
        self.Huff.pushln(self.F1.mulmodmont384_count)
