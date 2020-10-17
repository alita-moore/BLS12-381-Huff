import unittest
from compiler import Huff

class CompilerTests(unittest.TestCase):
    def runTest(self):
        self.assert_gen_memstore()
        
    def assert_gen_memstore(self):
        buffer_offset = 0
        buffer_offset += 576
        buffer_offset += 576
        buffer_offset += 56
        buffer_offset += 288+96
        buffer_offset += 288
        buffer_offset += 144
        buffer_offset += 576
        buffer_offset += 864
        buffer_offset += 14*3*96
        buffer_offset += 7*3*96
        buffer_inputs = buffer_offset

        huff = Huff()
        # test from https://tools.ietf.org/id/draft-yonezawa-pairing-friendly-curves-02.html#rfc.appendix.B
        # Input x,y values:
        inE1  = bytearray.fromhex("120177419e0bfb75edce6ecc21dbf440f0ae6acdf3d0e747154f95c7143ba1c17817fc679976fff55cb38790fd530c16")[::-1]
        inE1  += bytearray.fromhex("0e44d2ede97744303cff1b76964b531712caf35ba344c12a89d7738d9fa9d05592899ce4383b0270ff526c2af318883a")[::-1]
        huff.gen_memstore(buffer_inputs,inE1)
        inE2 = bytearray.fromhex("058191924350bcd76f67b7631863366b9894999d1a3caee9a1a893b53e2ae580b3f5fb2687b4961af5f28fa202940a10")[::-1] 
        inE2 += bytearray.fromhex("11922a097360edf3c2b6ed0ef21585471b1ab6cc8541b3673bb17e18e2867806aaa0c59dbccd60c3a5a9c0759e23f606")[::-1] 
        inE2 += bytearray.fromhex("197d145bbaff0bb54347fe40525c8734a887959b8577c95f7f4a4d344ca692c9c52f05df531d63a56d8bf5079fb65e61")[::-1] 
        inE2 += bytearray.fromhex("0ed54f48d5a1caa764044f659f0ee1e9eb2def362a476f84e0832636bacc0a840601d8f4863f9e230c3e036d209afa4e")[::-1] 
        huff.gen_memstore(buffer_inputs+96, inE2)

        # expected from https://gist.github.com/poemm/87969fe13ec5656d63230ac95d56fc36
        expected = [
            "0x160c53fd9087b35cf5ff769967fc1778c1a13b14c7954f1547e7d0f3cd6aaef0 0x2528 mstore",
            "0x40f4db21cc6eceed75fb0b9e417701123a8818f32a6c52ff70023b38e49c8992 0x2548 mstore",
            "0x55d0a99f8d73d7892ac144a35bf3ca1217534b96761bff3c304477e9edd2440e 0x2568 mstore",
            "0x100a9402a28ff2f51a96b48726fbf5b380e52a3eb593a8a1e9ae3c1a9d999498 0x2588 mstore",
            "0x6b36631863b7676fd7bc50439291810506f6239e75c0a9a5c360cdbc9dc5a0aa 0x25a8 mstore",
            "0x067886e2187eb13b67b34185ccb61a1b478515f20eedb6c2f3ed6073092a9211 0x25c8 mstore",
            "0x615eb69f07f58b6da5631d53df052fc5c992a64c344d4a7f5fc977859b9587a8 0x25e8 mstore",
            "0x34875c5240fe4743b50bffba5b147d194efa9a206d033e0c239e3f86f4d80106 0x2608 mstore",
            "0x840accba362683e0846f472a36ef2debe9e10e9f654f0464a7caa1d5484fd50e 0x2628 mstore"
        ]

        for i, line in enumerate(huff.lines):
            self.assertEqual(line, expected[i])

    def assert_gen_memcopy(self):
        huff = Huff()
         
        buffer_offset = 0
        buffer_offset += 576
        buffer_offset += 576
        buffer_offset += 56
        buffer_offset += 288+96
        buffer_offset += 288
        buffer_f2mul = buffer_offset	# 3 f1 points
        buffer_offset += 144
        buffer_f6mul = buffer_offset	# 6 f2 points
        t0 = buffer_f6mul
        t1 = t0+96
        t2 = t1+96
        t3 = t2+96
        t = buffer_f2mul	# to prevent clobbering
        huff.gen_memcopy(t3,t,48)

        

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(CompilerTests())
