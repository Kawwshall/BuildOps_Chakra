import frappe
from frappe.model.document import Document

from chakra.payments import calculate_payable_amount


class FFAttendance(Document):
    def validate(self):
        self.set_marked_by()
        self.validate_project_membership()
        self.validate_attendance_date()
        self.prevent_duplicate_attendance()
        self.set_rates_and_payable_amount()

    def set_marked_by(self):
        if not self.marked_by:
            self.marked_by = frappe.get_value("User", frappe.session.user, "full_name") or frappe.session.user

    def validate_project_membership(self):
        if not self.project or not self.operator:
            return

        if not frappe.db.exists("FF Roster Entry", {"parent": self.project, "operator": self.operator}):
            frappe.throw("Attendance can only be marked for operators who are part of the selected project roster.")

    def validate_attendance_date(self):
        if not self.project or not self.date:
            return

        project = frappe.db.get_value(
            "FF Project",
            self.project,
            ["start_date", "end_date"],
            as_dict=True,
        )

        if project and project.start_date and self.date < project.start_date:
            frappe.throw("Attendance date cannot be earlier than the project start date.")

        if project and project.end_date and self.date > project.end_date:
            frappe.throw("Attendance date cannot be later than the project end date.")

    def prevent_duplicate_attendance(self):
        if not self.project or not self.operator or not self.date:
            return

        duplicate = frappe.db.exists(
            "FF Attendance",
            {"project": self.project, "operator": self.operator, "date": self.date},
        )

        if duplicate and duplicate != self.name:
            frappe.throw("Attendance is already marked for this operator, project, and date.")

    def set_rates_and_payable_amount(self):
        if not self.daily_rate and self.operator and self.project:
            rate = frappe.db.get_value(
                "FF Roster Entry",
                {"parent": self.project, "operator": self.operator},
                "daily_rate",
            )
            if rate:
                self.daily_rate = rate

        self.payable_amount = calculate_payable_amount(self.status, self.daily_rate)
