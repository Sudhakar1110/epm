// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.query_reports['Pending Task Report'] = {
    filters: [
        {
            fieldname: 'employee',
            fieldtype: 'Link',
            label: __('Employee'),
            options: 'User',
            get_query: function() {
                return {
                    filters: {
                        'user_type': 'System User'
                    }
                };
            }
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
            options: '\nPending\nIn Progress\nBlocked'
        },
        {
            fieldname: 'show_completed',
            fieldtype: 'Check',
            label: __('Show Completed'),
            default: 0
        }
    ],

    onload: function(report) {
        report.page.add_inner_button(__('Export to CSV'), function() {
            frappe.query_report.export_report();
        });
    }
};
