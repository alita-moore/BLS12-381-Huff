from compiler import Huff, F1, F2, F6, F12

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