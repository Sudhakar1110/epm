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

frappe.query_reports['Pending Task Report'] = {
    filters: [
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
            fieldname: 'status',
            fieldtype: 'Select',
            label: __('Status'),
            options: '\nPending\nIn Progress\nCompleted\nBlocked'
        },
        {
            fieldname: 'show_completed',
            fieldtype: 'Check',
            label: __('Show Completed'),
            default: 0
        }
    ],

    formatters: {
        task_status: function(v) { return epms_badge(v); },
        priority: function(v) { return epms_priority(v); }
    }
};
