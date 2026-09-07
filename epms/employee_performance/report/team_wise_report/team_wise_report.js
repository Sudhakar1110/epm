function epms_progress(val) {
    if (val === null || val === undefined || val === '') return '';
    var pct = parseFloat(val) || 0;
    var cls = 'blue';
    if (pct >= 80) cls = 'green';
    else if (pct >= 60) cls = 'yellow';
    else cls = 'red';
    return '<div class="epms-progress"><div class="epms-progress-track"><div class="epms-progress-fill ' + cls + '" style="width:' + Math.min(pct,100) + '%"></div></div><span class="epms-progress-label">' + pct.toFixed(1) + '%</span></div>';
}
function epms_score(v) {
    if (v === null || v === undefined || v === '') return '0';
    var n = parseFloat(v) || 0;
    var cls = 'epms-badge-success';
    if (n < 60) cls = 'epms-badge-danger';
    else if (n < 80) cls = 'epms-badge-warning';
    return '<span class="epms-badge ' + cls + '">' + n.toFixed(1) + '</span>';
}

frappe.query_reports['Team Wise Report'] = {
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
        }
    ],

    formatters: {
        avg_completion: function(v) { return epms_progress(v); },
        team_score: function(v) { return epms_score(v); }
    }
};
