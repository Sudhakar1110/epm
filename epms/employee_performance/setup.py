import frappe
from frappe import _
import json
import random
import string


def _rand_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=10))


def before_migrate():
    """Ensure Module Def exists before migration."""
    create_module_def()
    frappe.db.commit()


def after_install():
    """Run after app installation."""
    create_module_def()
    ensure_workspace_exists()
    create_roles()
    setup_role_permissions()
    frappe.db.commit()


def after_migrate():
    """Run after migration."""
    create_module_def()
    ensure_workspace_exists()
    frappe.db.commit()


def fix_workspace_now():
    """Run: bench --site epms.ogascale.com execute epms.employee_performance.setup.fix_workspace_now"""
    print("\n=== EPMS Workspace Fix ===")

    # Step 1: Ensure Module Def exists
    create_module_def()
    frappe.db.commit()

    # Step 2: Delete existing broken workspace
    ws_name = "Employee Performance Management"
    frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", ws_name)
    frappe.db.commit()
    print("Cleaned existing workspace data.")

    # Step 3: Create workspace via ORM using label (not title!)
    print("\n1. Creating workspace...")
    try:
        ws = frappe.get_doc({
            "doctype": "Workspace",
            "module": "Employee Performance",
            "label": ws_name,
        })
        ws.insert(ignore_permissions=True)
        frappe.db.commit()
        ws_name = ws.name
        print(f"   Created: {ws_name}")
    except Exception as e:
        print(f"   ORM failed: {e}")
        # SQL fallback with only columns that exist
        cols = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`", as_list=True)
        col_names = [c[0] for c in cols]
        insert_cols = {
            "name": ws_name,
            "module": "Employee Performance",
            "label": ws_name,
            "is_hidden": 0,
            "public": 1,
            "docstatus": 0,
            "idx": 0,
            "modified_by": "Administrator",
            "owner": "Administrator",
        }
        filtered = {k: v for k, v in insert_cols.items() if k in col_names}
        cols_str = ", ".join([f"`{k}`" for k in filtered.keys()])
        vals_str = ", ".join(["%s"] * len(filtered))
        frappe.db.sql(
            f"INSERT INTO `tabWorkspace` ({cols_str}) VALUES ({vals_str})",
            list(filtered.values()),
        )
        frappe.db.commit()
        print(f"   Created via SQL: {ws_name}")

    # Step 4: Set content JSON with card blocks
    print("\n2. Setting content with shortcuts and card sections...")
    content = _get_workspace_content()
    frappe.db.set_value("Workspace", ws_name, "content", content)
    frappe.db.commit()

    # Step 5: Add links via ORM
    print("\n3. Adding links via ORM...")
    try:
        ws = frappe.get_doc("Workspace", ws_name)

        links_data = [
            {"link_type": "DocType", "link_to": "Team", "label": "Teams", "onboard": 1, "type": "Link"},
            {"link_type": "DocType", "link_to": "Team Member Mapping", "label": "Team Members", "onboard": 1, "type": "Link"},
            {"link_type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance", "onboard": 1, "type": "Link"},
            {"link_type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks", "onboard": 1, "type": "Link"},
            {"link_type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards", "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Daily Performance Report", "label": "Daily Performance Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Monthly Performance Report", "label": "Monthly Performance Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Employee Wise Report", "label": "Employee Wise Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Team Wise Report", "label": "Team Wise Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Pending Task Report", "label": "Pending Task Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Top Performers", "label": "Top Performers", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Low Performers", "label": "Low Performers", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Monthly KPI Report", "label": "Monthly KPI Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Leaderboard Report", "label": "Leaderboard Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
        ]
        for link in links_data:
            ws.append("links", link)

        # Step 6: Add shortcuts via ORM
        print("4. Adding shortcuts via ORM...")
        shortcuts_data = [
            {"link_to": "Team", "type": "DocType", "label": "Team"},
            {"link_to": "Team Member Mapping", "type": "DocType", "label": "Team Member Mapping"},
            {"link_to": "Daily Performance", "type": "DocType", "label": "Daily Performance"},
            {"link_to": "Pending Task", "type": "DocType", "label": "Pending Task"},
            {"link_to": "Performance Scorecard", "type": "DocType", "label": "Performance Scorecard"},
        ]
        for sc in shortcuts_data:
            ws.append("shortcuts", sc)

        ws.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()
        print("   Saved workspace with links and shortcuts.")
    except Exception as e:
        print(f"   ORM append failed: {e}")
        frappe.log_error(f"EPMS: {str(e)}")

    # Step 7: Verify
    print("\n5. Verification:")
    link_count = frappe.db.count("Workspace Link", {"parent": ws_name})
    sc_count = frappe.db.count("Workspace Shortcut", {"parent": ws_name})
    print(f"   Links: {link_count}, Shortcuts: {sc_count}")
    print(f"   URL: /app/employee-performance-management")
    print("=== Done ===")


def _get_workspace_content():
    """Content matching Frappe v15 format with shortcuts AND card blocks for links."""
    content = [
        # Shortcuts section
        {"id": _rand_id(), "type": "header", "data": {"text": "<span class=\"h4\"><b>Your Shortcuts</b></span>", "col": 12}},
        {"id": _rand_id(), "type": "shortcut", "data": {"shortcut_name": "Team", "col": 3}},
        {"id": _rand_id(), "type": "shortcut", "data": {"shortcut_name": "Team Member Mapping", "col": 3}},
        {"id": _rand_id(), "type": "shortcut", "data": {"shortcut_name": "Daily Performance", "col": 3}},
        {"id": _rand_id(), "type": "shortcut", "data": {"shortcut_name": "Pending Task", "col": 3}},
        {"id": _rand_id(), "type": "shortcut", "data": {"shortcut_name": "Performance Scorecard", "col": 3}},
        # Spacer
        {"id": _rand_id(), "type": "spacer", "data": {"col": 12}},
        # Reports & Masters section with cards
        {"id": _rand_id(), "type": "header", "data": {"text": "<span class=\"h4\"><b>Reports &amp; Masters</b></span>", "col": 12}},
        {"id": _rand_id(), "type": "card", "data": {"card_name": "Employee Performance", "col": 4}},
    ]
    return json.dumps(content)


def ensure_workspace_exists():
    """Create workspace if it doesn't exist."""
    if frappe.db.exists("Workspace", "Employee Performance Management"):
        # Check if it has links, if not populate it
        link_count = frappe.db.count("Workspace Link", {"parent": "Employee Performance Management"})
        if link_count == 0:
            _populate_workspace("Employee Performance Management")
        return

    ws_name = "Employee Performance Management"
    create_module_def()

    # Try ORM first with label (not title!)
    try:
        ws = frappe.get_doc({
            "doctype": "Workspace",
            "module": "Employee Performance",
            "label": ws_name,
        })
        ws.insert(ignore_permissions=True)
        frappe.db.commit()
        ws_name = ws.name
    except Exception:
        # SQL fallback
        try:
            cols = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`", as_list=True)
            col_names = [c[0] for c in cols]
            insert_cols = {
                "name": ws_name,
                "module": "Employee Performance",
                "label": ws_name,
                "is_hidden": 0,
                "public": 1,
                "docstatus": 0,
                "idx": 0,
                "modified_by": "Administrator",
                "owner": "Administrator",
            }
            filtered = {k: v for k, v in insert_cols.items() if k in col_names}
            cols_str = ", ".join([f"`{k}`" for k in filtered.keys()])
            vals_str = ", ".join(["%s"] * len(filtered))
            frappe.db.sql(
                f"INSERT INTO `tabWorkspace` ({cols_str}) VALUES ({vals_str})",
                list(filtered.values()),
            )
            frappe.db.commit()
        except Exception:
            return

    _populate_workspace(ws_name)


def _populate_workspace(ws_name):
    """Add links and shortcuts to workspace via ORM."""
    try:
        ws = frappe.get_doc("Workspace", ws_name)
        ws.content = _get_workspace_content()

        for link in [
            {"link_type": "DocType", "link_to": "Team", "label": "Teams", "onboard": 1, "type": "Link"},
            {"link_type": "DocType", "link_to": "Team Member Mapping", "label": "Team Members", "onboard": 1, "type": "Link"},
            {"link_type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance", "onboard": 1, "type": "Link"},
            {"link_type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks", "onboard": 1, "type": "Link"},
            {"link_type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards", "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Daily Performance Report", "label": "Daily Performance Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Monthly Performance Report", "label": "Monthly Performance Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Employee Wise Report", "label": "Employee Wise Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Team Wise Report", "label": "Team Wise Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Pending Task Report", "label": "Pending Task Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Top Performers", "label": "Top Performers", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Low Performers", "label": "Low Performers", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Monthly KPI Report", "label": "Monthly KPI Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
            {"link_type": "Report", "link_to": "Leaderboard Report", "label": "Leaderboard Report", "is_query_report": 1, "onboard": 1, "type": "Link"},
        ]:
            ws.append("links", link)

        for sc in [
            {"link_to": "Team", "type": "DocType", "label": "Team"},
            {"link_to": "Team Member Mapping", "type": "DocType", "label": "Team Member Mapping"},
            {"link_to": "Daily Performance", "type": "DocType", "label": "Daily Performance"},
            {"link_to": "Pending Task", "type": "DocType", "label": "Pending Task"},
            {"link_to": "Performance Scorecard", "type": "DocType", "label": "Performance Scorecard"},
        ]:
            ws.append("shortcuts", sc)

        ws.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()
    except Exception as e:
        frappe.log_error(f"EPMS: Failed to populate workspace: {str(e)}")


def create_module_def():
    if not frappe.db.exists("Module Def", "Employee Performance"):
        try:
            frappe.get_doc({
                "doctype": "Module Def",
                "module_name": "Employee Performance",
                "app_name": "epms",
                "label": "Employee Performance",
                "color": "#28a745",
                "icon": "octicon octicon-goal",
                "description": "Employee Performance Management System",
                "type": "Module",
                "custom": 0,
            }).insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"EPMS: Failed to create Module Def: {str(e)}")


def create_roles():
    for rd in [
        {"role_name": "EPMS Founder", "desk_access": 1, "is_custom": 1},
        {"role_name": "EPMS Team Leader", "desk_access": 1, "is_custom": 1},
        {"role_name": "EPMS Team Member", "desk_access": 1, "is_custom": 1},
    ]:
        if not frappe.db.exists("Role", rd["role_name"]):
            frappe.get_doc({"doctype": "Role", **rd}).insert(ignore_permissions=True)


def setup_role_permissions():
    permissions = {
        "Team": {"EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1}, "EPMS Team Leader": {"read": 1}, "EPMS Team Member": {"read": 1}},
        "Team Member Mapping": {"EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1}, "EPMS Team Leader": {"read": 1, "write": 1, "create": 1}, "EPMS Team Member": {"read": 1}},
        "Daily Performance": {"EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1}, "EPMS Team Leader": {"read": 1, "write": 1, "create": 1, "cancel": 1, "submit": 1}, "EPMS Team Member": {"read": 1}},
        "Pending Task": {"EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1}, "EPMS Team Leader": {"read": 1, "write": 1, "create": 1, "submit": 1}, "EPMS Team Member": {"read": 1}},
        "Performance Scorecard": {"EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1}, "EPMS Team Leader": {"read": 1}, "EPMS Team Member": {"read": 1}},
    }
    for dt, roles in permissions.items():
        for role, perms in roles.items():
            if not frappe.db.exists("Custom DocPerm", {"parent": dt, "role": role}):
                try:
                    frappe.get_doc({"doctype": "Custom DocPerm", "parent": dt, "parenttype": "DocType", "parentfield": "permissions", "role": role, **perms}).insert(ignore_permissions=True)
                except Exception:
                    pass
