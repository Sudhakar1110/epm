import frappe
from frappe import _
from datetime import date


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"))

    user = frappe.get_doc("User", frappe.session.user)
    context.user_name = user.full_name or frappe.session.user
    context.user_initial = (context.user_name[0] or "U").upper()
    context.user_role = "Team Member"
    roles = frappe.get_roles(frappe.session.user)
    if "Employee Performance Founder" in roles:
        context.user_role = "Founder"
    elif "Employee Performance Team Leader" in roles:
        context.user_role = "Team Leader"

    context.current_month = date.today().strftime("%Y-%m")

    scorecards = frappe.get_all(
        "Performance Scorecard",
        fields=["name", "employee_name", "team", "month", "total_score", "grade", "status", "department"],
        order_by="month desc, total_score desc",
    )

    context.scorecards = []
    for s in scorecards:
        s["grade_class"] = "gray"
        if s.get("grade") == "A":
            s["grade_class"] = "green"
        elif s.get("grade") == "B":
            s["grade_class"] = "blue"
        elif s.get("grade") == "C":
            s["grade_class"] = "orange"
        elif s.get("grade") == "D":
            s["grade_class"] = "red"
        context.scorecards.append(s)

    context.total_scorecards = len(context.scorecards)
    scores = [s.total_score for s in context.scorecards if s.total_score]
    context.avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    context.top_score = max(scores) if scores else 0
    context.low_score = min(scores) if scores else 0

    context.active_page = "performance"
    context.no_cache = 1
