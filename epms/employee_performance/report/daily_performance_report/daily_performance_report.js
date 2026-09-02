// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

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
            fieldname: 'task_status',
            fieldtype: 'Select',
            label: __('Status'),
            options: '\nCompleted\nIn Progress\nPending\nBlocked'
        }
    ],

    onload: function(report) {
        report.page.add_inner_button(__('Export to CSV'), function() {
            frappe.query_report.export_report();
        });
    }
};
