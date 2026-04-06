import frappe
from frappe.model.document import Document

from chakra.validators import (
    normalize_aadhaar_number,
    normalize_bank_account,
    normalize_ifsc_code,
    normalize_mobile_number,
    normalize_upi_id,
)


class Operator(Document):
    def validate(self):
        self.prevent_mobile_rename()
        self.normalize_identifiers()
        self.validate_user_mapping()

    def prevent_mobile_rename(self):
        if not self.is_new() and frappe.db.get_value(self.doctype, self.name, "mobile") != self.mobile:
            frappe.throw("Mobile Number is used as the Operator ID and cannot be changed after creation.")

    def normalize_identifiers(self):
        self.mobile = self._normalize_field(self.mobile, normalize_mobile_number)
        self.aadhar_number = self._normalize_field(self.aadhar_number, normalize_aadhaar_number)
        self.bank_account = self._normalize_field(self.bank_account, normalize_bank_account)
        self.ifsc_code = self._normalize_field(self.ifsc_code, normalize_ifsc_code)
        self.upi_id = self._normalize_field(self.upi_id, normalize_upi_id)

    def validate_user_mapping(self):
        if not self.user_id:
            return

        linked_operators = frappe.get_all(
            "Operator",
            filters={"user_id": self.user_id},
            pluck="name",
        )

        if any(operator_name != self.name for operator_name in linked_operators):
            frappe.throw("This User is already linked to another Operator record.")

    @staticmethod
    def _normalize_field(value, normalizer):
        try:
            return normalizer(value)
        except ValueError as exc:
            frappe.throw(str(exc))
