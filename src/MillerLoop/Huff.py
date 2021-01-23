import binascii
import codecs

hexlify = codecs.getencoder('hex')

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
        if len(bytes_) < 32:
            print("ERROR gen_copy() fewer than 32 bytes needs special handling, len_ is only ", len_)
            return
        idx = 0
        while idx < len(bytes_) - 32:
            # e.g. 0xfdfffcfffcfff389000000000000000000000000000000000000000000000000 0x4b0 mstore
            line = "0x" + str(binascii.hexlify(bytes_[idx:idx + 32]))[2:-1] + ' '
            line += hex(dst_offset) + ' '
            line += "mstore"
            self.lines.append(line)
            # step
            dst_offset += 32
            idx += 32
        line = "0x" + str(binascii.hexlify(bytes_[-32:]))[2:-1] + ' '
        line += hex(dst_offset + len(bytes_[idx:]) - 32) + ' '
        line += "mstore"
        self.lines.append(line)

    def gen_memcopy(self, dst_offset, src_offset, len_):
        """
      copies the object into memory
    """
        if len_ < 32:
            print("ERROR gen_memcopy() len_ is ", len_)
            return
        while len_ > 32:
            len_ -= 32
            self.lines.append(hex(src_offset))
            self.lines.append("mload")
            self.lines.append(hex(dst_offset))
            self.lines.append("mstore")
            src_offset += 32
            dst_offset += 32
        self.lines.append(hex(src_offset - (32 - len_)))
        self.lines.append("mload")
        self.lines.append(hex(dst_offset - (32 - len_)))
        self.lines.append("mstore")

    def gen_isNonzero(self, offset, len_):
        # leaves stack item 0 if zero or >0 if nonzero
        # len_ must be >=33 bytes
        if len_ < 32:
            print("ERROR gen_isZero() len_ is ", len_)
            return
        self.lines.append(hex(offset))
        self.lines.append("mload")
        self.lines.append("iszero 0x1 sub")
        buffer_ = offset
        buffer_ += 32
        len_ -= 32
        while len_ > 32:
            self.lines.append(hex(offset))
            self.lines.append("mload")
            self.lines.append("iszero 0x1 sub")
            self.lines.append("add")
            buffer_ += 32
            len_ -= 32
        # final check
        if len_ > 0:
            self.lines.append(hex(buffer_ - (32 - len_)))
            self.lines.append("mload")
            self.lines.append("iszero 0x1 sub")
            self.lines.append("add")

    def gen_evm384_offsets(self, a, b, c, d, op):
        self.lines.append("0x" + hex(a)[2:].zfill(8) + hex(b)[2:].zfill(8) + hex(c)[2:].zfill(8) + hex(d)[2:].zfill(8) + ' ' + op)

    def pushln(self, line):
        self.lines.append(line)