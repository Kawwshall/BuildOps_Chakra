import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, today

from chakra.permissions import user_is_privileged


class VendorInvoice(Document):
    def validate(self):
        self.set_defaults()
        self.validate_vendor_user()
        self.validate_invoice_uniqueness()
        self.validate_period()
        self.validate_project_window()
        self.validate_status_updates()

    def set_defaults(self):
        if not self.invoice_date:
            self.invoice_date = today()

        if not self.status:
            self.status = "Submitted"

    def validate_vendor_user(self):
        if not self.vendor_user:
            if "FF Vendor" in frappe.get_roles(frappe.session.user) and not user_is_privileged(frappe.session.user):
                self.vendor_user = frappe.session.user
            else:
                frappe.throw("Vendor User is required.")

        if "FF Vendor" in frappe.get_roles(frappe.session.user) and not user_is_privileged(frappe.session.user):
            if self.vendor_user != frappe.session.user:
                frappe.throw("Vendors can only submit invoices for their own login.")

    def validate_invoice_uniqueness(self):
        if not self.vendor_user or not self.invoice_number:
            return

        duplicate = frappe.db.exists(
            "Vendor Invoice",
            {"vendor_user": self.vendor_user, "invoice_number": self.invoice_number},
        )

        if duplicate and duplicate != self.name:
            frappe.throw("This invoice number is already used for the selected vendor.")

    def validate_period(self):
        if not self.period_start or not self.period_end:
            return

        if self.period_end < self.period_start:
            frappe.throw("Invoice period end date cannot be earlier than period start date.")

    def validate_project_window(self):
        if not self.project or not self.period_start or not self.period_end:
            return

        project = frappe.db.get_value(
            "FF Project",
            self.project,
            ["start_date", "end_date"],
            as_dict=True,
        )

        if project and project.start_date and self.period_start < project.start_date:
            frappe.throw("Invoice period cannot start before the project start date.")

        if project and project.end_date and self.period_end > project.end_date:
            frappe.throw("Invoice period cannot end after the project end date.")

    def validate_status_updates(self):
        is_vendor = "FF Vendor" in frappe.get_roles(frappe.session.user)
        is_privileged = user_is_privileged(frappe.session.user)

        if is_vendor and not is_privileged and self.status != "Submitted":
            frappe.throw("Vendors can only submit invoices. Approval and payment updates are handled by management.")

        if self.status not in {"Approved", "Paid", "Rejected"}:
            self.processed_by = ""
            self.processed_on = None
            if self.status != "Paid":
                self.payment_reference = ""
                self.payment_date = None
            return

        if not is_privileged:
            frappe.throw("Only System Managers and FF Chiefs can approve, reject, or pay invoices.")

        if self.status == "Paid" and not self.payment_reference:
            frappe.throw("Payment Reference is required before marking an invoice as Paid.")

        if self.status == "Paid" and not self.payment_date:
            self.payment_date = today()

        self.processed_by = frappe.get_value("User", frappe.session.user, "full_name") or frappe.session.user
        self.processed_on = now_datetime()
