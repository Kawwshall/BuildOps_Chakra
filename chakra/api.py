import frappe
from frappe.utils import getdate, nowdate

from chakra.permissions import get_operator_for_user


@frappe.whitelist()
def get_my_operator_stats(from_date=None, to_date=None):
    operator_name = get_operator_for_user(frappe.session.user)

    if not operator_name:
        frappe.throw("This user is not linked to an Operator record.")

    date_filters = {}
    if from_date or to_date:
        date_filters["date"] = [
            "between",
            [getdate(from_date) if from_date else "1900-01-01", getdate(to_date) if to_date else nowdate()],
        ]

    attendance_filters = {"operator": operator_name, **date_filters}
    attendance_rows = frappe.get_all(
        "FF Attendance",
        filters=attendance_filters,
        fields=["project", "date", "status", "payable_amount"],
        order_by="date desc",
    )

    summary = {
        "present_days": 0,
        "half_days": 0,
        "absent_days": 0,
        "total_payable": 0,
    }

    for row in attendance_rows:
        if row.status == "Present":
            summary["present_days"] += 1
        elif row.status == "Half Day":
            summary["half_days"] += 1
        elif row.status == "Absent":
            summary["absent_days"] += 1

        summary["total_payable"] += float(row.payable_amount or 0)

    operator = frappe.db.get_value(
        "Operator",
        operator_name,
        ["full_name", "current_project", "current_factory", "assignment_status"],
        as_dict=True,
    )

    pending_discrepancies = frappe.db.count(
        "Attendance Discrepancy",
        {"operator": operator_name, "resolution_status": "Pending"},
    )

    return {
        "operator": operator,
        "summary": summary,
        "pending_discrepancies": pending_discrepancies,
        "recent_attendance": attendance_rows[:10],
    }
