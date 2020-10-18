from EVM import EVM
evm = EVM(32)
evm.mstore(23, bytearray(range(256)))
print(evm.m)
quit()

# def add(BIGINT_BITS, LIMB_BITS, out, x, y):
#   NUM_LIMBS = int(BIGINT_BITS / LIMB_BITS)
  
#   expected = int(x) + int(y)
#   print(expected)
#   out = ["0"] * LIMB_BITS
#   x = ["0"] * (LIMB_BITS - len(x)) + [i for i in x]
#   y = ["0"] * (LIMB_BITS - len(y)) + [i for i in y]
#   print(x)
#   print(y)
#   c = 0
#   print(NUM_LIMBS)
#   for i in range(LIMB_BITS):
#     temp = int(x[i]) + c
#     out[i] = str(temp + int(y[i]))
    
#     if temp < c:
#       c = 1
#     elif int(out[i]) < temp:
#       c = 1
#     else:
#       c = 0
#   return int(''.join(out))

# def pack_64_bigint(i):
#   b = bytearray()
#   while i:
#     b.append(i % 2**64)
#     i >>= 64
#   return b

# def unpack_bigint(b):
#   b = bytearray(b) # in case you're passing in a bytes/str
#   return sum((1 << (bi*64)) * bb for (bi, bb) in enumerate(b))


# print(add(384, 64, "0000000000000", "342342342342434", "231231231231231"))