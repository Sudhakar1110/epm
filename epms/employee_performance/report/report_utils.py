"""Shared HTML formatting helpers for EPMS reports.

Returns raw HTML that Frappe renders in report cells.
CSS classes are defined in epms.css and epms_portal.css.
"""


def badge(value):
    """Render status/grade as a colored badge."""
    if not value:
        return ""
    v = str(value).lower()
    cls = "epms-badge-info"
    if v in ("on track", "excellent", "very good", "completed", "a+", "a", "b+", "b"):
        cls = "epms-badge-success"
    elif v in ("needs attention", "good", "average", "in progress", "c", "d"):
        cls = "epms-badge-warning"
    elif v in ("at risk", "needs improvement", "blocked", "f", "fail"):
        cls = "epms-badge-danger"
    elif v in ("pending",):
        cls = "epms-badge-muted"
    return f'<span class="epms-badge {cls}">{value}</span>'


def progress_bar(value):
    """Render a percentage as a colored progress bar."""
    if value is None or value == "":
        return ""
    pct = float(value) or 0
    if pct >= 80:
        cls = "green"
    elif pct >= 60:
        cls = "yellow"
    else:
        cls = "red"
    return (
        f'<div class="epms-progress">'
        f'<div class="epms-progress-track"><div class="epms-progress-fill {cls}" '
        f'style="width:{min(pct, 100):.0f}%"></div></div>'
        f'<span class="epms-progress-label">{pct:.1f}%</span></div>'
    )


def priority(value):
    """Render priority as a colored dot badge."""
    if not value:
        return ""
    v = str(value).lower()
    cls = "epms-priority-medium"
    if v == "low":
        cls = "epms-priority-low"
    elif v == "medium":
        cls = "epms-priority-medium"
    elif v == "high":
        cls = "epms-priority-high"
    elif v == "critical":
        cls = "epms-priority-critical"
    return f'<span class="epms-priority {cls}">{value}</span>'


def score_color(value):
    """Render a numeric score with color class."""
    if value is None or value == "":
        return "0"
    v = float(value) or 0
    if v >= 80:
        cls = "epms-badge-success"
    elif v >= 60:
        cls = "epms-badge-warning"
    else:
        cls = "epms-badge-danger"
    return f'<span class="epms-badge {cls}">{v:.1f}</span>'
