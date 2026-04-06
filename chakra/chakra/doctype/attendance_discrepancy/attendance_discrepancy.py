import frappe
from frappe.model.document import Document

from chakra.permissions import get_operator_for_user, user_is_privileged


class AttendanceDiscrepancy(Document):
    def validate(self):
        self.link_operator_to_logged_in_user()
        self.validate_project_membership()
        self.prevent_duplicate_pending_discrepancies()
        self.apply_resolution_workflow()

    def link_operator_to_logged_in_user(self):
        if user_is_privileged(frappe.session.user):
            return

        if "FF Operator" not in frappe.get_roles(frappe.session.user):
            return

        operator = get_operator_for_user(frappe.session.user)
        if not operator:
            frappe.throw("This user is not linked to any Operator record.")

        if self.operator and self.operator != operator:
            frappe.throw("You can only create discrepancies for your own Operator record.")

        self.operator = operator

    def validate_project_membership(self):
        if not self.project or not self.operator:
            return

        if not frappe.db.exists("FF Roster Entry", {"parent": self.project, "operator": self.operator}):
            frappe.throw("Discrepancies can only be raised for operators who are part of the selected project roster.")

    def prevent_duplicate_pending_discrepancies(self):
        if not self.operator or not self.project or not self.attendance_date:
            return

        duplicate = frappe.db.exists(
            "Attendance Discrepancy",
            {
                "operator": self.operator,
                "project": self.project,
                "attendance_date": self.attendance_date,
                "resolution_status": "Pending",
            },
        )

        if duplicate and duplicate != self.name:
            frappe.throw("There is already a pending discrepancy for this operator, project, and date.")

    def apply_resolution_workflow(self):
        if self.resolution_status not in {"Approved", "Rejected"}:
            self.resolved_by = ""
            self.resolved_on = None
            return

        if not user_is_privileged(frappe.session.user):
            frappe.throw("Only System Managers and FF Chiefs can resolve discrepancies.")

        if not self.resolution_note:
            frappe.throw("Please add a short resolution note before resolving this discrepancy.")

        self.resolved_by = frappe.get_value("User", frappe.session.user, "full_name") or frappe.session.user
        self.resolved_on = frappe.utils.now_datetime()

        if self.resolution_status == "Approved":
            self.upsert_attendance()

    def upsert_attendance(self):
        attendance_name = frappe.db.exists(
            "FF Attendance",
            {
                "project": self.project,
                "operator": self.operator,
                "date": self.attendance_date,
            },
        )

        if attendance_name:
            attendance = frappe.get_doc("FF Attendance", attendance_name)
            attendance.status = self.claimed_status
            attendance.save(ignore_permissions=True)
            return

        attendance = frappe.get_doc(
            {
                "doctype": "FF Attendance",
                "project": self.project,
                "operator": self.operator,
                "date": self.attendance_date,
                "status": self.claimed_status,
            }
        )
        attendance.insert(ignore_permissions=True)
