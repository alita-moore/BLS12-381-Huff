###########
# Constants

bls12_384_prime = 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab

# offsets for zero, input/output, and local buffers
buffer_offset = 0
zero = buffer_offset
f1zero = buffer_offset  # 48 bytes
f2zero = buffer_offset  # 96 bytes
f6zero = buffer_offset  # 288 bytes
f12zero = buffer_offset  # 576 bytes
buffer_offset += 576
f12one = buffer_offset  # 576 bytes
buffer_offset += 576
mod = buffer_offset  # 56 bytes, mod||inv
buffer_offset += 56
buffer_miller_loop = buffer_offset  # 1 E2 point, 1 E1 point affine
buffer_offset += 288 + 96
buffer_line = buffer_offset  # 3 f2 points
buffer_offset += 288
buffer_f2mul = buffer_offset  # 3 f1 points
buffer_offset += 144
buffer_f6mul = buffer_offset  # 6 f2 points
buffer_offset += 576
buffer_f12mul = buffer_offset  # 3 f6 points
buffer_offset += 864
buffer_Eadd = buffer_offset  # 14 or 9 values
buffer_offset += 14 * 3 * 96
buffer_Edouble = buffer_offset  # 7 or 6 values
buffer_offset += 7 * 3 * 96
buffer_inputs = buffer_offset
buffer_offset += 2 * 48 + 2 * 96
buffer_output = buffer_offset
buffer_offset += 12 * 48