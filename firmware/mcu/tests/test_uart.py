"""Compile/run the actual USART2 backend against a deterministic register model."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class UartTest(unittest.TestCase):
    def test_register_model_both_variants(self):
        with tempfile.TemporaryDirectory() as directory:
            for variant in (0, 1):
                with self.subTest(variant=variant):
                    binary = str(pathlib.Path(directory) / f"uart-{variant}")
                    subprocess.run(["cc", "-std=c11", "-O2", "-Wall", "-Wextra",
                                    "-Werror", f"-DSMART_APO_VARIANT={variant}",
                                    "-I" + str(ROOT / "include"),
                                    str(ROOT / "tests/uart_registers.c"), "-o", binary], check=True)
                    subprocess.run([binary], check=True, timeout=10)

if __name__ == "__main__":
    unittest.main()
