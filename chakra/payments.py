PAYABLE_FACTORS = {
    "Present": 1.0,
    "Half Day": 0.5,
    "Absent": 0.0,
}


def calculate_payable_amount(status, daily_rate):
    rate = float(daily_rate or 0)
    factor = PAYABLE_FACTORS.get(status or "", 0.0)
    return round(rate * factor, 2)
