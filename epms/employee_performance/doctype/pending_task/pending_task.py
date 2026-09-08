import frappe
from frappe import _
from frappe.model.document import Document


class PendingTask(Document):
    def validate(self):
        if not self.assigned_date:
            self.assigned_date = frappe.utils.nowdate()
        if self.current_status == "Completed" and not self.completion_date:
            self.completion_date = frappe.utils.nowdate()

    def on_submit(self):
        self.create_timeline_entry("Task Created")

    def on_cancel(self):
        self.create_timeline_entry("Task Cancelled")

    def create_timeline_entry(self, action):
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "Pending Task",
            "reference_name": self.name,
            "content": action,
        }).insert(ignore_permissions=True)


def has_permission(doc, user):
    """Data-level permission: Founder sees all, Leader sees own team, Member sees own tasks."""
    user_roles = frappe.get_roles(user)
    if "EPMS Founder" in user_roles:
        return True
    if "EPMS Team Leader" in user_roles:
        team = frappe.db.get_value("Team", {"team_leader": user}, "name")
        if team:
            team_members = frappe.get_all(
                "Team Member Mapping",
                filters={"team": team, "status": "Active"},
                pluck="user",
            )
            if doc.employee in team_members or doc.employee == user:
                return True
    if doc.employee == user:
        return True
    return False
