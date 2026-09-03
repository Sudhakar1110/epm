import frappe
from frappe import _
import os
import json
import random
import string


def _rand_id():
    """Generate random ID like Frappe workspace uses."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=10))


def before_migrate():
    """Run before migration to ensure Module Def exists."""
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
    """Run from bench to force-create the workspace with full content.

    bench --site epms.ogascale.com execute epms.employee_performance.setup.fix_workspace_now
    """
    print("\n=== EPMS Workspace Fix ===")

    # Check for workspace-related child tables
    tables = frappe.db.sql(
        "SHOW TABLES LIKE '%Workspace%'",
    )
    print(f"\n1. Workspace-related tables: {[t[0] for t in tables]}")

    # Check Home workspace links (child table)
    home_links = frappe.db.sql(
        "SELECT * FROM `tabWorkspace Link` WHERE parent = 'Home' LIMIT 5",
        as_dict=True,
    )
    if home_links:
        print(f"\n2. Home workspace links (sample):")
        for link in home_links:
            print(f"   - type={link.get('type')}, link_type={link.get('link_type')}, link_to={link.get('link_to')}, label={link.get('label')}, parenttype={link.get('parenttype')}")
    else:
        print("\n2. No links in 'tabWorkspace Link' for Home")

    # Check Home shortcuts
    home_shortcuts = frappe.db.sql(
        "SELECT * FROM `tabWorkspace Shortcut` WHERE parent = 'Home' LIMIT 5",
        as_dict=True,
    )
    if home_shortcuts:
        print(f"\n3. Home workspace shortcuts (sample):")
        for s in home_shortcuts:
            print(f"   - link_to={s.get('link_to')}, type={s.get('type')}, label={s.get('label')}")
    else:
        print("\n3. No shortcuts in 'tabWorkspace Shortcut' for Home")

    # Delete existing workspace and recreate
    frappe.db.sql(
        "DELETE FROM `tabWorkspace Link` WHERE parent = %s",
        "Employee Performance Management",
    )
    frappe.db.sql(
        "DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s",
        "Employee Performance Management",
    )
    frappe.db.sql(
        "DELETE FROM `tabWorkspace` WHERE name = %s",
        "Employee Performance Management",
    )
    frappe.db.commit()

    ensure_workspace_exists()

    final = frappe.db.exists("Workspace", "Employee Performance Management")
    print(f"\n4. Workspace exists: {final}")
    if final:
        ws = frappe.get_doc("Workspace", "Employee Performance Management")
        content_len = len(ws.content) if ws.content else 0
        print(f"   Content length: {content_len} chars")
        link_count = frappe.db.count("Workspace Link", {"parent": "Employee Performance Management"})
        print(f"   Links in child table: {link_count}")
        shortcut_count = frappe.db.count("Workspace Shortcut", {"parent": "Employee Performance Management"})
        print(f"   Shortcuts in child table: {shortcut_count}")
        print(f"   URL: /app/employee-performance-management")
    print("=== Done ===")


def _get_workspace_content():
    """Build workspace content JSON matching Frappe v15 format exactly."""
    content = [
        {"id": _rand_id(), "type": "header", "data": {"text": "<span class=\"h4\"><b>Employee Performance</b></span>", "col": 12}},
        {"id": _rand_id(), "type": "shortcut", "data": {"shortcut_name": "Team", "col": 3}},
        {"id": _rand_id(), "type": "shortcut", "data": {"shortcut_name": "Team Member Mapping", "col": 3}},
        {"id": _rand_id(), "type": "shortcut", "data": {"shortcut_name": "Daily Performance", "col": 3}},
        {"id": _rand_id(), "type": "shortcut", "data": {"shortcut_name": "Pending Task", "col": 3}},
        {"id": _rand_id(), "type": "shortcut", "data": {"shortcut_name": "Performance Scorecard", "col": 3}},
        {"id": _rand_id(), "type": "spacer", "data": {"col": 12}},
        {"id": _rand_id(), "type": "header", "data": {"text": "<span class=\"h4\"><b>DocTypes &amp; Reports</b></span>", "col": 12}},
        {"id": _rand_id(), "type": "card", "data": {"card_name": "DocTypes", "col": 6}},
        {"id": _rand_id(), "type": "card", "data": {"card_name": "Reports", "col": 6}},
    ]
    return json.dumps(content)


def _get_workspace_links():
    """Build links for the workspace child table."""
    links = [
        # DocTypes card
        {"type": "Link", "link_type": "DocType", "link_to": "Team", "label": "Teams", "onboard": 1, "dependencies": "", "description": "Manage Teams"},
        {"type": "Link", "link_type": "DocType", "link_to": "Team Member Mapping", "label": "Team Members", "onboard": 1, "dependencies": "", "description": "Manage Team Members"},
        {"type": "Link", "link_type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance", "onboard": 1, "dependencies": "", "description": "Log Daily Performance"},
        {"type": "Link", "link_type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks", "onboard": 1, "dependencies": "", "description": "View Pending Tasks"},
        {"type": "Link", "link_type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards", "onboard": 1, "dependencies": "", "description": "View Performance Scorecards"},
        # Reports card
        {"type": "Link", "link_type": "Report", "link_to": "Daily Performance Report", "label": "Daily Performance Report", "is_query_report": 1, "onboard": 1, "dependencies": "", "description": ""},
        {"type": "Link", "link_type": "Report", "link_to": "Monthly Performance Report", "label": "Monthly Performance Report", "is_query_report": 1, "onboard": 1, "dependencies": "", "description": ""},
        {"type": "Link", "link_type": "Report", "link_to": "Employee Wise Report", "label": "Employee Wise Report", "is_query_report": 1, "onboard": 1, "dependencies": "", "description": ""},
        {"type": "Link", "link_type": "Report", "link_to": "Team Wise Report", "label": "Team Wise Report", "is_query_report": 1, "onboard": 1, "dependencies": "", "description": ""},
        {"type": "Link", "link_type": "Report", "link_to": "Pending Task Report", "label": "Pending Task Report", "is_query_report": 1, "onboard": 1, "dependencies": "", "description": ""},
        {"type": "Link", "link_type": "Report", "link_to": "Top Performers", "label": "Top Performers", "is_query_report": 1, "onboard": 1, "dependencies": "", "description": ""},
        {"type": "Link", "link_type": "Report", "link_to": "Low Performers", "label": "Low Performers", "is_query_report": 1, "onboard": 1, "dependencies": "", "description": ""},
        {"type": "Link", "link_type": "Report", "link_to": "Monthly KPI Report", "label": "Monthly KPI Report", "is_query_report": 1, "onboard": 1, "dependencies": "", "description": ""},
        {"type": "Link", "link_type": "Report", "link_to": "Leaderboard Report", "label": "Leaderboard Report", "is_query_report": 1, "onboard": 1, "dependencies": "", "description": ""},
    ]
    return links


def _get_workspace_shortcuts():
    """Build shortcuts for the workspace child table."""
    return [
        {"type": "DocType", "link_to": "Team", "label": "Team", "color": "#28a745"},
        {"type": "DocType", "link_to": "Team Member Mapping", "label": "Team Member Mapping", "color": "#28a745"},
        {"type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance", "color": "#28a745"},
        {"type": "DocType", "link_to": "Pending Task", "label": "Pending Task", "color": "#28a745"},
        {"type": "DocType", "link_to": "Performance Scorecard", "label": "Performance Scorecard", "color": "#28a745"},
    ]


def _build_workspace_row():
    """Build workspace data dict using only columns that exist."""
    columns = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`", as_dict=True)
    col_names = [c.Field for c in columns]

    data = {
        "name": "Employee Performance Management",
        "label": "Employee Performance Management",
        "title": "Employee Performance Management",
        "module": "Employee Performance",
        "icon": "octicon octicon-goal",
        "indicator_color": "green",
        "is_hidden": 0,
        "public": 1,
        "for_user": "",
        "modified_by": "Administrator",
        "owner": "Administrator",
        "creation": "2024-01-01 00:00:00.000000",
        "modified": "2024-01-01 00:00:00.000000",
        "content": _get_workspace_content(),
        "sequence_id": 1,
        "parent_page": "",
        "hide_custom": 0,
        "restrict_to_domain": "",
        "docstatus": 0,
        "idx": 0,
    }
    return {k: v for k, v in data.items() if k in col_names}


def ensure_workspace_exists():
    """Create workspace with full content and child tables."""
    if frappe.db.exists("Workspace", "Employee Performance Management"):
        return

    # Insert main workspace row
    data = _build_workspace_row()
    cols = ", ".join([f"`{k}`" for k in data.keys()])
    placeholders = ", ".join(["%s"] * len(data))
    vals = list(data.values())

    try:
        frappe.db.sql(
            f"INSERT INTO `tabWorkspace` ({cols}) VALUES ({placeholders})",
            vals,
        )
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"EPMS: Failed to create workspace row: {str(e)}")
        return

    # Insert links into child table
    ws_name = "Employee Performance Management"
    link_columns = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Link`", as_dict=True)
    link_col_names = [c.Field for c in link_columns] if link_columns else []

    if link_col_names:
        for idx, link in enumerate(_get_workspace_links(), 1):
            link_data = {
                "parent": ws_name,
                "parenttype": "Workspace",
                "parentfield": "links",
                "idx": idx,
                **link,
            }
            link_data = {k: v for k, v in link_data.items() if k in link_col_names}
            lcols = ", ".join([f"`{k}`" for k in link_data.keys()])
            lph = ", ".join(["%s"] * len(link_data))
            try:
                frappe.db.sql(
                    f"INSERT INTO `tabWorkspace Link` ({lcols}) VALUES ({lph})",
                    list(link_data.values()),
                )
            except Exception as e:
                frappe.log_error(f"EPMS: Failed to insert link: {str(e)}")

    # Insert shortcuts into child table
    shortcut_columns = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Shortcut`", as_dict=True)
    shortcut_col_names = [c.Field for c in shortcut_columns] if shortcut_columns else []

    if shortcut_col_names:
        for idx, sc in enumerate(_get_workspace_shortcuts(), 1):
            sc_data = {
                "parent": ws_name,
                "parenttype": "Workspace",
                "parentfield": "shortcuts",
                "idx": idx,
                **sc,
            }
            sc_data = {k: v for k, v in sc_data.items() if k in shortcut_col_names}
            scols = ", ".join([f"`{k}`" for k in sc_data.keys()])
            sph = ", ".join(["%s"] * len(sc_data))
            try:
                frappe.db.sql(
                    f"INSERT INTO `tabWorkspace Shortcut` ({scols}) VALUES ({sph})",
                    list(sc_data.values()),
                )
            except Exception as e:
                frappe.log_error(f"EPMS: Failed to insert shortcut: {str(e)}")

    frappe.db.commit()
    frappe.logger().info("EPMS: Created workspace with links and shortcuts")


def create_module_def():
    """Ensure the Employee Performance Module Def exists."""
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
    """Create EPMS roles."""
    roles = [
        {"role_name": "EPMS Founder", "desk_access": 1, "is_custom": 1},
        {"role_name": "EPMS Team Leader", "desk_access": 1, "is_custom": 1},
        {"role_name": "EPMS Team Member", "desk_access": 1, "is_custom": 1},
    ]
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            frappe.get_doc({"doctype": "Role", **role_data}).insert(ignore_permissions=True)


def setup_role_permissions():
    """Setup role permissions for EPMS doctypes."""
    permissions = {
        "Team": {
            "EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1},
            "EPMS Team Leader": {"read": 1},
            "EPMS Team Member": {"read": 1},
        },
        "Team Member Mapping": {
            "EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1},
            "EPMS Team Leader": {"read": 1, "write": 1, "create": 1},
            "EPMS Team Member": {"read": 1},
        },
        "Daily Performance": {
            "EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
            "EPMS Team Leader": {"read": 1, "write": 1, "create": 1, "cancel": 1, "submit": 1},
            "EPMS Team Member": {"read": 1},
        },
        "Pending Task": {
            "EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
            "EPMS Team Leader": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "EPMS Team Member": {"read": 1},
        },
        "Performance Scorecard": {
            "EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
            "EPMS Team Leader": {"read": 1},
            "EPMS Team Member": {"read": 1},
        },
    }
    for doctype, roles in permissions.items():
        for role, perms in roles.items():
            if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role}):
                try:
                    frappe.get_doc({
                        "doctype": "Custom DocPerm",
                        "parent": doctype,
                        "parenttype": "DocType",
                        "parentfield": "permissions",
                        "role": role,
                        **perms,
                    }).insert(ignore_permissions=True)
                except Exception:
                    pass
