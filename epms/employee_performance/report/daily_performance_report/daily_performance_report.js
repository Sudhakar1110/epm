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
        task_status: function(value) { return epms_report_utils.badge(value); },
        priority: function(value) { return epms_report_utils.priority(value); },
        completion_percentage: function(value) { return epms_report_utils.progress(value); }
    },

    onload: function(report) {
        epms_report_utils.addExportButtons(report);
    }
};
