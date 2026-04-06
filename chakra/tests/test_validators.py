import unittest

from chakra.validators import (
    normalize_aadhaar_number,
    normalize_bank_account,
    normalize_ifsc_code,
    normalize_mobile_number,
    normalize_upi_id,
)


class TestValidators(unittest.TestCase):
    def test_mobile_normalization(self):
        self.assertEqual(normalize_mobile_number("+91 98765 43210"), "9876543210")

    def test_mobile_validation(self):
        with self.assertRaises(ValueError):
            normalize_mobile_number("12345")

    def test_aadhaar_normalization(self):
        self.assertEqual(normalize_aadhaar_number("1234 5678 9012"), "123456789012")

    def test_ifsc_normalization(self):
        self.assertEqual(normalize_ifsc_code("hdfc0123456"), "HDFC0123456")

    def test_upi_normalization(self):
        self.assertEqual(normalize_upi_id("Worker.One@OKHDFC"), "worker.one@okhdfc")

    def test_bank_account_validation(self):
        with self.assertRaises(ValueError):
            normalize_bank_account("1234")


if __name__ == "__main__":
    unittest.main()
