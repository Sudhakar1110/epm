import frappe
from frappe import _
import json
import random
import string


def _rand_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=10))


def before_migrate():
    """Ensure Module Def exists before migration."""
    try:
        create_module_def()
        frappe.db.commit()
    except Exception:
        pass


def after_install():
    """Run after app installation."""
    try:
        create_module_def()
        ensure_workspace_exists()
        create_roles()
        setup_role_permissions()
        frappe.db.commit()
    except Exception:
        pass


def after_migrate():
    """Run after migration."""
    try:
        create_module_def()
        ensure_workspace_exists()
        frappe.db.commit()
    except Exception:
        pass


def fix_workspace_now():
    """Run: bench --site epms.ogascale.com execute epms.employee_performance.setup.fix_workspace_now"""
    print("\n=== EPMS Workspace Fix ===")

    # Step 1: Ensure Module Def exists
    create_module_def()
    frappe.db.commit()

    # Step 2: Clean existing workspace
    ws_name = "Employee Performance Management"
    frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", ws_name)
    frappe.db.commit()
    print("Cleaned existing workspace data.")

    # Step 3: Create workspace via SQL (ORM keeps failing)
    print("\n1. Creating workspace via SQL...")
    cols = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`", as_list=True)
    col_names = [c[0] for c in cols]
    print(f"   Available columns: {col_names}")

    insert_cols = {
        "name": ws_name,
        "module": "Employee Performance",
        "label": ws_name,
        "content": _get_workspace_content(),
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

    try:
        frappe.db.sql(
            f"INSERT INTO `tabWorkspace` ({cols_str}) VALUES ({vals_str})",
            list(filtered.values()),
        )
        frappe.db.commit()
        print(f"   Created workspace: {ws_name}")
    except Exception as e:
        print(f"   SQL INSERT failed: {e}")
        return

    # Step 4: Insert links via SQL
    print("\n2. Inserting links...")
    link_cols_map = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Link`", as_list=True)
    link_col_names = [c[0] for c in link_cols_map]
    print(f"   Link columns: {link_col_names}")

    links_data = [
        {"link_type": "DocType", "link_to": "Team", "label": "Teams", "onboard": 1, "type": "Link", "idx": 1},
        {"link_type": "DocType", "link_to": "Team Member Mapping", "label": "Team Members", "onboard": 1, "type": "Link", "idx": 2},
        {"link_type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance", "onboard": 1, "type": "Link", "idx": 3},
        {"link_type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks", "onboard": 1, "type": "Link", "idx": 4},
        {"link_type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards", "onboard": 1, "type": "Link", "idx": 5},
        {"link_type": "Report", "link_to": "Daily Performance Report", "label": "Daily Performance Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 6},
        {"link_type": "Report", "link_to": "Monthly Performance Report", "label": "Monthly Performance Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 7},
        {"link_type": "Report", "link_to": "Employee Wise Report", "label": "Employee Wise Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 8},
        {"link_type": "Report", "link_to": "Team Wise Report", "label": "Team Wise Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 9},
        {"link_type": "Report", "link_to": "Pending Task Report", "label": "Pending Task Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 10},
        {"link_type": "Report", "link_to": "Top Performers", "label": "Top Performers", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 11},
        {"link_type": "Report", "link_to": "Low Performers", "label": "Low Performers", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 12},
        {"link_type": "Report", "link_to": "Monthly KPI Report", "label": "Monthly KPI Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 13},
        {"link_type": "Report", "link_to": "Leaderboard Report", "label": "Leaderboard Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 14},
    ]

    inserted_links = 0
    for link in links_data:
        row = dict(link)
        row["name"] = _rand_id()
        row["parent"] = ws_name
        row["parentfield"] = "links"
        row["parenttype"] = "Workspace"
        row["docstatus"] = 0
        row["owner"] = "Administrator"
        row["modified_by"] = "Administrator"

        filtered_link = {k: v for k, v in row.items() if k in link_col_names}
        cols_str_l = ", ".join([f"`{k}`" for k in filtered_link.keys()])
        vals_str_l = ", ".join(["%s"] * len(filtered_link))
        try:
            frappe.db.sql(
                f"INSERT INTO `tabWorkspace Link` ({cols_str_l}) VALUES ({vals_str_l})",
                list(filtered_link.values()),
            )
            inserted_links += 1
        except Exception as e:
            print(f"   Link '{link['label']}' failed: {e}")

    frappe.db.commit()
    print(f"   Inserted {inserted_links}/{len(links_data)} links")

    # Step 5: Insert shortcuts via SQL
    print("\n3. Inserting shortcuts...")
    sc_cols_map = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Shortcut`", as_list=True)
    sc_col_names = [c[0] for c in sc_cols_map]
    print(f"   Shortcut columns: {sc_col_names}")

    shortcuts_data = [
        {"link_to": "Team", "type": "DocType", "label": "Team", "idx": 1},
        {"link_to": "Team Member Mapping", "type": "DocType", "label": "Team Member Mapping", "idx": 2},
        {"link_to": "Daily Performance", "type": "DocType", "label": "Daily Performance", "idx": 3},
        {"link_to": "Pending Task", "type": "DocType", "label": "Pending Task", "idx": 4},
        {"link_to": "Performance Scorecard", "type": "DocType", "label": "Performance Scorecard", "idx": 5},
    ]

    inserted_scs = 0
    for sc in shortcuts_data:
        row = dict(sc)
        row["name"] = _rand_id()
        row["parent"] = ws_name
        row["parentfield"] = "shortcuts"
        row["parenttype"] = "Workspace"
        row["docstatus"] = 0
        row["owner"] = "Administrator"
        row["modified_by"] = "Administrator"

        filtered_sc = {k: v for k, v in row.items() if k in sc_col_names}
        cols_str_s = ", ".join([f"`{k}`" for k in filtered_sc.keys()])
        vals_str_s = ", ".join(["%s"] * len(filtered_sc))
        try:
            frappe.db.sql(
                f"INSERT INTO `tabWorkspace Shortcut` ({cols_str_s}) VALUES ({vals_str_s})",
                list(filtered_sc.values()),
            )
            inserted_scs += 1
        except Exception as e:
            print(f"   Shortcut '{sc['label']}' failed: {e}")

    frappe.db.commit()
    frappe.clear_cache()
    print(f"   Inserted {inserted_scs}/{len(shortcuts_data)} shortcuts")

    # Step 6: Verify
    print("\n4. Verification:")
    final_links = frappe.db.count("Workspace Link", {"parent": ws_name})
    final_scs = frappe.db.count("Workspace Shortcut", {"parent": ws_name})
    ws_exists = frappe.db.exists("Workspace", ws_name)
    content_preview = frappe.db.get_value("Workspace", ws_name, "content")
    print(f"   Workspace exists: {ws_exists}")
    print(f"   Content length: {len(content_preview) if content_preview else 0} chars")
    print(f"   Links in DB: {final_links}")
    print(f"   Shortcuts in DB: {final_scs}")
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
    """Create workspace if it doesn't exist. SQL-only approach."""
    try:
        if frappe.db.exists("Workspace", "Employee Performance Management"):
            return
    except Exception:
        return

    ws_name = "Employee Performance Management"
    create_module_def()

    try:
        cols = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`", as_list=True)
        col_names = [c[0] for c in cols]
        insert_cols = {
            "name": ws_name,
            "module": "Employee Performance",
            "label": ws_name,
            "content": _get_workspace_content(),
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

        # Add shortcuts
        sc_cols_map = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Shortcut`", as_list=True)
        sc_col_names = [c[0] for c in sc_cols_map]

        for sc in [
            {"link_to": "Team", "type": "DocType", "label": "Team"},
            {"link_to": "Team Member Mapping", "type": "DocType", "label": "Team Member Mapping"},
            {"link_to": "Daily Performance", "type": "DocType", "label": "Daily Performance"},
            {"link_to": "Pending Task", "type": "DocType", "label": "Pending Task"},
            {"link_to": "Performance Scorecard", "type": "DocType", "label": "Performance Scorecard"},
        ]:
            row = dict(sc)
            row["name"] = _rand_id()
            row["parent"] = ws_name
            row["parentfield"] = "shortcuts"
            row["parenttype"] = "Workspace"
            row["docstatus"] = 0
            row["owner"] = "Administrator"
            row["modified_by"] = "Administrator"
            filtered_sc = {k: v for k, v in row.items() if k in sc_col_names}
            cols_str_s = ", ".join([f"`{k}`" for k in filtered_sc.keys()])
            vals_str_s = ", ".join(["%s"] * len(filtered_sc))
            frappe.db.sql(
                f"INSERT INTO `tabWorkspace Shortcut` ({cols_str_s}) VALUES ({vals_str_s})",
                list(filtered_sc.values()),
            )

        # Add links
        link_cols_map = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace Link`", as_list=True)
        link_col_names = [c[0] for c in link_cols_map]

        links_data = [
            {"link_type": "DocType", "link_to": "Team", "label": "Teams", "onboard": 1, "type": "Link", "idx": 1},
            {"link_type": "DocType", "link_to": "Team Member Mapping", "label": "Team Members", "onboard": 1, "type": "Link", "idx": 2},
            {"link_type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance", "onboard": 1, "type": "Link", "idx": 3},
            {"link_type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks", "onboard": 1, "type": "Link", "idx": 4},
            {"link_type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards", "onboard": 1, "type": "Link", "idx": 5},
            {"link_type": "Report", "link_to": "Daily Performance Report", "label": "Daily Performance Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 6},
            {"link_type": "Report", "link_to": "Monthly Performance Report", "label": "Monthly Performance Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 7},
            {"link_type": "Report", "link_to": "Employee Wise Report", "label": "Employee Wise Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 8},
            {"link_type": "Report", "link_to": "Team Wise Report", "label": "Team Wise Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 9},
            {"link_type": "Report", "link_to": "Pending Task Report", "label": "Pending Task Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 10},
            {"link_type": "Report", "link_to": "Top Performers", "label": "Top Performers", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 11},
            {"link_type": "Report", "link_to": "Low Performers", "label": "Low Performers", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 12},
            {"link_type": "Report", "link_to": "Monthly KPI Report", "label": "Monthly KPI Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 13},
            {"link_type": "Report", "link_to": "Leaderboard Report", "label": "Leaderboard Report", "is_query_report": 1, "onboard": 1, "type": "Link", "idx": 14},
        ]

        for link in links_data:
            row = dict(link)
            row["name"] = _rand_id()
            row["parent"] = ws_name
            row["parentfield"] = "links"
            row["parenttype"] = "Workspace"
            row["docstatus"] = 0
            row["owner"] = "Administrator"
            row["modified_by"] = "Administrator"
            filtered_link = {k: v for k, v in row.items() if k in link_col_names}
            cols_str_l = ", ".join([f"`{k}`" for k in filtered_link.keys()])
            vals_str_l = ", ".join(["%s"] * len(filtered_link))
            frappe.db.sql(
                f"INSERT INTO `tabWorkspace Link` ({cols_str_l}) VALUES ({vals_str_l})",
                list(filtered_link.values()),
            )

        frappe.db.commit()
        frappe.clear_cache()
    except Exception:
        pass


def create_module_def():
    try:
        if not frappe.db.exists("Module Def", "Employee Performance"):
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
    except Exception:
        pass


def create_roles():
    for rd in [
        {"role_name": "EPMS Founder", "desk_access": 1, "is_custom": 1},
        {"role_name": "EPMS Team Leader", "desk_access": 1, "is_custom": 1},
        {"role_name": "EPMS Team Member", "desk_access": 1, "is_custom": 1},
    ]:
        try:
            if not frappe.db.exists("Role", rd["role_name"]):
                frappe.get_doc({"doctype": "Role", **rd}).insert(ignore_permissions=True)
        except Exception:
            pass


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
            try:
                if not frappe.db.exists("Custom DocPerm", {"parent": dt, "role": role}):
                    frappe.get_doc({"doctype": "Custom DocPerm", "parent": dt, "parenttype": "DocType", "parentfield": "permissions", "role": role, **perms}).insert(ignore_permissions=True)
            except Exception:
                pass
