// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

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

    onload: function(report) {
        report.page.add_inner_button(__('Export to CSV'), function() {
            frappe.query_report.export_report();
        });
    }
};
