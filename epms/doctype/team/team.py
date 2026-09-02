import frappe
from frappe import _
from frappe.model.document import Document


class Team(Document):
    def validate(self):
        self.validate_team_leader()
        self.update_member_count()

    def validate_team_leader(self):
        """Validate team leader has correct role."""
        if self.team_leader:
            user_roles = frappe.get_roles(self.team_leader)
            if "EPMS Team Leader" not in user_roles and "EPMS Founder" not in user_roles:
                frappe.throw(
                    _("User {0} must have EPMS Team Leader or EPMS Founder role").format(
                        self.team_leader
                    )
                )

    def update_member_count(self):
        """Update total members count."""
        self.total_members = frappe.db.count(
            "Team Member Mapping",
            filters={"team": self.name, "status": "Active"},
        )

    def on_update(self):
        """On team update."""
        self.update_member_count()
        self.create_timeline_entry("Team Updated")

    def on_trash(self):
        """On team delete."""
        # Check for active members
        members = frappe.get_all(
            "Team Member Mapping",
            filters={"team": self.name, "status": "Active"},
        )
        if members:
            frappe.throw(
                _("Cannot delete team with active members. Remove members first.")
            )

    def create_timeline_entry(self, action):
        """Create timeline entry."""
        frappe.get_doc(
            {
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": "Team",
                "reference_name": self.name,
                "content": action,
            }
        ).insert(ignore_permissions=True)


def has_permission(doc, user):
    """Custom permission check for Team."""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    # Founder has full access
    if "EPMS Founder" in user_roles:
        return True

    # Team leader can only see their teams
    if "EPMS Team Leader" in user_roles:
        return doc.team_leader == user

    # Team member can only read
    if "EPMS Team Member" in user_roles:
        # Check if member belongs to this team
        member = frappe.db.exists(
            "Team Member Mapping",
            {"user": user, "team": doc.name, "status": "Active"},
        )
        return bool(member)

    return False
