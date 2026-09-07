// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.listview_settings['Daily Performance'] = {
    get_indicator: function(doc) {
        if (doc.task_status === 'Completed') {
            return [__('Completed'), 'green', 'task_status,=,Completed'];
        } else if (doc.task_status === 'In Progress') {
            return [__('In Progress'), 'blue', 'task_status,=,In Progress'];
        } else if (doc.task_status === 'Pending') {
            return [__('Pending'), 'orange', 'task_status,=,Pending'];
        } else {
            return [__('Blocked'), 'red', 'task_status,=,Blocked'];
        }
    },

    formatters: {
        performance_id: function(value) {
            return `<strong>${value}</strong>`;
        },
        priority: function(value) {
            if (value === 'Critical') {
                return `<span class="indicator-pill red">${value}</span>`;
            } else if (value === 'High') {
                return `<span class="indicator-pill orange">${value}</span>`;
            } else if (value === 'Medium') {
                return `<span class="indicator-pill blue">${value}</span>`;
            } else {
                return `<span class="indicator-pill green">${value}</span>`;
            }
        }
    },

    onload: function(listview) {
        // Add filter buttons
        listview.page.add_inner_button(__('Today'), function() {
            listview.filter_area.add([[listview.doctype, 'date', '=', frappe.datetime.get_today()]]);
            listview.refresh();
        });

        listview.page.add_inner_button(__('This Week'), function() {
            var week_start = frappe.datetime.add_days(frappe.datetime.get_today(), -frappe.datetime.get_day(frappe.datetime.get_today()));
            listview.filter_area.add([[listview.doctype, 'date', '>=', week_start]]);
            listview.refresh();
        });
    }
};
