"""Host semantic tests of the actual freestanding byte routines (no MCU claim)."""
import ctypes
import pathlib
import random
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class RuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        path = pathlib.Path(cls.tmp.name) / "runtime.dylib"
        subprocess.run(["cc", "-shared", "-fPIC", "-std=c11", "-O2",
                        "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                        "-Dmemcpy=apo_memcpy", "-Dmemset=apo_memset", "-Dmemcmp=apo_memcmp",
                        "-I" + str(ROOT / "runtime/include"),
                        str(ROOT / "runtime/string.c"), "-o", str(path)], check=True)
        cls.lib = ctypes.CDLL(str(path))
        cls.lib.apo_memcpy.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        cls.lib.apo_memcpy.restype = ctypes.c_void_p
        cls.lib.apo_memset.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t]
        cls.lib.apo_memset.restype = ctypes.c_void_p
        cls.lib.apo_memcmp.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        cls.lib.apo_memcmp.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_copy_fill_unsigned_compare_and_guards(self):
        rng = random.Random(0xA902)
        for n in [0, 1, 3, 4, 7, 34, 255, 256, 513]:
            for offset in [1, 2, 3]:
                data = bytes(rng.randrange(256) for _ in range(n))
                src = ctypes.create_string_buffer(data)
                dst = ctypes.create_string_buffer(b"\xa5" * (n + 8), n + 8)
                addr = ctypes.addressof(dst) + offset
                self.assertEqual(self.lib.apo_memcpy(addr, src, n), addr)
                self.assertEqual(dst.raw[offset:offset + n], data)
                self.assertEqual(dst.raw[:offset], b"\xa5" * offset)
                self.assertEqual(dst.raw[offset + n:], b"\xa5" * (8 - offset))
                self.assertEqual(self.lib.apo_memcmp(addr, src, n), 0)
                for value in [-1, 0, 256, 511]:
                    self.assertEqual(self.lib.apo_memset(addr, value, n), addr)
                    self.assertEqual(dst.raw[offset:offset + n], bytes([value & 255]) * n)
        self.assertGreater(self.lib.apo_memcmp(b"\xff", b"\x01", 1), 0)
        self.assertLess(self.lib.apo_memcmp(b"\x01", b"\xff", 1), 0)

if __name__ == "__main__":
    unittest.main()
