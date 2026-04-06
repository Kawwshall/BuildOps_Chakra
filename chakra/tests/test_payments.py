import unittest

from chakra.payments import calculate_payable_amount


class TestPayments(unittest.TestCase):
    def test_present_day_payment(self):
        self.assertEqual(calculate_payable_amount("Present", 1200), 1200.0)

    def test_half_day_payment(self):
        self.assertEqual(calculate_payable_amount("Half Day", 1200), 600.0)

    def test_absent_payment(self):
        self.assertEqual(calculate_payable_amount("Absent", 1200), 0.0)

    def test_unknown_status_defaults_to_zero(self):
        self.assertEqual(calculate_payable_amount("Unknown", 1200), 0.0)


if __name__ == "__main__":
    unittest.main()
