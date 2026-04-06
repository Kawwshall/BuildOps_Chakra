app_name = "chakra"
app_title = "Chakra"
app_publisher = "BuildOps"
app_description = "Factory Operations - Operator Management, Attendance & Payments"
app_email = "ops@buildops.in"
app_license = "MIT"
app_version = "1.0.0"

fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["FF Chief", "FF Captain", "FF Operator", "FF Vendor"]]]}
]

permission_query_conditions = {
    "Operator": "chakra.permissions.operator_query",
    "FF Attendance": "chakra.permissions.attendance_query",
    "Attendance Discrepancy": "chakra.permissions.discrepancy_query",
    "Vendor Invoice": "chakra.permissions.vendor_invoice_query",
}

has_permission = {
    "Operator": "chakra.permissions.operator_has_permission",
    "FF Attendance": "chakra.permissions.attendance_has_permission",
    "Attendance Discrepancy": "chakra.permissions.discrepancy_has_permission",
    "Vendor Invoice": "chakra.permissions.vendor_invoice_has_permission",
}
