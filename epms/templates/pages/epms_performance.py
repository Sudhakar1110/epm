no_cache = True
template = "templates/pages/epms/performance.html"

def get_context(context):
    context.no_cache = True
    context.title = "Performance"
    context.show_sidebar = False
    context.user_name = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user
    context.user_type = frappe.db.get_value("User", frappe.session.user, "user_type") or "User"
    context.active_page = "performance"
