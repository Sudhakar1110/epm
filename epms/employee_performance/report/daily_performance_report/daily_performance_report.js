function epms_badge(v) {
    if (!v) return '';
    var s = String(v).toLowerCase();
    var cls = 'epms-badge-info';
    if (['on track','excellent','very good','completed','a+','a','b+','b','gold','silver'].indexOf(s) > -1) cls = 'epms-badge-success';
    else if (['needs attention','good','average','in progress','c','d'].indexOf(s) > -1) cls = 'epms-badge-warning';
    else if (['at risk','needs improvement','blocked','f','fail'].indexOf(s) > -1) cls = 'epms-badge-danger';
    else if (['pending'].indexOf(s) > -1) cls = 'epms-badge-muted';
    return '<span class="epms-badge ' + cls + '">' + v + '</span>';
}
function epms_priority(v) {
    if (!v) return '';
    var s = String(v).toLowerCase();
    var cls = 'epms-priority-medium';
    if (s === 'low') cls = 'epms-priority-low';
    else if (s === 'medium') cls = 'epms-priority-medium';
    else if (s === 'high') cls = 'epms-priority-high';
    else if (s === 'critical') cls = 'epms-priority-critical';
    return '<span class="epms-priority ' + cls + '">' + v + '</span>';
}
function epms_progress(val) {
    if (val === null || val === undefined || val === '') return '';
    var pct = parseFloat(val) || 0;
    var cls = 'blue';
    if (pct >= 80) cls = 'green';
    else if (pct >= 60) cls = 'yellow';
    else cls = 'red';
    return '<div class="epms-progress"><div class="epms-progress-track"><div class="epms-progress-fill ' + cls + '" style="width:' + Math.min(pct,100) + '%"></div></div><span class="epms-progress-label">' + pct.toFixed(1) + '%</span></div>';
}

frappe.query_reports['Daily Performance Report'] = {
    filters: [
        {
            fieldname: 'date_from',
            fieldtype: 'Date',
            label: __('From Date'),
            default: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
            reqd: 1
        },
        {
            fieldname: 'date_to',
            fieldtype: 'Date',
            label: __('To Date'),
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: 'team',
            fieldtype: 'Link',
            label: __('Team'),
            options: 'Team'
        },
        {
            fieldname: 'employee',
            fieldtype: 'Link',
            label: __('Employee'),
            options: 'Employee'
        },
        {
            fieldname: 'priority',
            fieldtype: 'Select',
            label: __('Priority'),
            options: '\nLow\nMedium\nHigh\nCritical'
        },
        {
            fieldname: 'task_status',
            fieldtype: 'Select',
            label: __('Status'),
            options: '\nCompleted\nIn Progress\nPending\nBlocked'
        }
    ],

    formatters: {
        task_status: function(v) { return epms_badge(v); },
        priority: function(v) { return epms_priority(v); },
        completion_percentage: function(v) { return epms_progress(v); }
    }
};
