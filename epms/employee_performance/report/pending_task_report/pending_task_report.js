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

    onload: function(report) {
        epms_report_utils.addExportButtons(report);
    }
};
