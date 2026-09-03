import frappe
from frappe import _
import os
import json
import random
import string


def _rand_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=10))


def before_migrate():
    create_module_def()
    frappe.db.commit()


def after_install():
    create_module_def()
    ensure_workspace_exists()
    create_roles()
    setup_role_permissions()
    frappe.db.commit()


def after_migrate():
    create_module_def()
    ensure_workspace_exists()
    frappe.db.commit()


def fix_workspace_now():
    """bench --site epms.ogascale.com execute epms.employee_performance.setup.fix_workspace_now"""
    print("\n=== EPMS Workspace Fix ===")

    # Show actual columns for child tables
    for tbl in ["tabWorkspace Link", "tabWorkspace Shortcut"]:
        cols = frappe.db.sql(f"SHOW COLUMNS FROM `{tbl}`", as_dict=True)
        print(f"\n{tbl} columns: {[c.Field for c in cols]}")

    # Show a full Home link row to see all fields
    home_link = frappe.db.sql(
        "SELECT * FROM `tabWorkspace Link` WHERE parent = 'Home' LIMIT 1",
        as_dict=True,
    )
    if home_link:
        print(f"\nHome link full row: {dict(home_link[0])}")

    home_sc = frappe.db.sql(
        "SELECT * FROM `tabWorkspace Shortcut` WHERE parent = 'Home' LIMIT 1",
        as_dict=True,
    )
    if home_sc:
        print(f"\nHome shortcut full row: {dict(home_sc[0])}")

    # Delete and recreate
    frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s", "Employee Performance Management")
    frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s", "Employee Performance Management")
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", "Employee Performance Management")
    frappe.db.commit()

    ensure_workspace_exists()

    final = frappe.db.exists("Workspace", "Employee Performance Management")
    print(f"\nFinal: Workspace exists = {final}")
    if final:
        link_count = frappe.db.count("Workspace Link", {"parent": "Employee Performance Management"})
        sc_count = frappe.db.count("Workspace Shortcut", {"parent": "Employee Performance Management"})
        print(f"Links: {link_count}, Shortcuts: {sc_count}")
        print(f"URL: /app/employee-performance-management")
    print("=== Done ===")


def _get_workspace_content():
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


def _insert_links(ws_name):
    """Insert links using only columns that exist."""
    link_cols_info = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Link`", as_dict=True)
    link_col_names = [c.Field for c in link_cols_info]
    print(f"\nUsing link columns: {link_col_names}")

    links = [
        {"link_type": "DocType", "link_to": "Team", "label": "Teams", "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "DocType", "link_to": "Team Member Mapping", "label": "Team Members", "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance", "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks", "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards", "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "Report", "link_to": "Daily Performance Report", "label": "Daily Performance Report", "is_query_report": 1, "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "Report", "link_to": "Monthly Performance Report", "label": "Monthly Performance Report", "is_query_report": 1, "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "Report", "link_to": "Employee Wise Report", "label": "Employee Wise Report", "is_query_report": 1, "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "Report", "link_to": "Team Wise Report", "label": "Team Wise Report", "is_query_report": 1, "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "Report", "link_to": "Pending Task Report", "label": "Pending Task Report", "is_query_report": 1, "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "Report", "link_to": "Top Performers", "label": "Top Performers", "is_query_report": 1, "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "Report", "link_to": "Low Performers", "label": "Low Performers", "is_query_report": 1, "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "Report", "link_to": "Monthly KPI Report", "label": "Monthly KPI Report", "is_query_report": 1, "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
        {"link_type": "Report", "link_to": "Leaderboard Report", "label": "Leaderboard Report", "is_query_report": 1, "onboard": 1, "type": "Link", "dependencies": "", "description": ""},
    ]

    count = 0
    for idx, link in enumerate(links, 1):
        row = {
            "name": _rand_id(),
            "parent": ws_name,
            "parenttype": "Workspace",
            "parentfield": "links",
            "docstatus": 0,
            "idx": idx,
            **link,
        }
        row = {k: v for k, v in row.items() if k in link_col_names}
        cols = ", ".join([f"`{k}`" for k in row.keys()])
        ph = ", ".join(["%s"] * len(row))
        try:
            frappe.db.sql(f"INSERT INTO `tabWorkspace Link` ({cols}) VALUES ({ph})", list(row.values()))
            count += 1
        except Exception as e:
            print(f"  Link insert error: {e}")
            frappe.log_error(f"EPMS link insert error: {str(e)}")

    print(f"Inserted {count}/{len(links)} links")
    return count


def _insert_shortcuts(ws_name):
    """Insert shortcuts using only columns that exist."""
    sc_cols_info = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Shortcut`", as_dict=True)
    sc_col_names = [c.Field for c in sc_cols_info]
    print(f"\nUsing shortcut columns: {sc_col_names}")

    shortcuts = [
        {"link_to": "Team", "type": "DocType", "label": "Team", "color": "#28a745"},
        {"link_to": "Team Member Mapping", "type": "DocType", "label": "Team Member Mapping", "color": "#28a745"},
        {"link_to": "Daily Performance", "type": "DocType", "label": "Daily Performance", "color": "#28a745"},
        {"link_to": "Pending Task", "type": "DocType", "label": "Pending Task", "color": "#28a745"},
        {"link_to": "Performance Scorecard", "type": "DocType", "label": "Performance Scorecard", "color": "#28a745"},
    ]

    count = 0
    for idx, sc in enumerate(shortcuts, 1):
        row = {
            "name": _rand_id(),
            "parent": ws_name,
            "parenttype": "Workspace",
            "parentfield": "shortcuts",
            "docstatus": 0,
            "idx": idx,
            **sc,
        }
        row = {k: v for k, v in row.items() if k in sc_col_names}
        cols = ", ".join([f"`{k}`" for k in row.keys()])
        ph = ", ".join(["%s"] * len(row))
        try:
            frappe.db.sql(f"INSERT INTO `tabWorkspace Shortcut` ({cols}) VALUES ({ph})", list(row.values()))
            count += 1
        except Exception as e:
            print(f"  Shortcut insert error: {e}")
            frappe.log_error(f"EPMS shortcut insert error: {str(e)}")

    print(f"Inserted {count}/{len(shortcuts)} shortcuts")
    return count


def _build_workspace_row():
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
    if frappe.db.exists("Workspace", "Employee Performance Management"):
        return

    ws_name = "Employee Performance Management"
    data = _build_workspace_row()
    cols = ", ".join([f"`{k}`" for k in data.keys()])
    placeholders = ", ".join(["%s"] * len(data))

    try:
        frappe.db.sql(f"INSERT INTO `tabWorkspace` ({cols}) VALUES ({placeholders})", list(data.values()))
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"EPMS: Failed to create workspace: {str(e)}")
        return

    _insert_links(ws_name)
    _insert_shortcuts(ws_name)
    frappe.db.commit()


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
