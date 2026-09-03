import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


def execute(filters=None):
    """Execute Employee Wise Report."""
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)

    return columns, data, None, chart


def get_columns():
    """Get report columns."""
    return [
        {"fieldname": "employee_name", "fieldtype": "Data", "label": _("Employee"), "width": 150},
        {"fieldname": "team", "fieldtype": "Link", "label": _("Team"), "options": "Team", "width": 120},
        {"fieldname": "total_entries", "fieldtype": "Int", "label": _("Total Entries"), "width": 100},
        {"fieldname": "tasks_completed", "fieldtype": "Int", "label": _("Tasks Completed"), "width": 110},
        {"fieldname": "avg_rating", "fieldtype": "Float", "label": _("Avg Rating"), "width": 90},
        {"fieldname": "avg_quality", "fieldtype": "Float", "label": _("Avg Quality"), "width": 90},
        {"fieldname": "total_hours", "fieldtype": "Float", "label": _("Total Hours"), "width": 90},
        {"fieldname": "avg_completion", "fieldtype": "Percent", "label": _("Avg Completion %"), "width": 110},
        {"fieldname": "latest_score", "fieldtype": "Float", "label": _("Latest Score"), "width": 100},
        {"fieldname": "latest_grade", "fieldtype": "Data", "label": _("Latest Grade"), "width": 100},
    ]


def get_data(filters):
    """Get report data."""
    conditions = {"docstatus": 1}

    if filters.get("date_from"):
        conditions["date"] = [">=", filters["date_from"]]
    if filters.get("date_to"):
        if "date" in conditions and isinstance(conditions["date"], list) and conditions["date"][0] == ">=":
            conditions["date"] = ["between", [filters["date_from"], filters["date_to"]]]
        else:
            conditions["date"] = ["<=", filters["date_to"]]

    if filters.get("team"):
        conditions["team"] = filters["team"]

    if filters.get("employee"):
        conditions["employee"] = filters["employee"]

    # Get all performance entries
    entries = frappe.get_all(
        "Daily Performance",
        filters=conditions,
        fields=["employee", "employee_name", "team", "daily_rating", "quality_score", "actual_hours", "completion_percentage", "task_status"],
    )

    # Group by employee
    employee_data = {}
    for entry in entries:
        emp = entry.employee
        if emp not in employee_data:
            employee_data[emp] = {
                "employee_name": entry.employee_name,
                "team": entry.team,
                "total_entries": 0,
                "tasks_completed": 0,
                "ratings": [],
                "qualities": [],
                "hours": [],
                "completions": [],
            }
        d = employee_data[emp]
        d["total_entries"] += 1
        if entry.task_status == "Completed":
            d["tasks_completed"] += 1
        if entry.daily_rating:
            d["ratings"].append(entry.daily_rating)
        if entry.quality_score:
            d["qualities"].append(entry.quality_score)
        if entry.actual_hours:
            d["hours"].append(entry.actual_hours)
        if entry.completion_percentage:
            d["completions"].append(entry.completion_percentage)

    # Build result
    data = []
    for emp, d in employee_data.items():
        avg_rating = sum(d["ratings"]) / len(d["ratings"]) if d["ratings"] else 0
        avg_quality = sum(d["qualities"]) / len(d["qualities"]) if d["qualities"] else 0
        total_hours = sum(d["hours"])
        avg_completion = sum(d["completions"]) / len(d["completions"]) if d["completions"] else 0

        # Get latest scorecard
        scorecard = frappe.db.get_value(
            "Performance Scorecard",
            {"employee": emp, "docstatus": 1},
            ["overall_score", "final_grade"],
            order_by="year desc, month desc",
            as_dict=True,
        )

        data.append({
            "employee_name": d["employee_name"],
            "team": d["team"],
            "total_entries": d["total_entries"],
            "tasks_completed": d["tasks_completed"],
            "avg_rating": round(avg_rating, 2),
            "avg_quality": round(avg_quality, 2),
            "total_hours": round(total_hours, 2),
            "avg_completion": round(avg_completion, 2),
            "latest_score": scorecard.overall_score if scorecard else 0,
            "latest_grade": scorecard.final_grade if scorecard else "N/A",
        })

    # Sort by avg rating descending
    data.sort(key=lambda x: x["avg_rating"], reverse=True)

    return data


def get_chart_data(data):
    """Get chart data."""
    if not data:
        return None

    top_performers = sorted(data, key=lambda x: x.get("avg_rating", 0), reverse=True)[:10]

    return {
        "data": {
            "labels": [d.get("employee_name", "Unknown") for d in top_performers],
            "datasets": [
                {
                    "name": "Average Rating",
                    "values": [d.get("avg_rating", 0) for d in top_performers],
                }
            ],
        },
        "type": "bar",
        "colors": ["#5e64ff"],
    }
