class Huff:
  def __init__(self):
    self.lines = []
    self.addmod384_count=0
    self.submod384_count=0
    self.mulmodmont384_count=0
    self.f2add_count=0
    self.f2sub_count=0
    self.f2mul_count=0
    self.f6add_count=0
    self.f6sub_count=0
    self.f6mul_count=0
    self.f12add_count=0
    self.f12sub_count=0
    self.f12mul_count=0
    buffer_offset = 0
    self.zero = buffer_offset
    self.f1zero = buffer_offset	# 48 bytes
    self.f2zero = buffer_offset	# 96 bytes
    self.f6zero = buffer_offset	# 288 bytes
    self.f12zero = buffer_offset	# 576 bytes
    buffer_offset += 576
    self.f12one = buffer_offset	# 576 bytes
    buffer_offset += 576
    self.mod = buffer_offset	# 56 bytes, mod||inv
    buffer_offset += 56
    self.buffer_miller_loop = buffer_offset	# 1 E2 point, 1 E1 point affine
    buffer_offset += 288+96
    self.buffer_line = buffer_offset		# 3 f2 points
    buffer_offset += 288
    self.buffer_f2mul = buffer_offset	# 3 f1 points
    buffer_offset += 144
    self.buffer_f6mul = buffer_offset	# 6 f2 points
    buffer_offset += 576
    self.buffer_f12mul = buffer_offset	# 3 f6 points
    buffer_offset += 864
    self.buffer_Eadd = buffer_offset	# 14 or 9 values
    buffer_offset += 14*3*96
    self.buffer_Edouble = buffer_offset	# 7 or 6 values
    buffer_offset += 7*3*96
    self.buffer_inputs = buffer_offset
    buffer_offset += 2*48+2*96
    self.buffer_output = buffer_offset
    buffer_offset += 12*48
    self.buffer_offset = buffer_offset
  
  def gen_memstore(self, dst_offset, bytes_):
    """
      takes in a bytestring greater than 32 bytes and
      stores them in memory using mstore
    """
    if len(bytes_)<32:
      print("ERROR gen_copy() fewer than 32 bytes needs special handling, len_ is only ", len(bytes_))
      return
    idx = 0
    while idx<len(bytes_)-32:
      # e.g. 0xfdfffcfffcfff389000000000000000000000000000000000000000000000000 0x4b0 mstore
      line = "0x" + str(bytes_[idx:idx+32]).encode("hex") + ' '
      line += hex(dst_offset) + ' '
      line += "mstore"
      self.lines.append(line)
      # step
      dst_offset+=32
      idx+=32
    line = "0x"+ str(bytes_[-32:]).encode("hex") + ' '
    line += hex(dst_offset+len(bytes_[idx:])-32) + ' '
    line += "mstore"
    self.lines.append(line)

  def gen_memcopy(self, dst_offset, src_offset,len_):
    """
      copies the object into memory
    """
    if len_<32:
      print("ERROR gen_memcopy() len_ is ",len_)
      return
    while len_>32:
      len_-=32
      self.lines.append(hex(src_offset))
      self.lines.append("mload")
      self.lines.append(hex(dst_offset))
      self.lines.append("mstore")
      src_offset+=32
      dst_offset+=32
    self.lines.append(hex(src_offset-(32-len_)))
    self.lines.append("mload")
    self.lines.append(hex(dst_offset-(32-len_)))
    self.lines.append("mstore")

  def gen_evm384_offsets(self,a,b,c,d):
    line = "0x"
    line += hex(a)[2:].zfill(8)
    line += hex(b)[2:].zfill(8)
    line += hex(c)[2:].zfill(8)
    line += hex(d)[2:].zfill(8)
    line += ' '
    self.lines.append(line)

  def gen_mul_by_u_plus_1_fp2(self,out,x,mod):
    t = self.buffer_f2mul	# to prevent clobbering
    self.gen_f1sub(t, x, x+48, mod)
    self.gen_f1add(out+48, x, x+48, mod)
    self.gen_memcopy(out,t,48)
    
  def gen_fadd(self,f,out,x,y,mod):
    if f=="f12":
      self.gen_f12add(out,x,y,mod)
    if f=="f6":
      self.gen_f6add(out,x,y,mod)
    if f=="f2":
      self.gen_f2add(out,x,y,mod)
    if f=="f1":
      self.gen_f1add(out,x,y,mod)

  def gen_fsub(self,f,out,x,y,mod):
    if f=="f12":
      self.gen_f12sub(out,x,y,mod)
    if f=="f6":
      self.gen_f6sub(out,x,y,mod)
    if f=="f2":
      self.gen_f2sub(out,x,y,mod)
    if f=="f1":
      self.gen_f1sub(out,x,y,mod)

  def gen_fmul(self,f,out,x,y,mod):
    if f=="f12":
      self.gen_f12mul(out,x,y,mod)
    if f=="f6":
      self.gen_f6mul(out,x,y,mod)
    if f=="f2":
      self.gen_f2mul(out,x,y,mod)
    if f=="f1":
      self.gen_f1mul(out,x,y,mod)

  def gen_fsqr(self,f,out,x,mod):
    if f=="f12":
      self.gen_f12sqr(out,x,mod)
    if f=="f6":
      self.gen_f6sqr(out,x,mod)
    if f=="f2":
      self.gen_f2sqr(out,x,mod)
    if f=="f1":
      self.gen_f1sqr(out,x,mod)   

class F1():
  def __init__(self, out, value, mod, huff):
    self.huff = huff
    self.out = out
    self.value = value
    self.mod = mod

  def __add__(self, other):
    # TODO: handle if case if false
    if isinstance(other, self.__class__):
      x = self.value
      y = other.value
      out = self.out
      mod = self.mod
      self.huff.gen_evm384_offsets(out,x,y,mod)

      # debugging
      print("addmod384")
      self.huff.addmod384_count+=1

  def __sub__(self,other):
    if isinstance(other, self.__class__):
      x = self.value
      y = other.value
      out = self.out
      mod = self.mod
      self.huff.gen_evm384_offsets(out,x,y,mod)

      # debugging
      print("submod384")
      self.huff.submod384_count+=1
    
  def __mul__(self,other):
    if isinstance(other, self.__class__):
      x = self.value
      y = other.value
      out = self.out
      mod = self.mod
      self.huff.gen_evm384_offsets(out,x,y,mod)

      # debugging
      print("mulmod384")
      self.huff.submod384_count+=1
    
  def __neg__(self):
    y = self.value
    out = self.out
    mod = self.mod
    self.huff.gen_evm384_offsets(out,0,y,mod)

    # debugging
    print("submod384")
    self.huff.submod384_count+=1

class F2():
  def __init__(self, out, value, mod, huff):
    self.huff = huff
    self.out = out
    self.mod = mod
    self.x = x
    self.y = y

  def __add__(self,out,x,y,mod):
    if isinstance(other, self.__class__):
      self.huff.f2add_count+=1
      print("// f2 add")
      x0 = self.x
      x1 = x+48
      y0 = self.y
      y1 = y+48
      out0 = out
      out1 = out+48

      x0 = F1(out0, x0, mod, self.huff)
      x1 = F1(out1, x1, mod, self.huff)
      y0 = F1(out0, y0, mod, self.huff)
      y1 = F1(out1, y1, mod, self.huff)
      x0 + y0
      x1 + y1

  def gen_f2sub(self,out,x,y,mod):
    self.f2sub_count+=1
    print("// f2 sub")
    x0 = x
    x1 = x+48
    y0 = y
    y1 = y+48
    out0 = out
    out1 = out+48
    self.gen_f1sub(out0,x0,y0,mod)
    self.gen_f1sub(out1,x1,y1,mod)

  def gen_f2mul(self,out,x,y,mod):
    self.f2mul_count+=1
    print("// f2 mul")
    # get offsets
    x0 = x
    x1 = x+48
    y0 = y
    y1 = y+48
    out0 = out
    out1 = out+48
    # temporary values
    tmp1 = self.buffer_f2mul
    tmp2 = tmp1+48
    tmp3 = tmp2+48
    """
    tmp1 = x0*y0
    tmp2 = x1*y1
    tmp3 = zero-tmp2
    out0 = tmp1+tmp3
    tmp1 = tmp1+tmp2
    tmp2 = x0+x1
    tmp3 = y0+y1
    tmp2 = tmp2*tmp3
    out1 = tmp2-tmp1
    """
    if 0:
      self.gen_f1mul(tmp1,x0,y0,mod)
      self.gen_f1mul(tmp2,x1,y1,mod)
      self.gen_f1sub(out0,tmp1,tmp2,mod)		# above sub,add give same result as just this sub
      self.gen_f1mul(tmp1,x0,y1,mod)
      self.gen_f1mul(tmp2,x1,y0,mod)
      self.gen_f1add(out1,tmp1,tmp2,mod)
    elif 1:
      self.gen_f1mul(tmp1,x0,y0,mod)
      self.gen_f1mul(tmp2,x1,y1,mod)
      self.gen_f1sub(out0,tmp1,tmp2,mod)		# above sub,add give same result as just this sub
      self.gen_f1add(tmp1,tmp1,tmp2,mod)
      self.gen_f1add(tmp2,x0,x1,mod)
      self.gen_f1add(tmp3,y0,y1,mod)
      self.gen_f1mul(tmp2,tmp2,tmp3,mod)
      self.gen_f1sub(out1,tmp2,tmp1,mod)
    elif 0:
      self.gen_f1mul(tmp1,x0,y0,mod)			# t1 = x0*y0
      self.gen_f1sub(tmp2,self.zero,x1,mod)			# t2 = -x1
      self.gen_f1mul(tmp2,tmp2,y1,mod)			# t2 = -x1*y1
      self.gen_f1add(out0,tmp1,tmp2,mod)		# out0 = t1+t2
      self.gen_f1add(tmp3,x0,x1,mod)			# t3 = x0+y0
      self.gen_f1add(out1,y0,y1,mod)			# out1 = x1+y1
      self.gen_f1mul(out1,out1,tmp3,mod)		# out1 = out1*t3
      self.gen_f1sub(out1,out1,tmp1,mod)		# out1 = out1-t1
      self.gen_f1add(out1,out1,tmp2,mod)		# out1 = out1+t2
    elif 0:
      self.gen_f1mul(tmp1,x0,y0,mod)                   # t1 = x0*y0
      self.gen_f1mul(tmp2,x1,y1,mod)                 # t2 = x1*y1
      self.gen_f1sub(out0,tmp1,tmp2,mod)               # out0 = t1-t2
      self.gen_f1add(tmp3,x0,x1,mod)                   # t3 = x0+y0
      self.gen_f1add(out1,y0,y1,mod)                   # out1 = x1+y1
      self.gen_f1mul(out1,out1,tmp3,mod)               # out1 = out1*t3
      self.gen_f1sub(out1,out1,tmp1,mod)               # out1 = out1-t1
      self.gen_f1sub(out1,out1,tmp2,mod)               # out1 = out1-t2

  def gen_f2sqr(self,out,x,mod):
    self.f2mul_count+=1
    print("// f2sqr")
    if 0:
      self.gen_f2mul(out,x,x,mod)
    else:
      # get offsets
      x0 = x
      x1 = x+48
      out0 = out
      out1 = out+48
      tmp0 = self.buffer_f2mul
      tmp1 = tmp0+48
      self.gen_f1add(tmp0,x0,x1,mod)
      self.gen_f1sub(tmp1,x0,x1,mod)
      self.gen_f1mul(out1,x0,x1,mod)
      self.gen_f1add(out1,out1,out1,mod)
      self.gen_f1mul(out0,tmp0,tmp1,mod)
    
  def gen_f2neg(self,out,in_,mod):
    #gen_f2sub(out,zero,in_,mod)
    self.gen_f1sub(out,mod,in_,mod)
    self.gen_f1sub(out+48,mod,in_+48,mod)

class F6():
  def __init__(self, huff):
    self.huff = huff

  def gen_f6add(self,out,x,y,mod):
    self.f6add_count+=1
    print("// f6 add")
    x0 = x
    x1 = x0+96
    x2 = x1+96
    y0 = y
    y1 = y0+96
    y2 = y1+96
    out0 = out
    out1 = out0+96
    out2 = out1+96
    self.gen_f2add(out0,x0,y0,mod)
    self.gen_f2add(out1,x1,y1,mod)
    self.gen_f2add(out2,x2,y2,mod)

  def gen_f6sub(self,out,x,y,mod):
    self.f6sub_count+=1
    print("// f6 sub")
    x0 = x
    x1 = x0+96
    x2 = x1+96
    y0 = y
    y1 = y0+96
    y2 = y1+96
    out0 = out
    out1 = out0+96
    out2 = out1+96
    self.gen_f2sub(out0,x0,y0,mod)
    self.gen_f2sub(out1,x1,y1,mod)
    self.gen_f2sub(out2,x2,y2,mod)

  def gen_f6neg(self,out,x,mod):
    x0=x
    x1=x0+96
    x2=x1+96
    out0=out
    out1=out0+96
    out2=out1+96
    self.gen_f2neg(out0,x0,mod)
    self.gen_f2neg(out1,x1,mod)
    self.gen_f2neg(out2,x2,mod)

  def gen_f6mul(self,out,x,y,mod):
    self.f6mul_count+=1
    print("// f6 add")
    x0 = x
    x1 = x0+96
    x2 = x1+96
    y0 = y
    y1 = y0+96
    y2 = y1+96
    out0 = out
    out1 = out0+96
    out2 = out1+96
    # temporary variables
    t0 = self.buffer_f6mul
    t1 = t0+96
    t2 = t1+96
    t3 = t2+96
    t4 = t3+96
    t5 = t4+96
    # algorithm
    self.gen_f2mul(t0,x0,y0,mod)
    self.gen_f2mul(t1,x1,y1,mod)
    self.gen_f2mul(t2,x2,y2,mod)
    # out0
    self.gen_f2add(t4,x1,x2,mod)
    self.gen_f2add(t5,y1,y2,mod)
    self.gen_f2mul(t3,t4,t5,mod)
    self.gen_f2sub(t3,t3,t1,mod)
    self.gen_f2sub(t3,t3,t2,mod)
    self.gen_mul_by_u_plus_1_fp2(t3,t3,mod)
    #gen_f2add(out0,t3,t0,mod)	# below
    # out1
    self.gen_f2add(t4,x0,x1,mod)
    self.gen_f2add(t5,y0,y1,mod)
    self.gen_f2mul(out1,t4,t5,mod)
    self.gen_f2sub(out1,out1,t0,mod)
    self.gen_f2sub(out1,out1,t1,mod)
    self.gen_mul_by_u_plus_1_fp2(t4,t2,mod)
    self.gen_f2add(out1,out1,t4,mod)
    # out2
    self.gen_f2add(t4,x0,x2,mod)
    self.gen_f2add(t5,y0,y2,mod)
    self.gen_f2mul(out2,t4,t5,mod)
    self.gen_f2sub(out2,out2,t0,mod)
    self.gen_f2sub(out2,out2,t2,mod)
    self.gen_f2add(out2,out2,t1,mod)

    self.gen_f2add(out0,t3,t0,mod)

  def gen_f6sqr(self,out,x,mod):
    self.gen_f6mul(out,x,x,mod)	# TODO: optimize

class F12():
  def __init__(self, huff):
    self.huff = huff

  def gen_f12add(self,out,x,y,mod):
    self.f12add_count+=1
    print("// f6 add")
    x0 = x
    x1 = x0+288
    y0 = y
    y1 = y0+288
    out0 = out
    out1 = out0+288
    self.gen_f6add(out0,x0,y0,mod)
    self.gen_f6add(out1,x1,y1,mod)
  
  def gen_f12sub(self,out,x,y,mod):
    self.f12sub_count+=1
    print("// f6 add")
    x0 = x
    x1 = x0+288
    y0 = y
    y1 = y0+288
    out0 = out
    out1 = out0+288
    self.gen_f6sub(out0,x0,y0,mod)
    self.gen_f6sub(out1,x1,y1,mod)

  def gen_f12mul(self,out,x,y,mod):
    self.f12mul_count+=1
    print("// f12 mul")
    x0 = x
    x1 = x0+288
    y0 = y
    y1 = y0+288
    out0 = out
    out00 = out0
    out01 = out00+96
    out02 = out01+96
    out1 = out0+288
    # temporary variables
    t0 = self.buffer_f12mul
    t00 = t0
    t01 = t00+96
    t02 = t01+96
    t1 = t0+288
    t10 = t1
    t11 = t10+96
    t12 = t11+96
    t2 = t1+288
    # debugging
    self.gen_f6mul(out0,x0,y0,mod)
    self.gen_f6mul(out1,x1,y1,mod)
    self.gen_f6mul(t0,x0,y0,mod)
    self.gen_f6mul(t1,x1,y1,mod)
    # out1
    self.gen_f6add(t2,x0,x1,mod)
    self.gen_f6add(out1,y0,y1,mod)
    self.gen_f6mul(out1,out1,t2,mod)
    self.gen_f6sub(out1,out1,t0,mod)
    self.gen_f6sub(out1,out1,t1,mod)
    # out0
    self.gen_mul_by_u_plus_1_fp2(t12,t12,mod)
    self.gen_f2add(out00,t00,t12,mod)
    self.gen_f2add(out01,t01,t10,mod)
    self.gen_f2add(out02,t02,t11,mod)

  def gen_f12sqr(self,out,x,mod):
    print("// f12 sqr")
    x0 = x
    x00 = x0
    x01 = x00+96
    x02 = x01+96
    x1 = x0+288
    x10 = x1
    x11 = x10+96
    x12 = x11+96
    out0 = out
    out00 = out0
    out01 = out00+96
    out02 = out01+96
    out1 = out0+288
    # temporary variables
    t0 = self.buffer_f12mul
    t00 = t0
    t01 = t00+96
    t02 = t01+96
    t1 = t0+288
    t10 = t1
    t11 = t10+96
    t12 = t11+96

    self.gen_f6add(t0,x0,x1,mod)

    self.gen_mul_by_u_plus_1_fp2(t12,x12,mod)
    self.gen_f2add(t10,x00,t12,mod)
    self.gen_f2add(t11,x01,x10,mod)
    self.gen_f2add(t12,x02,x11,mod)
    
    self.gen_f6mul(t0,t0,t1,mod)
    self.gen_f6mul(t1,x0,x1,mod)

    self.gen_f6add(out1,t1,t1,mod)
    self.gen_f6sub(out0,t0,t1,mod)
  
    self.gen_mul_by_u_plus_1_fp2(t12,t12,mod)
    self.gen_f2sub(out00,out00,t12,mod)
    self.gen_f2sub(out01,out01,t10,mod)
    self.gen_f2sub(out02,out02,t11,mod)

  def gen_f12_conjugate(self,x,mod):
    x1 = x+288
    self.gen_f6neg(x1,x1,mod)