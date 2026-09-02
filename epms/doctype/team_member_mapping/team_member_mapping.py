import frappe
from frappe import _
from frappe.model.document import Document


class TeamMemberMapping(Document):
    def validate(self):
        self.validate_team_exists()
        self.validate_employee_user()
        self.validate_duplicate()
        self.validate_team_leader_role()

    def validate_team_exists(self):
        """Validate team exists and is active."""
        if self.team:
            team = frappe.get_doc("Team", self.team)
            if team.status != "Active":
                frappe.throw(_("Cannot add member to inactive team"))

    def validate_employee_user(self):
        """Validate employee has a linked user."""
        if self.employee and not self.user:
            employee = frappe.get_doc("Employee", self.employee)
            if employee.user_id:
                self.user = employee.user_id
            else:
                frappe.throw(
                    _("Employee {0} does not have a linked user account").format(
                        self.employee
                    )
                )

    def validate_duplicate(self):
        """Check for duplicate employee-team mapping."""
        existing = frappe.db.exists(
            "Team Member Mapping",
            {
                "employee": self.employee,
                "team": self.team,
                "status": "Active",
                "name": ["!=", self.name],
            },
        )
        if existing:
            frappe.throw(
                _("Employee {0} is already mapped to team {1}").format(
                    self.employee, self.team
                )
            )

    def validate_team_leader_role(self):
        """Validate user has team member role."""
        if self.user:
            user_roles = frappe.get_roles(self.user)
            if "EPMS Team Member" not in user_roles and "EPMS Team Leader" not in user_roles:
                frappe.get_doc("User", self.user).add_roles("EPMS Team Member")

    def on_update(self):
        """On mapping update."""
        self.update_team_member_count()
        self.create_timeline_entry("Team Member Mapping Updated")

    def on_trash(self):
        """On mapping delete."""
        self.update_team_member_count()

    def update_team_member_count(self):
        """Update team member count."""
        if self.team:
            team = frappe.get_doc("Team", self.team)
            team.update_member_count()
            team.db_update()

    def create_timeline_entry(self, action):
        """Create timeline entry."""
        frappe.get_doc(
            {
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": "Team Member Mapping",
                "reference_name": self.name,
                "content": action,
            }
        ).insert(ignore_permissions=True)


def has_permission(doc, user):
    """Custom permission check for Team Member Mapping."""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    # Founder has full access
    if "EPMS Founder" in user_roles:
        return True

    # Team leader can manage their team members
    if "EPMS Team Leader" in user_roles:
        team = frappe.db.get_value("Team", {"team_leader": user}, "name")
        return doc.team == team

    # Team member can only see their own mapping
    if "EPMS Team Member" in user_roles:
        return doc.user == user

    return False


def on_update(doc, method):
    """On Team Member Mapping update."""
    if doc.team:
        team_member_count = frappe.db.count(
            "Team Member Mapping",
            filters={"team": doc.team, "status": "Active"},
        )
        frappe.db.set_value("Team", doc.team, "total_members", team_member_count)
