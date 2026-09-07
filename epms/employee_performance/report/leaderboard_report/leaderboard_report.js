frappe.query_reports['Leaderboard Report'] = {
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
        }
    ],

    formatters: {
        final_grade: function(value) { return epms_report_utils.badge(value); },
        overall_score: function(value) { return epms_report_utils.progress(value); }
    },

    onload: function(report) {
        epms_report_utils.addExportButtons(report);
    }
};
