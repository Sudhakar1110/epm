import frappe

from epms.employee_performance.utils import (
    portal_login_redirect,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    teams = frappe.get_all(
        "Team",
        filters={"status": "Active"},
        fields=["name", "team_name", "team_leader", "description", "total_members", "status"],
        order_by="team_name asc",
    )

    all_members = frappe.get_all(
        "Team Member Mapping",
        filters={"status": "Active"},
        fields=["team", "employee_name"],
        order_by="employee_name asc",
    )

    members_by_team = {}
    for m in all_members:
        members_by_team.setdefault(m.get("team"), []).append(m.get("employee_name") or "Member")

    context.teams = []
    for t in teams:
        members = members_by_team.get(t.get("name"), [])
        leader = t.get("team_leader")
        leader_name = leader
        if leader:
            full_name = frappe.db.get_value("User", leader, "full_name")
            leader_name = full_name or leader
        t["leader_name"] = leader_name
        t["member_count"] = len(members)
        t["member_preview"] = members[:4]
        t["extra_members"] = max(len(members) - 4, 0)
        context.teams.append(t)

    context.total_teams = len(context.teams)
    context.total_members = len(all_members)

    # Portal team creation: who may create, and whom they may assign as leader.
    context.can_create_team = frappe.has_permission("Team", "create")

    # Every enabled system user is a candidate (same pool the desk shows);
    # choosing a user without a leader role auto-assigns it on creation.
    candidates = []
    users = frappe.get_all(
        "User",
        filters={"enabled": 1, "user_type": "System User"},
        fields=["name", "full_name", "email"],
        order_by="full_name asc",
    )
    for u in users:
        label = (u.get("full_name") or "").strip() or u.get("email") or u.get("name")
        candidates.append({"name": u.get("name"), "label": f"{label} ({u.get('name')})"})
    context.candidate_leaders = candidates

    context.active_page = "teams"
