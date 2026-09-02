// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

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

    onload: function(report) {
        report.page.add_inner_button(__('Export to CSV'), function() {
            frappe.query_report.export_report();
        });
    }
};
