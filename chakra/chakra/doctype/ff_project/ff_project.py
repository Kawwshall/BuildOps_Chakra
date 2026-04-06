import frappe
from frappe.model.document import Document


class FFProject(Document):
    def validate(self):
        self.capture_existing_state()
        self.validate_dates()
        self.validate_chiefs()
        self.sync_roster()

    def on_update(self):
        self.reconcile_operator_assignments()

    def on_trash(self):
        self.free_operators(self.get_roster_operators())

    def capture_existing_state(self):
        self._previous_status = None
        self._previous_roster = set()

        if not self.is_new():
            previous_doc = frappe.get_doc(self.doctype, self.name)
            self._previous_status = previous_doc.status
            self._previous_roster = {
                row.operator for row in previous_doc.roster if row.operator
            }

    def validate_dates(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            frappe.throw("End Date cannot be earlier than Start Date.")

    def validate_chiefs(self):
        chiefs = [chief for chief in [self.chief_1, self.chief_2] if chief]

        if len(chiefs) != len(set(chiefs)):
            frappe.throw("Chief 1 and Chief 2 must be different operators.")

        for chief in chiefs:
            operator = self.get_operator_details(chief)

            if operator.role_type != "Chief":
                frappe.throw(f"Operator {operator.full_name} must have role 'Chief' to be selected as a project chief.")

            if operator.status != "Active":
                frappe.throw(f"Operator {operator.full_name} must be Active before being assigned to a project.")

    def sync_roster(self):
        seen_operators = set()

        for row in self.roster:
            if not row.operator:
                continue

            if row.operator in seen_operators:
                frappe.throw(f"Operator {row.operator} is added more than once in the roster.")

            seen_operators.add(row.operator)
            self.sync_roster_row(row)

        for chief in [self.chief_1, self.chief_2]:
            if chief:
                self.sync_chief_row(chief)

    def sync_roster_row(self, row):
        operator = self.get_operator_details(row.operator)

        if operator.status != "Active":
            frappe.throw(f"Operator {operator.full_name} must be Active before being assigned to a project.")

        if operator.role_type == "Regional Lead":
            frappe.throw(f"Operator {operator.full_name} cannot be added to the roster because Regional Leads are not rostered workers.")

        if operator.current_project and operator.current_project != self.name and operator.assignment_status == "Deployed":
            frappe.throw(
                f"Operator {operator.full_name} is already deployed on project {operator.current_project}. "
                "Free that operator first before moving them to another active project."
            )

        row.role_type = operator.role_type

        if not row.daily_rate:
            row.daily_rate = self.get_default_rate_for_role(row.role_type)

    def sync_chief_row(self, chief):
        existing_row = next((row for row in self.roster if row.operator == chief), None)

        if existing_row:
            existing_row.role_type = "Chief"
            existing_row.daily_rate = self.rate_chief or existing_row.daily_rate or 4000
            return

        self.append(
            "roster",
            {
                "operator": chief,
                "role_type": "Chief",
                "daily_rate": self.rate_chief or 4000,
            },
        )

    def reconcile_operator_assignments(self):
        previous_roster = getattr(self, "_previous_roster", set())
        current_roster = self.get_roster_operators()

        if self.status == "Active":
            removed_operators = previous_roster - current_roster
            self.free_operators(removed_operators)
            self.assign_operators(current_roster)
            return

        self.free_operators(previous_roster | current_roster)

    def assign_operators(self, operators):
        for operator_name in operators:
            if frappe.db.exists("Operator", operator_name):
                frappe.db.set_value(
                    "Operator",
                    operator_name,
                    {
                        "current_project": self.name,
                        "current_factory": self.factory_name,
                        "assignment_status": "Deployed",
                    },
                    update_modified=False,
                )

    def free_operators(self, operators):
        for operator_name in operators:
            if not frappe.db.exists("Operator", operator_name):
                continue

            if frappe.db.get_value("Operator", operator_name, "current_project") != self.name:
                continue

            frappe.db.set_value(
                "Operator",
                operator_name,
                {
                    "current_project": "",
                    "current_factory": "",
                    "assignment_status": "Available",
                },
                update_modified=False,
            )

    def get_roster_operators(self):
        return {row.operator for row in self.roster if row.operator}

    def get_default_rate_for_role(self, role_type):
        rate_map = {
            "Operator": self.rate_operator or 1200,
            "Captain": self.rate_captain or 1500,
            "Chief": self.rate_chief or 4000,
        }
        return rate_map.get(role_type, self.rate_operator or 1200)

    @staticmethod
    def get_operator_details(operator_name):
        operator = frappe.db.get_value(
            "Operator",
            operator_name,
            ["name", "full_name", "role_type", "status", "current_project", "assignment_status"],
            as_dict=True,
        )

        if not operator:
            frappe.throw(f"Operator {operator_name} does not exist.")

        return operator
