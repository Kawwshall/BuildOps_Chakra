import frappe


PRIVILEGED_ROLES = {"System Manager", "FF Chief"}


def get_operator_for_user(user=None):
    user = user or frappe.session.user

    if user in {"Guest", "Administrator"}:
        return None

    return frappe.db.get_value("Operator", {"user_id": user}, "name")


def user_is_privileged(user=None):
    user = user or frappe.session.user

    if user == "Administrator":
        return True

    return bool(PRIVILEGED_ROLES.intersection(set(frappe.get_roles(user))))


def operator_query(user):
    if user_is_privileged(user):
        return None

    if "FF Operator" in frappe.get_roles(user):
        return f"`tabOperator`.`user_id` = {frappe.db.escape(user)}"

    return None


def attendance_query(user):
    if user_is_privileged(user):
        return None

    operator = get_operator_for_user(user)
    if operator:
        return f"`tabFF Attendance`.`operator` = {frappe.db.escape(operator)}"

    return "1 = 0"


def discrepancy_query(user):
    if user_is_privileged(user):
        return None

    operator = get_operator_for_user(user)
    if operator:
        return f"`tabAttendance Discrepancy`.`operator` = {frappe.db.escape(operator)}"

    return "1 = 0"


def vendor_invoice_query(user):
    if user_is_privileged(user):
        return None

    if "FF Vendor" in frappe.get_roles(user):
        return f"`tabVendor Invoice`.`vendor_user` = {frappe.db.escape(user)}"

    return "1 = 0"


def operator_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user

    if user_is_privileged(user):
        return True

    if permission_type == "create" or not doc:
        return None

    if "FF Operator" in frappe.get_roles(user):
        return doc.user_id == user

    return None


def attendance_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user

    if user_is_privileged(user):
        return True

    if permission_type == "create" or not doc:
        return None

    operator = get_operator_for_user(user)
    if operator:
        return doc.operator == operator

    return False


def discrepancy_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user

    if user_is_privileged(user):
        return True

    if permission_type == "create" or not doc:
        return None

    operator = get_operator_for_user(user)
    if operator:
        return doc.operator == operator

    return False


def vendor_invoice_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user

    if user_is_privileged(user):
        return True

    if permission_type == "create" or not doc:
        return None

    if "FF Vendor" in frappe.get_roles(user):
        return doc.vendor_user == user

    return False
