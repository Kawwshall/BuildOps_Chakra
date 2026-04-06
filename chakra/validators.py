import re


def normalize_mobile_number(value):
    if not value:
        raise ValueError("Mobile Number is required.")

    digits = digits_only(value)
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    if len(digits) != 10:
        raise ValueError("Mobile Number must be exactly 10 digits.")

    return digits


def normalize_aadhaar_number(value):
    if not value:
        return ""

    digits = digits_only(value)
    if len(digits) != 12:
        raise ValueError("Aadhar Number must be exactly 12 digits.")

    return digits


def normalize_bank_account(value):
    if not value:
        return ""

    digits = digits_only(value)
    if len(digits) < 9 or len(digits) > 18:
        raise ValueError("Bank Account Number must be between 9 and 18 digits.")

    return digits


def normalize_ifsc_code(value):
    if not value:
        return ""

    code = str(value).strip().upper()
    if not re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", code):
        raise ValueError("IFSC Code format is invalid.")

    return code


def normalize_upi_id(value):
    if not value:
        return ""

    upi_id = str(value).strip().lower()
    if not re.fullmatch(r"[a-z0-9._-]{2,256}@[a-z][a-z0-9.-]{1,63}", upi_id):
        raise ValueError("UPI ID format is invalid.")

    return upi_id


def digits_only(value):
    return "".join(ch for ch in str(value) if ch.isdigit())
