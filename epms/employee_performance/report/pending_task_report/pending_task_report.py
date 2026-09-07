import frappe
from frappe import _
from frappe.utils import getdate, nowdate, date_diff


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)

    return columns, data, None, chart


def get_columns():
    return [
        {"fieldname": "task_title", "fieldtype": "Data", "label": _("Task"), "width": 200},
        {"fieldname": "employee_name", "fieldtype": "Data", "label": _("Employee"), "width": 150},
        {"fieldname": "date", "fieldtype": "Date", "label": _("Date"), "width": 100},
        {"fieldname": "days_overdue", "fieldtype": "Int", "label": _("Days Overdue"), "width": 100},
        {"fieldname": "priority", "fieldtype": "Data", "label": _("Priority"), "width": 80},
        {"fieldname": "task_status", "fieldtype": "Data", "label": _("Status"), "width": 100},
        {"fieldname": "remarks", "fieldtype": "Data", "label": _("Remarks"), "width": 150},
    ]


def get_data(filters):
    today = getdate(nowdate())

    dp_conditions = {"docstatus": 1}
    if filters.get("employee"):
        dp_conditions["employee"] = filters["employee"]

    daily_performances = frappe.get_all(
        "Daily Performance",
        filters=dp_conditions,
        fields=["name", "employee", "employee_name", "date"],
        order_by="date desc",
    )

    dp_names = [d.name for d in daily_performances]
    if not dp_names:
        return []

    dp_map = {d.name: d for d in daily_performances}

    sub_conditions = {}
    if filters.get("priority"):
        sub_conditions["priority"] = filters["priority"]
    if filters.get("status"):
        sub_conditions["task_status"] = filters["status"]
    if filters.get("show_completed") != 1:
        sub_conditions["task_status"] = ["not in", ["Completed"]]

    sub_conditions["parent"] = ["in", dp_names]

    subtasks = frappe.get_all(
        "Daily Performance Subtask",
        filters=sub_conditions,
        fields=["task_title", "task_status", "priority", "remarks", "parent"],
        order_by="priority desc",
    )

    data = []
    for st in subtasks:
        dp = dp_map.get(st.parent, {})
        days_overdue = 0
        if dp.get("date") and st.task_status != "Completed":
            dp_date = getdate(dp["date"])
            if dp_date < today:
                days_overdue = date_diff(today, dp_date)

        data.append({
            "task_title": st.task_title,
            "employee_name": dp.get("employee_name", ""),
            "date": dp.get("date"),
            "days_overdue": days_overdue,
            "priority": st.priority,
            "task_status": st.task_status,
            "remarks": st.remarks,
        })

    return data


def get_chart_data(data):
    if not data:
        return None

    status_counts = {}
    for row in data:
        status = row.get("task_status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [{"name": "Tasks", "values": list(status_counts.values())}],
        },
        "type": "bar",
        "colors": ["#ffc107", "#007bff", "#28a745", "#dc3545"],
    }
