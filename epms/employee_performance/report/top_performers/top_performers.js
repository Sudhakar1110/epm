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
function epms_score(v) {
    if (v === null || v === undefined || v === '') return '0';
    var n = parseFloat(v) || 0;
    var cls = 'epms-badge-success';
    if (n < 60) cls = 'epms-badge-danger';
    else if (n < 80) cls = 'epms-badge-warning';
    return '<span class="epms-badge ' + cls + '">' + n.toFixed(1) + '</span>';
}

frappe.query_reports['Top Performers'] = {
    filters: [
        {
            fieldname: 'month',
            fieldtype: 'Select',
            label: __('Month'),
            options: '1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12',
            default: new Date().getMonth() + 1,
            reqd: 1
        },
        {
            fieldname: 'year',
            fieldtype: 'Int',
            label: __('Year'),
            default: new Date().getFullYear(),
            reqd: 1
        },
        {
            fieldname: 'team',
            fieldtype: 'Link',
            label: __('Team'),
            options: 'Team'
        },
        {
            fieldname: 'limit',
            fieldtype: 'Int',
            label: __('Show Top N'),
            default: 10
        }
    ],

    formatters: {
        final_grade: function(v) { return epms_badge(v); },
        overall_score: function(v) { return epms_score(v); }
    }
};
