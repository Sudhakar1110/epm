import frappe
from frappe import _
import json
import os
import random
import string


def _rand_id():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=10))


def before_migrate():
    """Clean broken data and ensure Module Def exists before migration."""
    try:
        clean_broken_workspaces()
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


def clean_broken_workspaces():
    """Delete workspaces with null/empty names that break the sidebar."""
    try:
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name IS NULL OR name = '' OR name = '0'")
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent IS NULL OR parent = ''")
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent IS NULL OR parent = ''")
        frappe.db.commit()
    except Exception:
        pass


def fix_workspace_now():
    """Run: bench --site epms.ogascale.com execute epms.employee_performance.setup.fix_workspace_now"""
    print("\n=== EPMS Workspace Fix ===")

    # Step 0: Clean broken data
    print("0. Cleaning broken workspaces...")
    clean_broken_workspaces()

    # Step 1: Ensure Module Def exists
    create_module_def()
    frappe.db.commit()

    # Step 2: Delete existing workspace entirely
    ws_name = "Employee Performance Management"
    print(f"\n1. Deleting existing workspace '{ws_name}'...")
    frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace Quick List` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace Number Card` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace Chart` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace Custom Block` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace Workflow Overview` WHERE parent = %s", ws_name)
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", ws_name)
    frappe.db.commit()
    print("   Deleted.")

    # Step 3: Load workspace JSON and create via frappe.new_doc
    print("\n2. Creating workspace via frappe.new_doc...")
    json_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "workspace",
        "employee_performance_management.json",
    )

    try:
        with open(json_path, "r") as f:
            ws_data = json.load(f)

        # Create workspace using new_doc (proper ORM)
        ws = frappe.new_doc("Workspace")
        ws.module = "Employee Performance"
        ws.label = ws_data.get("label", ws_name)
        ws.title = ws_data.get("title", ws_name)
        ws.icon = ws_data.get("icon", "octicon octicon-goal")
        ws.indicator_color = ws_data.get("indicator_color", "green")
        ws.is_hidden = 0
        ws.public = 1
        ws.content = ws_data.get("content", "[]")

        # Add links from JSON
        for link in ws_data.get("links", []):
            if link.get("type") == "Separator":
                continue
            ws.append("links", {
                "link_type": link.get("link_type", "DocType"),
                "link_to": link.get("link_to"),
                "label": link.get("label", ""),
                "onboard": link.get("onboard", 1),
                "is_query_report": link.get("is_query_report", 0),
                "type": "Link",
            })

        # Add shortcuts from JSON
        for sc in ws_data.get("shortcuts", []):
            ws.append("shortcuts", {
                "link_to": sc.get("link_to"),
                "type": sc.get("type", "DocType"),
                "label": sc.get("label", ""),
            })

        # Add number cards from JSON
        for nc in ws_data.get("number_cards", []):
            ws.append("number_cards", {
                "number_card": nc.get("number_card"),
            })

        # Add charts from JSON
        for chart in ws_data.get("charts", []):
            ws.append("charts", {
                "chart": chart.get("chart"),
                "width": chart.get("width", "Half"),
            })

        ws.insert(ignore_permissions=True)
        frappe.db.commit()
        ws_name = ws.name
        print(f"   Created workspace: {ws_name}")
    except Exception as e:
        print(f"   frappe.new_doc failed: {e}")
        print("   Falling back to SQL...")
        _create_workspace_sql(ws_name, json_path)
        return

    # Step 4: Force clear ALL caches
    frappe.clear_cache()
    frappe.clear_document_cache("Workspace", ws_name)
    frappe.client.delete_cache("Workspace", ws_name)
    try:
        frappe.cache().delete_value("workspace:{0}".format(ws_name))
        frappe.cache().delete_value("workspace_list")
        frappe.cache().delete_value("desk_sidebar")
        frappe.cache().delete_value("app_modules")
    except Exception:
        pass
    print("\n3. Verification:")
    final_links = frappe.db.count("Workspace Link", {"parent": ws_name})
    final_scs = frappe.db.count("Workspace Shortcut", {"parent": ws_name})
    final_nc = frappe.db.count("Workspace Number Card", {"parent": ws_name})
    final_ch = frappe.db.count("Workspace Chart", {"parent": ws_name})
    # Verify content
    content = frappe.db.get_value("Workspace", ws_name, "content")
    print(f"   Links: {final_links}, Shortcuts: {final_scs}")
    print(f"   Number Cards: {final_nc}, Charts: {final_ch}")
    print(f"   Content length: {len(content) if content else 0} chars")
    print(f"   Content preview: {content[:200] if content else 'EMPTY'}...")
    print(f"   URL: /app/employee-performance-management")
    print("\nIMPORTANT: Clear browser cache too! Press Ctrl+Shift+R")
    print("=== Done ===")


def _create_workspace_sql(ws_name, json_path):
    """Fallback: create workspace via SQL if ORM fails."""
    try:
        with open(json_path, "r") as f:
            ws_data = json.load(f)
    except Exception:
        ws_data = {}

    cols = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`", as_list=True)
    col_names = [c[0] for c in cols]

    insert_cols = {
        "name": ws_name,
        "module": "Employee Performance",
        "label": ws_name,
        "title": ws_name,
        "content": ws_data.get("content", "[]"),
        "icon": "octicon octicon-goal",
        "indicator_color": "green",
        "is_hidden": 0,
        "public": 1,
        "docstatus": 0,
        "idx": 0,
        "sequence_id": 1,
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
        print(f"   Created workspace via SQL: {ws_name}")
    except Exception as e:
        print(f"   SQL INSERT failed: {e}")
        return

    # Add shortcuts
    for sc in ws_data.get("shortcuts", []):
        try:
            frappe.db.sql(
                """INSERT INTO `tabWorkspace Shortcut`
                (`name`, `type`, `link_to`, `label`, `parent`, `parentfield`, `parenttype`,
                 `docstatus`, `owner`, `modified_by`)
                VALUES (%s, %s, %s, %s, %s, 'shortcuts', 'Workspace', 0, 'Administrator', 'Administrator')""",
                (_rand_id(), sc.get("type", "DocType"), sc.get("link_to"), sc.get("label", ""), ws_name),
            )
        except Exception:
            pass

    # Add links
    for link in ws_data.get("links", []):
        if link.get("type") == "Separator":
            continue
        try:
            frappe.db.sql(
                """INSERT INTO `tabWorkspace Link`
                (`name`, `type`, `link_type`, `link_to`, `label`, `onboard`, `is_query_report`,
                 `parent`, `parentfield`, `parenttype`, `docstatus`, `owner`, `modified_by`)
                VALUES (%s, 'Link', %s, %s, %s, %s, %s, %s, 'links', 'Workspace', 0, 'Administrator', 'Administrator')""",
                (_rand_id(), link.get("link_type", "DocType"), link.get("link_to"),
                 link.get("label", ""), link.get("onboard", 1), link.get("is_query_report", 0), ws_name),
            )
        except Exception:
            pass

    # Add number cards
    for nc in ws_data.get("number_cards", []):
        try:
            frappe.db.sql(
                """INSERT INTO `tabWorkspace Number Card`
                (`name`, `number_card`, `parent`, `parentfield`, `parenttype`,
                 `docstatus`, `owner`, `modified_by`)
                VALUES (%s, %s, %s, 'number_cards', 'Workspace', 0, 'Administrator', 'Administrator')""",
                (_rand_id(), nc.get("number_card"), ws_name),
            )
        except Exception:
            pass

    # Add charts
    for chart in ws_data.get("charts", []):
        try:
            frappe.db.sql(
                """INSERT INTO `tabWorkspace Chart`
                (`name`, `chart`, `width`, `parent`, `parentfield`, `parenttype`,
                 `docstatus`, `owner`, `modified_by`)
                VALUES (%s, %s, %s, %s, 'charts', 'Workspace', 0, 'Administrator', 'Administrator')""",
                (_rand_id(), chart.get("chart"), chart.get("width", "Half"), ws_name),
            )
        except Exception:
            pass

    frappe.db.commit()
    frappe.clear_cache()

    final_links = frappe.db.count("Workspace Link", {"parent": ws_name})
    final_scs = frappe.db.count("Workspace Shortcut", {"parent": ws_name})
    final_nc = frappe.db.count("Workspace Number Card", {"parent": ws_name})
    final_ch = frappe.db.count("Workspace Chart", {"parent": ws_name})
    print(f"   Links: {final_links}, Shortcuts: {final_scs}")
    print(f"   Number Cards: {final_nc}, Charts: {final_ch}")
    print(f"   URL: /app/employee-performance-management")
    print("=== Done ===")


def ensure_workspace_exists():
    """Create workspace if it doesn't exist."""
    try:
        if frappe.db.exists("Workspace", "Employee Performance Management"):
            return
    except Exception:
        return

    create_module_def()

    json_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "workspace",
        "employee_performance_management.json",
    )

    try:
        with open(json_path, "r") as f:
            ws_data = json.load(f)

        ws = frappe.new_doc("Workspace")
        ws.module = "Employee Performance"
        ws.label = ws_data.get("label", "Employee Performance Management")
        ws.title = ws_data.get("title", "Employee Performance Management")
        ws.icon = ws_data.get("icon", "octicon octicon-goal")
        ws.indicator_color = ws_data.get("indicator_color", "green")
        ws.is_hidden = 0
        ws.public = 1
        ws.content = ws_data.get("content", "[]")

        for link in ws_data.get("links", []):
            if link.get("type") == "Separator":
                continue
            ws.append("links", {
                "link_type": link.get("link_type", "DocType"),
                "link_to": link.get("link_to"),
                "label": link.get("label", ""),
                "onboard": link.get("onboard", 1),
                "is_query_report": link.get("is_query_report", 0),
                "type": "Link",
            })

        for sc in ws_data.get("shortcuts", []):
            ws.append("shortcuts", {
                "link_to": sc.get("link_to"),
                "type": sc.get("type", "DocType"),
                "label": sc.get("label", ""),
            })

        for nc in ws_data.get("number_cards", []):
            ws.append("number_cards", {
                "number_card": nc.get("number_card"),
            })

        for chart in ws_data.get("charts", []):
            ws.append("charts", {
                "chart": chart.get("chart"),
                "width": chart.get("width", "Half"),
            })

        ws.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()
    except Exception:
        _create_workspace_sql("Employee Performance Management", json_path)


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
