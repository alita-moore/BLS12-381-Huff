
"""
notes
 - jacobian
   to jacobian just puts extra coordinate z=1
   to recover affine from jacobian, need reciprocal_fp which is a square and mul loop (like double and add) over exponent bits (which is hard-coded, related to field prime). fp2 uses one of these too.
 - montgomery form
   - I think that you can just use, but must reduce twice to recover
   - reduce by doing mulmodmont with other input=1

"""

class Huff:
  def __init__(self):
    self.lines = []
  def _clear_(self):
    self.lines = []
  def gen_memstore(self, dst_offset, bytes_):
    """
      takes in a bytestring greater than 32 bytes and
      stores them in memory using mstore
    """
    if len(bytes_)<32:
      print("ERROR gen_copy() fewer than 32 bytes needs special handling, len_ is only ",len_)
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

  def _memcopy(self, dst_offset, src_offset,len_):
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
  
  def gen_isNonzero(offset,len_):
    # leaves stack item 0 if zero or >0 if nonzero
    # len_ must be >=33 bytes
    if len_<32:
      print("ERROR gen_isZero() len_ is ",len_)
      return
    self.lines.append(hex(offset))
    self.lines.append("mload")
    self.lines.append("iszero 0x1 sub")
    buffer_+=32
    len_-=32
    while len_>32:
      self.lines.append(hex(offset))
      self.lines.append("mload")
      self.lines.append("iszero 0x1 sub")
      self.lines.append("add")
      buffer_+=32
      len_-=32
    # final check
    if len_>0:
      self.lines.append(hex(buffer_-(32-len_)))
      self.lines.append("mload")
      self.lines.append("iszero 0x1 sub")
      self.lines.append("add")
  
#######
# utils

# def gen_memstore(dst_offset,bytes_):
#   idx = 0
#   if len(bytes_)<32:
#     print("ERROR gen_copy() fewer than 32 bytes needs special handling, len_ is only ",len_)
#     return
#   while idx<len(bytes_)-32:
#     print("0x"+bytes_[idx:idx+32].hex(),end=' ')
#     print(hex(dst_offset),end=' ')
#     print("mstore")
#     dst_offset+=32
#     idx+=32
#   print("0x"+bytes_[-32:].hex(),end=' ')
#   print(hex(dst_offset+len(bytes_[idx:])-32),end=' ')
#   print("mstore")

# def gen_memcopy(dst_offset,src_offset,len_):
#   if len_<32:
#     print("ERROR gen_memcopy() len_ is ",len_)
#     return
#   while len_>32:
#     len_-=32
#     print(hex(src_offset))
#     print("mload")
#     print(hex(dst_offset))
#     print("mstore")
#     src_offset+=32
#     dst_offset+=32
#   print(hex(src_offset-(32-len_)))
#   print("mload")
#   print(hex(dst_offset-(32-len_)))
#   print("mstore")

# def gen_isNonzero(offset,len_):
#   # leaves stack item 0 if zero or >0 if nonzero
#   # len_ must be >=33 bytes
#   if len_<32:
#     print("ERROR gen_isZero() len_ is ",len_)
#     return
#   print(hex(offset))
#   print("mload")
#   print("iszero 0x1 sub")
#   buffer_+=32
#   len_-=32
#   while len_>32:
#     print(hex(offset))
#     print("mload")
#     print("iszero 0x1 sub")
#     print("add")
#     buffer_+=32
#     len_-=32
#   # final check
#   if len_>0:
#     print(hex(buffer_-(32-len_)))
#     print("mload")
#     print("iszero 0x1 sub")
#     print("add")



###########
# Constants

bls12_384_prime = 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab

# offsets for zero, input/output, and local buffers
buffer_offset = 0
zero = buffer_offset
f1zero = buffer_offset	# 48 bytes
f2zero = buffer_offset	# 96 bytes
f6zero = buffer_offset	# 288 bytes
f12zero = buffer_offset	# 576 bytes
buffer_offset += 576
f12one = buffer_offset	# 576 bytes
buffer_offset += 576
mod = buffer_offset	# 56 bytes, mod||inv
buffer_offset += 56
buffer_miller_loop = buffer_offset	# 1 E2 point, 1 E1 point affine
buffer_offset += 288+96
buffer_line = buffer_offset		# 3 f2 points
buffer_offset += 288
buffer_f2mul = buffer_offset	# 3 f1 points
buffer_offset += 144
buffer_f6mul = buffer_offset	# 6 f2 points
buffer_offset += 576
buffer_f12mul = buffer_offset	# 3 f6 points
buffer_offset += 864
buffer_Eadd = buffer_offset	# 14 or 9 values
buffer_offset += 14*3*96
buffer_Edouble = buffer_offset	# 7 or 6 values
buffer_offset += 7*3*96
buffer_inputs = buffer_offset
buffer_offset += 2*48+2*96
buffer_output = buffer_offset
buffer_offset += 12*48



def gen_test_case_values():
  if 0:
    # test from https://tools.ietf.org/id/draft-yonezawa-pairing-friendly-curves-02.html#rfc.appendix.B
    # Input x,y values:
    inE1  = bytearray.fromhex("120177419e0bfb75edce6ecc21dbf440f0ae6acdf3d0e747154f95c7143ba1c17817fc679976fff55cb38790fd530c16")[::-1]
    inE1  += bytearray.fromhex("0e44d2ede97744303cff1b76964b531712caf35ba344c12a89d7738d9fa9d05592899ce4383b0270ff526c2af318883a")[::-1]
    gen_memstore(buffer_inputs,inE1)
    # Input x’0,x'1 value:
    inE2 = bytearray.fromhex("058191924350bcd76f67b7631863366b9894999d1a3caee9a1a893b53e2ae580b3f5fb2687b4961af5f28fa202940a10")[::-1] 
    inE2 += bytearray.fromhex("11922a097360edf3c2b6ed0ef21585471b1ab6cc8541b3673bb17e18e2867806aaa0c59dbccd60c3a5a9c0759e23f606")[::-1] 
    # Input y’0,y'1 value:
    inE2 += bytearray.fromhex("197d145bbaff0bb54347fe40525c8734a887959b8577c95f7f4a4d344ca692c9c52f05df531d63a56d8bf5079fb65e61")[::-1] 
    inE2 += bytearray.fromhex("0ed54f48d5a1caa764044f659f0ee1e9eb2def362a476f84e0832636bacc0a840601d8f4863f9e230c3e036d209afa4e")[::-1] 
    gen_memstore(buffer_inputs+96,inE2)
  if 0:
    print()
    # these are the identity elements, copied from https://github.com/ethereum/EIPs/blob/master/EIPS/eip-2539.md#specification
    # G1:
    inE1  = bytearray.fromhex("008848defe740a67c8fc6225bf87ff5485951e2caa9d41bb188282c8bd37cb5cd5481512ffcd394eeab9b16eb21be9ef")[::-1]
    inE1  += bytearray.fromhex("01914a69c5102eff1f674f5d30afeec4bd7fb348ca3e52d96d182ad44fb82305c2fe3d3634a9591afd82de55559c8ea6")[::-1]
    gen_memstore(buffer_inputs,inE1)
    # G2:
    inE2 = bytearray.fromhex("018480be71c785fec89630a2a3841d01c565f071203e50317ea501f557db6b9b71889f52bb53540274e3e48f7c005196")[::-1] 
    inE2 += bytearray.fromhex("00ea6040e700403170dc5a51b1b140d5532777ee6651cecbe7223ece0799c9de5cf89984bff76fe6b26bfefa6ea16afe")[::-1] 
    inE2 += bytearray.fromhex("00690d665d446f7bd960736bcbb2efb4de03ed7274b49a58e458c282f832d204f2cf88886d8c7c2ef094094409fd4ddf")[::-1] 
    inE2 += bytearray.fromhex("00f8169fd28355189e549da3151a70aa61ef11ac3d591bf12463b01acee304c24279b83f5e52270bd9a1cdd185eb8f93")[::-1] 
    gen_memstore(buffer_inputs+96,inE2)
  if 0:
    print()
    # these are from wasmsnark
    # cd wasmsnark && ~/repos/node/node-v12.18.4-linux-x64/bin/npx mocha test/bls12381.js
    # G1:
    inE1  = bytearray.fromhex("0f81da25ecf1c84b577fefbedd61077a81dc43b00304015b2b596ab67f00e41c86bb00ebd0f90d4b125eb0539891aeed")[::-1]
    inE1  += bytearray.fromhex("11af629591ec86916d6ce37877b743fe209a3af61147996c1df7fd1c47b03181cd806fd31c3071b739e4deb234bd9e19")[::-1]
    gen_memstore(buffer_inputs,inE1)
    # G2:
    inE2 = bytearray.fromhex("024aa2b2f08f0a91260805272dc51051c6e47ad4fa403b02b4510b647ae3d1770bac0326a805bbefd48056c8c121bdb8")[::-1] 
    inE2 += bytearray.fromhex("13e02b6052719f607dacd3a088274f65596bd0d09920b61ab5da61bbdc7f5049334cf11213945d57e5ac7d055d042b7e")[::-1] 
    inE2 += bytearray.fromhex("0ce5d527727d6e118cc9cdc6da2e351aadfd9baa8cbdd3a76d429a695160d12c923ac9cc3baca289e193548608b82801")[::-1] 
    inE2 += bytearray.fromhex("0606c4a02ea734cc32acd2b02bc28b99cb3e287e85a763af267492ab572e99ab3f370d275cec1da1aaa9075ff05f79be")[::-1] 
    gen_memstore(buffer_inputs+96,inE2)
  if 0:
    # from https://datatracker.ietf.org/doc/draft-irtf-cfrg-pairing-friendly-curves/?include_text=1 appendix B
    inE1  = bytearray.fromhex("17f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb")[::-1]
    inE1  += bytearray.fromhex("08b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1")[::-1]
    gen_memstore(buffer_inputs,inE1)
    inE2  = bytearray.fromhex("024aa2b2f08f0a91260805272dc51051c6e47ad4fa403b02b4510b647ae3d1770bac0326a805bbefd48056c8c121bdb8")[::-1]
    inE2  += bytearray.fromhex("13e02b6052719f607dacd3a088274f65596bd0d09920b61ab5da61bbdc7f5049334cf11213945d57e5ac7d055d042b7e")[::-1]
    inE2  += bytearray.fromhex("0ce5d527727d6e118cc9cdc6da2e351aadfd9baa8cbdd3a76d429a695160d12c923ac9cc3baca289e193548608b82801")[::-1]
    inE2  += bytearray.fromhex("0606c4a02ea734cc32acd2b02bc28b99cb3e287e85a763af267492ab572e99ab3f370d275cec1da1aaa9075ff05f79be")[::-1]
    gen_memstore(buffer_inputs+96,inE2)
  if 1:
    # from casey
    inE1  = bytearray.fromhex("0b83dfefb120fab7665a607d749ef1765fbb3cc0ba5827a20a135402c09d987c701ddb5b60f0f5495026817e8ab6ea2e")[::-1]
    inE1  += bytearray.fromhex("15c82e5362493d173e96edb436e396a30b9d3ae5d1a2633c375cfbbf3aed34bbc30448ec6b8102ab2f8da4486d23a717")[::-1]
    gen_memstore(buffer_inputs,inE1)
    inE2  = bytearray.fromhex("16fc2f7ff7eb01f34e97a5d5274390ee168f32ff5803597da434b40fa7778793eaac8cc3e8f0d75f3bf55889258ebea7")[::-1]
    inE2  += bytearray.fromhex("183aa5f5b84721a4efdfc5a759ec88792e3080b8f9207d02eca66082d6076569b84b95e05b3a4b95697909f1dda69d8d")[::-1]
    inE2  += bytearray.fromhex("002e5c809b03e98d5406ae13e3aa6e477b4aa0a0cedef70dafdd5f0b0c2c64152f52837f92870d0c57b21dd62e9ead91")[::-1]
    inE2  += bytearray.fromhex("039dc3bb023f737d7c60f62b4e669843817fe1ed0751a7b750d02c9df5ee87758e7fe7d6fd614b5fe013f35e6fd9ae4d")[::-1]
    gen_memstore(buffer_inputs+96,inE2)


      
      
      
      


# for counting number of operations
addmod384_count=0
submod384_count=0
mulmodmont384_count=0
f2add_count=0
f2sub_count=0
f2mul_count=0
f6add_count=0
f6sub_count=0
f6mul_count=0
f12add_count=0
f12sub_count=0
f12mul_count=0


# pack offsets into stack item
def gen_evm384_offsets(a,b,c,d):
  print("0x"+hex(a)[2:].zfill(8)+hex(b)[2:].zfill(8)+hex(c)[2:].zfill(8)+hex(d)[2:].zfill(8), end=' ')



#################################
## Field operations add, sub, mul

# general ops when field can change

def gen_fadd(f,out,x,y,mod):
  if f=="f12":
    gen_f12add(out,x,y,mod)
  if f=="f6":
    gen_f6add(out,x,y,mod)
  if f=="f2":
    gen_f2add(out,x,y,mod)
  if f=="f1":
    gen_f1add(out,x,y,mod)

def gen_fsub(f,out,x,y,mod):
  if f=="f12":
    gen_f12sub(out,x,y,mod)
  if f=="f6":
    gen_f6sub(out,x,y,mod)
  if f=="f2":
    gen_f2sub(out,x,y,mod)
  if f=="f1":
    gen_f1sub(out,x,y,mod)

def gen_fmul(f,out,x,y,mod):
  if f=="f12":
    gen_f12mul(out,x,y,mod)
  if f=="f6":
    gen_f6mul(out,x,y,mod)
  if f=="f2":
    gen_f2mul(out,x,y,mod)
  if f=="f1":
    gen_f1mul(out,x,y,mod)

def gen_fsqr(f,out,x,mod):
  if f=="f12":
    gen_f12sqr(out,x,mod)
  if f=="f6":
    gen_f6sqr(out,x,mod)
  if f=="f2":
    gen_f2sqr(out,x,mod)
  if f=="f1":
    gen_f1sqr(out,x,mod)

# f1

def gen_f1add(out,x,y,mod):
  global addmod384_count
  gen_evm384_offsets(out,x,y,mod); print("addmod384"); addmod384_count+=1

def gen_f1sub(out,x,y,mod):
  global submod384_count
  gen_evm384_offsets(out,x,y,mod); print("submod384"); submod384_count+=1

def gen_f1mul(out,x,y,mod):
  global mulmodmont384_count
  gen_evm384_offsets(out,x,y,mod); print("mulmodmont384"); mulmodmont384_count+=1
  
def gen_f1neg(out,x,mod):
  global submod384_count
  gen_evm384_offsets(out,f1zero,x,mod); print("submod384"); submod384_count+=1

def gen_f1reciprocal(out_offset,in_offset,mod):
  pass
  #for bit in bin(mod-2)[2]:
  #  if bit:




# f2

def gen_f2add(out,x,y,mod):
  global f2add_count
  f2add_count+=1
  print("// f2 add")
  x0 = x
  x1 = x+48
  y0 = y
  y1 = y+48
  out0 = out
  out1 = out+48
  gen_f1add(out0,x0,y0,mod)
  gen_f1add(out1,x1,y1,mod)

def gen_f2sub(out,x,y,mod):
  global f2sub_count
  f2sub_count+=1
  print("// f2 sub")
  x0 = x
  x1 = x+48
  y0 = y
  y1 = y+48
  out0 = out
  out1 = out+48
  gen_f1sub(out0,x0,y0,mod)
  gen_f1sub(out1,x1,y1,mod)

def gen_f2mul(out,x,y,mod):
  global f2mul_count
  f2mul_count+=1
  print("// f2 mul")
  # get offsets
  x0 = x
  x1 = x+48
  y0 = y
  y1 = y+48
  out0 = out
  out1 = out+48
  # temporary values
  tmp1 = buffer_f2mul
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
    gen_f1mul(tmp1,x0,y0,mod)
    gen_f1mul(tmp2,x1,y1,mod)
    #gen_f1sub(tmp3,zero,tmp2,mod)
    #gen_f1add(out0,tmp1,tmp3,mod)
    gen_f1sub(out0,tmp1,tmp2,mod)		# above sub,add give same result as just this sub
    gen_f1mul(tmp1,x0,y1,mod)
    gen_f1mul(tmp2,x1,y0,mod)
    gen_f1add(out1,tmp1,tmp2,mod)
  elif 1:
    gen_f1mul(tmp1,x0,y0,mod)
    gen_f1mul(tmp2,x1,y1,mod)
    #gen_f1sub(tmp3,zero,tmp2,mod)
    #gen_f1add(out0,tmp1,tmp3,mod)
    gen_f1sub(out0,tmp1,tmp2,mod)		# above sub,add give same result as just this sub
    gen_f1add(tmp1,tmp1,tmp2,mod)
    gen_f1add(tmp2,x0,x1,mod)
    gen_f1add(tmp3,y0,y1,mod)
    gen_f1mul(tmp2,tmp2,tmp3,mod)
    gen_f1sub(out1,tmp2,tmp1,mod)
  elif 0:
    gen_f1mul(tmp1,x0,y0,mod)			# t1 = x0*y0
    gen_f1sub(tmp2,zero,x1,mod)			# t2 = -x1
    gen_f1mul(tmp2,tmp2,y1,mod)			# t2 = -x1*y1
    gen_f1add(out0,tmp1,tmp2,mod)		# out0 = t1+t2
    gen_f1add(tmp3,x0,x1,mod)			# t3 = x0+y0
    gen_f1add(out1,y0,y1,mod)			# out1 = x1+y1
    gen_f1mul(out1,out1,tmp3,mod)		# out1 = out1*t3
    gen_f1sub(out1,out1,tmp1,mod)		# out1 = out1-t1
    gen_f1add(out1,out1,tmp2,mod)		# out1 = out1+t2
  elif 0:
    gen_f1mul(tmp1,x0,y0,mod)                   # t1 = x0*y0
    gen_f1mul(tmp2,x1,y1,mod)                 # t2 = x1*y1
    gen_f1sub(out0,tmp1,tmp2,mod)               # out0 = t1-t2
    gen_f1add(tmp3,x0,x1,mod)                   # t3 = x0+y0
    gen_f1add(out1,y0,y1,mod)                   # out1 = x1+y1
    gen_f1mul(out1,out1,tmp3,mod)               # out1 = out1*t3
    gen_f1sub(out1,out1,tmp1,mod)               # out1 = out1-t1
    gen_f1sub(out1,out1,tmp2,mod)               # out1 = out1-t2



def gen_f2sqr(out,x,mod):
  global f2mul_count
  f2mul_count+=1
  print("// f2sqr")
  if 0:
    gen_f2mul(out,x,x,mod)
  else:
    # get offsets
    x0 = x
    x1 = x+48
    out0 = out
    out1 = out+48
    tmp0 = buffer_f2mul
    tmp1 = tmp0+48
    gen_f1add(tmp0,x0,x1,mod)
    gen_f1sub(tmp1,x0,x1,mod)
    gen_f1mul(out1,x0,x1,mod)
    gen_f1add(out1,out1,out1,mod)
    gen_f1mul(out0,tmp0,tmp1,mod)
  

def gen_f2neg(out,in_,mod):
  #gen_f2sub(out,zero,in_,mod)
  gen_f1sub(out,mod,in_,mod)
  gen_f1sub(out+48,mod,in_+48,mod)

def gen_mul_by_u_plus_1_fp2(out,x,mod):
  t = buffer_f2mul	# to prevent clobbering
  gen_f1sub(t, x, x+48, mod)
  gen_f1add(out+48, x, x+48, mod)
  gen_memcopy(out,t,48)


# f6

def gen_f6add(out,x,y,mod):
  global f6add_count
  f6add_count+=1
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
  gen_f2add(out0,x0,y0,mod)
  gen_f2add(out1,x1,y1,mod)
  gen_f2add(out2,x2,y2,mod)

def gen_f6sub(out,x,y,mod):
  global f6sub_count
  f6sub_count+=1
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
  gen_f2sub(out0,x0,y0,mod)
  gen_f2sub(out1,x1,y1,mod)
  gen_f2sub(out2,x2,y2,mod)

def gen_f6neg(out,x,mod):
  #gen_f6sub(out,f6zero,x,mod)
  #gen_f6sub(out,mod,x,mod)
  x0=x
  x1=x0+96
  x2=x1+96
  out0=out
  out1=out0+96
  out2=out1+96
  gen_f2neg(out0,x0,mod)
  gen_f2neg(out1,x1,mod)
  gen_f2neg(out2,x2,mod)

def gen_f6mul(out,x,y,mod):
  global f6mul_count
  f6mul_count+=1
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
  t0 = buffer_f6mul
  t1 = t0+96
  t2 = t1+96
  t3 = t2+96
  t4 = t3+96
  t5 = t4+96
  # algorithm
  gen_f2mul(t0,x0,y0,mod)
  gen_f2mul(t1,x1,y1,mod)
  gen_f2mul(t2,x2,y2,mod)
  # out0
  gen_f2add(t4,x1,x2,mod)
  gen_f2add(t5,y1,y2,mod)
  gen_f2mul(t3,t4,t5,mod)
  gen_f2sub(t3,t3,t1,mod)
  gen_f2sub(t3,t3,t2,mod)
  gen_mul_by_u_plus_1_fp2(t3,t3,mod)
  #gen_f2add(out0,t3,t0,mod)	# below
  # out1
  gen_f2add(t4,x0,x1,mod)
  gen_f2add(t5,y0,y1,mod)
  gen_f2mul(out1,t4,t5,mod)
  gen_f2sub(out1,out1,t0,mod)
  gen_f2sub(out1,out1,t1,mod)
  gen_mul_by_u_plus_1_fp2(t4,t2,mod)
  gen_f2add(out1,out1,t4,mod)
  # out2
  gen_f2add(t4,x0,x2,mod)
  gen_f2add(t5,y0,y2,mod)
  gen_f2mul(out2,t4,t5,mod)
  gen_f2sub(out2,out2,t0,mod)
  gen_f2sub(out2,out2,t2,mod)
  gen_f2add(out2,out2,t1,mod)

  gen_f2add(out0,t3,t0,mod)

def gen_f6sqr(out,x,mod):
  gen_f6mul(out,x,x,mod)	# TODO: optimize


# f12

def gen_f12add(out,x,y,mod):
  global f12add_count
  f12add_count+=1
  print("// f6 add")
  x0 = x
  x1 = x0+288
  y0 = y
  y1 = y0+288
  out0 = out
  out1 = out0+288
  gen_f6add(out0,x0,y0,mod)
  gen_f6add(out1,x1,y1,mod)
  
def gen_f12sub(out,x,y,mod):
  global f12sub_count
  f12sub_count+=1
  print("// f6 add")
  x0 = x
  x1 = x0+288
  y0 = y
  y1 = y0+288
  out0 = out
  out1 = out0+288
  gen_f6sub(out0,x0,y0,mod)
  gen_f6sub(out1,x1,y1,mod)

def gen_f12mul(out,x,y,mod):
  global f12mul_count
  f12mul_count+=1
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
  t0 = buffer_f12mul
  t00 = t0
  t01 = t00+96
  t02 = t01+96
  t1 = t0+288
  t10 = t1
  t11 = t10+96
  t12 = t11+96
  t2 = t1+288
  # debugging
  gen_f6mul(out0,x0,y0,mod)
  gen_f6mul(out1,x1,y1,mod)
  gen_f6mul(t0,x0,y0,mod)
  gen_f6mul(t1,x1,y1,mod)
  # out1
  gen_f6add(t2,x0,x1,mod)
  gen_f6add(out1,y0,y1,mod)
  gen_f6mul(out1,out1,t2,mod)
  gen_f6sub(out1,out1,t0,mod)
  gen_f6sub(out1,out1,t1,mod)
  # out0
  gen_mul_by_u_plus_1_fp2(t12,t12,mod)
  gen_f2add(out00,t00,t12,mod)
  gen_f2add(out01,t01,t10,mod)
  gen_f2add(out02,t02,t11,mod)

def gen_f12sqr(out,x,mod):
  #gen_f12mul(out,x,x,mod)		# TODO: optimize
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
  t0 = buffer_f12mul
  t00 = t0
  t01 = t00+96
  t02 = t01+96
  t1 = t0+288
  t10 = t1
  t11 = t10+96
  t12 = t11+96


  gen_f6add(t0,x0,x1,mod)

  # debugging
  #gen_memcopy(out0,t0,288)
  #gen_memcopy(out1,t0,288)

  gen_mul_by_u_plus_1_fp2(t12,x12,mod)
  gen_f2add(t10,x00,t12,mod)
  gen_f2add(t11,x01,x10,mod)
  gen_f2add(t12,x02,x11,mod)
  

  gen_f6mul(t0,t0,t1,mod)
  gen_f6mul(t1,x0,x1,mod)

  gen_f6add(out1,t1,t1,mod)

  gen_f6sub(out0,t0,t1,mod)
 
  gen_mul_by_u_plus_1_fp2(t12,t12,mod)
  gen_f2sub(out00,out00,t12,mod)
  gen_f2sub(out01,out01,t10,mod)
  gen_f2sub(out02,out02,t11,mod)


def gen_f12_conjugate(x,mod):
  x1 = x+288
  gen_f6neg(x1,x1,mod)


# f6 and f12 optimizations for custom operations

def gen_mul_by_0y0_fp6(out,x,y,mod):
  # out is f6, x is f6, y is f2
  x0 = x
  x1 = x0+96
  x2 = x1+96
  y0 = y
  y1 = y0+48
  out0 = out
  out1 = out0+96
  out2 = out1+96
  t = buffer_f6mul
  gen_f2mul(t,x2,y,mod)
  gen_f2mul(out2,x1,y,mod)
  gen_f2mul(out1,x0,y,mod)
  gen_mul_by_u_plus_1_fp2(out0,t,mod)
  
def gen_mul_by_xy0_fp6(out,x,y,mod):
  # out if f6, x is f6, y is f6
  x0 = x
  x1 = x0+96
  x2 = x1+96
  y0 = y
  y1 = y0+96
  y2 = y1+96
  out0 = out
  out1 = out0+96
  out2 = out1+96
  t0 = buffer_f6mul
  t1 = t0+96
  t2 = t1+96	# unused
  t3 = t2+96
  t4 = t3+96
  t5 = t4+96
  gen_f2mul(t0,x0,y0,mod)
  gen_f2mul(t1,x1,y1,mod)

  gen_f2mul(t3,x2,y1,mod)
  gen_mul_by_u_plus_1_fp2(t3,t3,mod)
  
  gen_f2add(t4,x0,x1,mod)
  gen_f2add(t5,y0,y1,mod)
  gen_f2mul(out1,t4,t5,mod)
  gen_f2sub(out1,out1,t0,mod)
  gen_f2sub(out1,out1,t1,mod)
  
  gen_f2mul(out2,x2,y0,mod)
  gen_f2add(out2,out2,t1,mod)

  gen_f2add(out0,t3,t0,mod)

def gen_mul_by_xy00z0_fp12(out,x,y,mod):
  # out is f12, x is f12, y is f6
  x0 = x
  x1 = x0+288
  y0 = y
  y1 = y0+96
  y2 = y1+96
  out0 = out
  out00 = out0
  out01 = out00+96
  out02 = out01+96
  out1 = out+288
  t0 = buffer_f12mul
  t00 = t0
  t01 = t00+96
  t02 = t01+96
  t1 = t0+288
  t10 = t1
  t11 = t10+96
  t12 = t11+96
  t2 = t1+288
  t20 = t2
  t21 = t2+96
  gen_mul_by_xy0_fp6(t0,x0,y,mod)
  gen_mul_by_0y0_fp6(t1,x1,y2,mod)
  gen_memcopy(t20,y0,96)
  gen_f2add(t21,y1,y2,mod)
  gen_f6add(out1,x0,x1,mod)
  gen_mul_by_xy0_fp6(out1,out1,t2,mod)
  gen_f6sub(out1,out1,t0,mod)
  gen_f6sub(out1,out1,t1,mod)
  gen_mul_by_u_plus_1_fp2(t12,t12,mod)
  gen_f2add(out00,t00,t12,mod)
  gen_f2add(out01,t01,t10,mod)
  gen_f2add(out02,t02,t11,mod)
  




###############################
# Curve operations: add, double

def gen_Eadd__madd_2001_b(f,XYZout,XYZ1,XYZ2,mod):
  print("/////////")
  print("// Eadd https://hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#addition-add-2001-b")
  # inputs/ouput
  X1=XYZ1
  Y1=X1+int(f[1])*48
  Z1=Y1+int(f[1])*48
  X2=XYZ2
  Y2=X2+int(f[1])*48
  Z2=Y2+int(f[1])*48
  X3=XYZout
  Y3=X3+int(f[1])*48
  Z3=Y3+int(f[1])*48
  """
  ZZ1 = Z1^2
  ZZZ1 = Z1*ZZ1
  ZZ2 = Z2^2
  ZZZ2 = Z2*ZZ2
  A = X1*ZZ2
  B = X2*ZZ1-A
  c = Y1*ZZZ2
  d = Y2*ZZZ1-c
  e = B^2
  f = B*e
  g = A*e
  h = Z1*Z2
  f2g = 2*g+f
  X3 = d^2-f2g
  Z3 = B*h
  gx = g-X3
  Y3 = d*gx-c*f
  """
  # temp vars
  ZZ1 = buffer_Eadd
  ZZZ1 = ZZ1+int(f[1])*48
  ZZ2 = ZZZ1+int(f[1])*48
  ZZZ2 = ZZ2+int(f[1])*48
  A = ZZZ2+int(f[1])*48
  B = A+int(f[1])*48
  c = B+int(f[1])*48
  d = c+int(f[1])*48
  e = d+int(f[1])*48
  f_ = e+int(f[1])*48
  g = f_+int(f[1])*48
  h = g+int(f[1])*48
  f2g = h+int(f[1])*48
  gx = f2g+int(f[1])*48

  print("ZZ1 = Z1^2")
  gen_fmul(f,ZZ1,Z1,Z1,mod)
  print("ZZZ1 = Z1*ZZ1")
  gen_fmul(f,ZZZ1,Z1,ZZ1,mod)
  print("ZZ2 = Z2^2")
  gen_fmul(f,ZZ2,Z2,Z2,mod)
  print("ZZZ2 = Z2*ZZ2")
  gen_fmul(f,ZZZ2,Z2,ZZ2,mod)
  print("A = X1*ZZ2")
  gen_fmul(f,A,X1,ZZ2,mod)
  print("B = X2*ZZ1-A")
  gen_fmul(f,B,X2,ZZ1,mod)
  gen_fsub(f,B,B,A,mod)
  print("c = Y1*ZZZ2")
  gen_fmul(f,c,Y1,ZZZ2,mod)
  print("d = Y2*ZZZ1-c")
  gen_fmul(f,d,Y2,ZZZ1,mod)
  gen_fsub(f,d,d,c,mod)
  print("e = B^2")
  gen_fmul(f,e,B,B,mod)
  print("f = B*e")
  gen_fmul(f,f_,B,e,mod)
  print("g = A*e")
  gen_fmul(f,g,A,e,mod)
  print("h = Z1*Z2")
  gen_fmul(f,h,Z1,Z2,mod)
  print("f2g = 2*g+f")
  gen_fadd(f,f2g,g,g,mod)
  gen_fadd(f,f2g,f2g,f_,mod)
  print("X3 = d^2-f2g")
  gen_fmul(f,X3,d,d,mod)
  gen_fsub(f,X3,X3,f2g,mod)
  print("Z3 = B*h")
  gen_fmul(f,Z3,B,h,mod)
  print("gx = g-X3")
  gen_fsub(f,gx,g,X3,mod)
  print("Y3 = d*gx-c*f")
  gen_fmul(f,Y3,d,g,mod)
  gen_fmul(f,c,c,f_,mod)	# clobber c
  gen_fsub(f,Y3,Y3,c,mod)

  print("// E add")
  print("/////////")

def gen_Eadd__madd_2007_bl(f,XYZout,XYZ1,XYZ2,line1,mod):
  print("/////////")
  print("// Eadd https://hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#addition-madd-2007-bl")
  # for pairing:
  #   line0 is useful for pairings which reuse that intermediate value in this calculation
  #   XYZout and XYZ are both T, and E2 point, and XYZ2 is Q which is affine E2 point

  # inputs/ouput
  X1=XYZ1
  Y1=X1+int(f[1])*48
  Z1=Y1+int(f[1])*48
  X2=XYZ2
  Y2=X2+int(f[1])*48
  Z2=Y2+int(f[1])*48
  X3=XYZout
  Y3=X3+int(f[1])*48
  Z3=Y3+int(f[1])*48

  # temp vars
  Z1Z1 = buffer_Eadd
  U2 = Z1Z1+int(f[1])*48
  S2 = U2+int(f[1])*48
  H = S2+int(f[1])*48
  HH = H+int(f[1])*48
  I = HH+int(f[1])*48
  J = I+int(f[1])*48
  V = J+int(f[1])*48
  r = line1 if line1 else V+int(f[1])*48

  # Z1Z1 = Z1^2
  print("// Z1Z1 = Z1^2")
  gen_fsqr(f,Z1Z1,Z1,mod)
  # U2 = X2*Z1Z1
  print("// U2 = X2*Z1Z1")
  gen_fmul(f,U2,X2,Z1Z1,mod)
  # S2 = Y2*Z1*Z1Z1
  print("// S2 = Y2*Z1*Z1Z1")
  gen_fmul(f,S2,Y2,Z1,mod)
  gen_fmul(f,S2,S2,Z1Z1,mod)
  # H = U2-X1
  print("// H = U2-X1")
  gen_fsub(f,H,U2,X1,mod)
  # HH = H^2
  print("// HH = H^2")
  gen_fsqr(f,HH,H,mod)
  # I = 4*HH
  print("// I = 4*HH")
  gen_fadd(f,I,HH,HH,mod)
  gen_fadd(f,I,I,I,mod)
  # J = H*I
  print("// J = H*I")
  gen_fmul(f,J,H,I,mod)
  # line0 = 2*(S2-Y1)
  print("// r = 2*(S2-Y1)")
  gen_fsub(f,r,S2,Y1,mod)
  gen_fadd(f,r,r,r,mod)
  # V = X1*I
  print("// V = X1*I")
  gen_fmul(f,V,X1,I,mod)
  # X3 = r^2-J-2*V
  print("// X3 = r^2-J-2*V")
  gen_fsqr(f,X3,r,mod)
  gen_fsub(f,X3,X3,J,mod)
  gen_fsub(f,X3,X3,V,mod)
  gen_fsub(f,X3,X3,V,mod)
  # Y3 = r*(V-X3)-2*Y1*J
  print("// Y3 = r*(V-X3)-2*Y1*J")
  gen_fmul(f,J,J,Y1,mod)
  gen_fsub(f,Y3,V,X3,mod)
  gen_fmul(f,Y3,Y3,r,mod)
  gen_fsub(f,Y3,Y3,J,mod)
  gen_fsub(f,Y3,Y3,J,mod)
  """
  gen_fsub(f,Y3,V,X3,mod)
  gen_fmul(f,Y3,r,Y3,mod)
  gen_fmul(f,V,Y1,J,mod)	# overwriting V
  gen_fsub(f,Y3,Y3,V,mod)
  gen_fsub(f,Y3,Y3,V,mod)
  """
  # Z3 = (Z1+H)^2-Z1Z1-HH
  print("// Z3 = (Z1+H)^2-Z1Z1-HH")
  gen_fadd(f,Z3,Z1,H,mod)
  gen_fsqr(f,Z3,Z3,mod)
  gen_fsub(f,Z3,Z3,Z1Z1,mod)
  gen_fsub(f,Z3,Z3,HH,mod)
  
  print("// E add")
  print("/////////")

  return I,J,r		# these are useful for pairing




def gen_Edouble__dbl_2009_alnr(f,XYZout,XYZ,line0,mod):
  # XYZout is E2 point, XYZ is E2 point		(note: for our pairing algorithm, T=XYZout=XYZ)
  # line is an extra f2 point, not part of dbl operation, but useful for pairing's line evaluation
  print("///////////")
  print("// Edouble https://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#doubling-dbl-2009-alnr")

  # inputs/ouput
  X1=XYZ
  Y1=X1+int(f[1])*48
  Z1=Y1+int(f[1])*48
  X3=XYZout
  Y3=X3+int(f[1])*48
  Z3=Y3+int(f[1])*48
  #print("gen_Edouble__dbl_2009_alnr(",X1,Y1,Z1,X3,Y3,Z3,")")

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
  B = A+int(f[1])*48
  ZZ = B+int(f[1])*48 
  C = ZZ+int(f[1])*48
  D = C+int(f[1])*48
  E = D+int(f[1])*48
  F = E+int(f[1])*48

  print("// A = X1^2")
  gen_fsqr(f,A,X1,mod)
  print("// B = Y1^2")
  gen_fsqr(f,B,Y1,mod)
  print("// ZZ = Z1^2")
  gen_fsqr(f,ZZ,Z1,mod)
  print("// C = B^2")
  gen_fsqr(f,C,B,mod)
  print("// D = 2*((X1+B)^2-A-C)")
  gen_fadd(f,D,X1,B,mod)
  gen_fsqr(f,D,D,mod)
  gen_fsub(f,D,D,A,mod)
  gen_fsub(f,D,D,C,mod)
  gen_fadd(f,D,D,D,mod)
  print("// E = 3*A")
  gen_fadd(f,E,A,A,mod)
  gen_fadd(f,E,E,A,mod)
  print("// F = E^2")
  gen_fsqr(f,F,E,mod)
  # note: the following is not part of the dbl, but is useful for line evaluation
  if line0:
    print("// line0 = E+X1, this is useful for pairing")
    gen_fadd(f,line0,E,X1,mod)
  print("// X3 = F-2*D")
  gen_fsub(f,X3,F,D,mod)
  gen_fsub(f,X3,X3,D,mod)
  print("// Z3 = (Y1+Z1)^2-B-ZZ")
  gen_fadd(f,Z3,Y1,Z1,mod)
  gen_fsqr(f,Z3,Z3,mod)
  gen_fsub(f,Z3,Z3,B,mod)
  gen_fsub(f,Z3,Z3,ZZ,mod)
  print("// Y3 = E*(D-X3)-8*C")
  gen_fsub(f,Y3,D,X3,mod)
  gen_fmul(f,Y3,E,Y3,mod)
  gen_fadd(f,C,C,C,mod)		# overwriting C
  gen_fadd(f,C,C,C,mod)
  gen_fadd(f,C,C,C,mod)
  gen_fsub(f,Y3,Y3,C,mod)
  print("// E double")
  print("////////////")
  return A,B,E,F,ZZ,X1

def gen_Edouble__dbl_2009_l(f,XYZout,XYZ,mod):
  print("///////////")
  print("// Edouble https://www.hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#doubling-dbl-2009-l")

  # inputs/ouput
  X1=XYZ
  Y1=X1+int(f[1])*48
  Z1=Y1+int(f[1])*48
  X3=XYZout
  Y3=X3+int(f[1])*48
  Z3=Y3+int(f[1])*48

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
  B = A+int(f[1])*48
  C = B+int(f[1])*48
  D = C+int(f[1])*48
  E = D+int(f[1])*48
  F = E+int(f[1])*48

  print("// A = X1^2")
  gen_fmul(f,A,X1,X1,mod)
  print("// B = Y1^2")
  gen_fmul(f,B,Y1,Y1,mod)
  print("// C = B^2")
  gen_fmul(f,C,B,B,mod)
  print("// D = 2*((X1+B)^2-A-C)")
  gen_fadd(f,D,X1,B,mod)
  gen_fmul(f,D,D,D,mod)
  gen_fsub(f,D,D,A,mod)
  gen_fsub(f,D,D,C,mod)
  gen_fadd(f,D,D,D,mod)
  print("// E = 3*A")
  gen_fadd(f,F,A,A,mod)
  gen_fadd(f,F,F,A,mod)
  print("// F = E^2")
  gen_fmul(f,F,E,E,mod)
  print("// X3 = F-2*D")
  gen_fadd(f,X3,D,D,mod)
  gen_fsub(f,X3,F,D,mod)
  print("// Y3 = E*(D-X3)-8*C")
  gen_fsub(f,Y3,D,X3,mod)
  gen_fmul(f,Y3,E,Y3,mod)
  gen_fadd(f,C,C,C,mod)		# clobber C
  gen_fadd(f,C,C,C,mod)
  gen_fadd(f,C,C,C,mod)
  gen_fsub(f,Y3,Y3,C,mod)
  print("// Z3 = 2*Y1*Z1")
  gen_fmul(f,Z3,Y1,Z1,mod)
  gen_fadd(f,Z3,Z3,Z3,mod)
  print("// E double")
  print("////////////")




#########
# Pairing

def gen_consts():
  # f12 one in mont form
  one = "15f65ec3fa80e4935c071a97a256ec6d77ce5853705257455f48985753c758baebf4000bc40c0002760900000002fffd"
  gen_memstore(f12one,bytearray.fromhex(one)[::-1])
  # prime
  p = "1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab"
  gen_memstore(mod,bytes.fromhex(p)[::-1])
  # inv
  inv="fdfffcfffcfff389000000000000000000000000000000000000000000000000"
  gen_memstore(mod+48,bytes.fromhex(inv))

def gen_line_add(line,T,R,Q,mod):
  # line is 3 f2s, T on E2, R on E2, Q on E2 affine
  TZ = T+192
  QX = Q
  QY = QX+96
  line0 = line
  line1 = line0+96
  line2 = line1+96
  # ecadd
  I,J,r = gen_Eadd__madd_2007_bl("f2",T,R,Q,line1,mod)
  # line eval
  gen_f2mul(I,r,QX,mod)
  gen_f2mul(J,QY,TZ,mod)
  gen_f2sub(I,I,J,mod)
  gen_f2add(line0,I,I,mod)
  #gen_memcopy(line1,r,96)	# already done in the 
  gen_memcopy(line2,TZ,96)	
  
def gen_line_dbl(line,T,Q,mod):
  # line is 3 f2s, T is E2 point, Q E2 point	(note: our pairing algorithm, T=Q)
  line0 = line
  line1 = line0+96
  line2 = line1+96
  QX = Q
  TZ = T+192
  # double
  A,B,E,F,ZZ,X1 = gen_Edouble__dbl_2009_alnr("f2",T,Q,line0,mod)
  # eval line
  # note: line0=E+QX is already done in alnr function
  gen_f2sqr(line0,line0,mod)
  gen_f2sub(line0,line0,A,mod)
  gen_f2sub(line0,line0,F,mod)
  gen_f2add(B,B,B,mod)
  gen_f2add(B,B,B,mod)
  gen_f2sub(line0,line0,B,mod)
  gen_f2mul(line1,E,ZZ,mod)
  gen_f2mul(line2,TZ,ZZ,mod)
  
def gen_line_by_Px2(line,Px2,mod):
  # line is 3 f2s, Px2 is E1 point affine
  Px2X = Px2
  Px2Y = Px2X+48
  line00 = line
  line01 = line00+48
  line10 = line01+48
  line11 = line10+48
  line20 = line11+48
  line21 = line20+48
  gen_f1mul(line10,line10,Px2X,mod)
  gen_f1mul(line11,line11,Px2X,mod)
  gen_f1mul(line20,line20,Px2Y,mod)
  gen_f1mul(line21,line21,Px2Y,mod)

def gen_start_dbl(out,T,Px2,mod):
  # out is f12 point (ie 2 f6 pts), T is E2 point, Px2 is E1 point (affine)
  out00 = out
  out11 = out+288+96	# ??
  line = buffer_line	# 3 f2 points
  line0 = line
  line2 = line0+192
  gen_line_dbl(line,T,T,mod)
  gen_line_by_Px2(line,Px2,mod)
  gen_memcopy(out,zero,576)
  gen_memcopy(out00,line0,192)
  gen_memcopy(out11,line2,96)

def gen_add_dbl_loop(out,T,Q,Px2,mod):
  line = buffer_line	# 3 f2 points
  print("0x3f")         # loop iterator, 63 iters
  #print("0x0 0x2 0x3 0x9 0x20 0x10") # jumk
  print("miller_loop:")
  print("0x1 swap1 sub")        # decrement loop iterator and leave it a top of stack
  print("0xd201000000010000 dup2 shr")   # get the next bit by shifting by loop iterator
  print("0x1 and")              # get next bit by shifting by loop iterator
  print("0x1 xor end_if jumpi")         # skip if next bit was 1 (ie skip if flipped bit is 1)
  print("begin_if:")    # if 1 bit, then add
  #print("0xffffff pop")
  gen_line_add(line,T,T,Q,mod)
  gen_line_by_Px2(line,Px2,mod)
  gen_mul_by_xy00z0_fp12(out,out,line,mod)
  print("end_if:")
  #print("0xffffffff pop")
  gen_f12sqr(out,out,mod)
  gen_line_dbl(line,T,T,mod)
  gen_line_by_Px2(line,Px2,mod)
  gen_mul_by_xy00z0_fp12(out,out,line,mod)
  print("dup1 0x1 lt")          # check if 1 < loop iterator	note: don't iterate on least significant bit
  #print("dup1 0x62 lt")          # check if 1 < loop iterator	note: don't iterate on least significant bit
  print("miller_loop jumpi")    # if loop iterator > 0, then jump to next iter
  print("pop")			# pop loop iterator to leave stack how we found it
  
  """
  #0xd201000000010000
  #0b
1
10
100
100000000
10000000000000000000000000000000
10000000000000000
  """
  
  
  
def gen_miller_loop(out,P,Q,mod):
  # P is E1 point (affine), Q is E2 point (affine)
  PX = P
  PY = PX+48
  QX = Q
  # temp offsets
  T = buffer_miller_loop	# E2 point
  TX = T
  TY = TX+96
  TZ = TY+96
  Px2 = T+288			# E1 point (affine)
  Px2X = Px2
  Px2Y = Px2+48
  # huff module
  print("#define macro MILLER_LOOP = takes(0) returns(0) {")
  gen_consts()	# TODO: put this somewhere else
  # prepare some stuff
  gen_f1add(Px2X,PX,PX,mod)
  gen_f1neg(Px2X,Px2X,mod)
  gen_f1add(Px2Y,PY,PY,mod)
  gen_memcopy(TX,QX,192)
  gen_memcopy(TZ,f12one,96)
  # execute
  gen_start_dbl(out,T,Px2,mod)
  gen_add_dbl_loop(out,T,Q,Px2,mod)


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
  gen_f12_conjugate(out,mod)
  print("} // MILLER_LOOP")

def gen_final_exponentiation(out,in_):
  pass

def gen_pairing():
  # input
  gen_miller_loop(buffer_output,buffer_inputs,buffer_inputs+96,mod)
  #gen_final_exponentiation(buffer_output,buffer_output)

  


  

def gen_add_dbl_unrolled(out,T,Q,Px2,k,mod):
  line = buffer_line    # 3 f2 points
  """
  gen_line_add(line,T,T,Q,mod)
  gen_line_by_Px2(line,Px2,mod)
  gen_mul_by_xy00z0_fp12(out,out,line,mod)
  """
  # loop init   #TODO
  # put k on stack
  # while(k--)
  for i in range(k):
    gen_f12sqr(out,out,mod)
    gen_line_dbl(line,T,T,mod)
    gen_line_by_Px2(line,Px2,mod)
    gen_mul_by_xy00z0_fp12(out,out,line,mod)


def gen_miller_loop_unrolled(out,P,Q,mod):
  # P is E1 point (affine), Q is E2 point (affine)
  PX = P
  PY = PX+48
  QX = Q
  # temp offsets
  T = buffer_miller_loop	# E2 point
  TX = T
  TY = TX+96
  TZ = TY+96
  Px2 = T+288			# E1 point (affine)
  Px2X = Px2
  Px2Y = Px2+48
  # huff module
  print("#define macro MILLER_LOOP = takes(0) returns(0) {")
  gen_consts()	# TODO: put this somewhere else
  # prepare some stuff
  gen_f1add(Px2X,PX,PX,mod)
  gen_f1neg(Px2X,Px2X,mod)
  gen_f1add(Px2Y,PY,PY,mod)
  gen_memcopy(TX,QX,192)
  gen_memcopy(TZ,f12one,96)
  # execute
  gen_start_dbl(out,T,Px2,mod)
  gen_add_dbl_unrolled(out,T,Q,Px2,2,mod)
  gen_add_dbl_unrolled(out,T,Q,Px2,3,mod)
  gen_add_dbl_unrolled(out,T,Q,Px2,9,mod)
  gen_add_dbl_unrolled(out,T,Q,Px2,32,mod)
  gen_add_dbl_unrolled(out,T,Q,Px2,16,mod)

  gen_f12_conjugate(out,mod)
  print("} // MILLER_LOOP")


def gen_pairing_unrolled():
  # input
  gen_miller_loop_unrolled(buffer_output,buffer_inputs,buffer_inputs+96,mod)
  #gen_final_exponentiation(buffer_output,buffer_output)
  print(addmod384_count)
  print(submod384_count)
  print(mulmodmont384_count)

  

if __name__=="__main__":
  #gen_Eadd__madd_2007_bl("f2",1,2,3,4)
  #gen_Edouble__dbl_2009_alnr("f2",1,2,3)
  #gen_Eadd__madd_2007_bl("f1",1,2,3,4)
  #gen_Edouble__dbl_2009_alnr("f2",1,2,3)
  #gen_Eadd__madd_2001_b("f2",1,2,3,4)
  #gen_Edouble__dbl_2009_l("f2",1,2,3)
  #gen_Eadd__madd_2007_bl("f2",1,2,3,4)
  print()
  print()
  addmod384_count=0
  submod384_count=0
  mulmodmont384_count=0
  gen_pairing()
  #gen_pairing_unrolled()
  #gen_test_case_values()
  #print("f12one, mod, buffer_miller_loop, buffer_line, buffer_f2mul, buffer_f6mul, buffer_f12mul, buffer_Eadd, buffer_Edouble, buffer_inputs, buffer_output")
  #print(f12one, mod, buffer_miller_loop, buffer_line, buffer_f2mul, buffer_f6mul, buffer_f12mul, buffer_Eadd, buffer_Edouble, buffer_inputs, buffer_output)
  if 0:
    print("addmod384_count ",addmod384_count)
    print("submod384_count ",submod384_count)
    print("mulmodmont384_count ",mulmodmont384_count)
  #global f2add_count
  #global f2sub_count
  #global f2mul_count
  """
  print("f2add_count ",f2add_count)
  print("f2sub_count ",f2sub_count)
  print("f2mul_count ",f2mul_count)
  print("addmod384_count ",addmod384_count)
  print("submod384_count ",submod384_count)
  print("mulmodmont384_count ",mulmodmont384_count)
  """



