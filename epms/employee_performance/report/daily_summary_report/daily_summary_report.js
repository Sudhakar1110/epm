function epms_progress(val) {
    if (val === null || val === undefined || val === '') return '';
    var pct = parseFloat(val) || 0;
    var cls = 'blue';
    if (pct >= 80) cls = 'green';
    else if (pct >= 60) cls = 'yellow';
    else cls = 'red';
    return '<div class="epms-progress"><div class="epms-progress-track"><div class="epms-progress-fill ' + cls + '" style="width:' + Math.min(pct,100) + '%"></div></div><span class="epms-progress-label">' + pct.toFixed(1) + '%</span></div>';
}

frappe.query_reports['Daily Summary Report'] = {
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
        }
    ],

    formatters: {
        avg_completion: function(v) { return epms_progress(v); }
    }
};
