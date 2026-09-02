// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.listview_settings['Pending Task'] = {
    get_indicator: function(doc) {
        if (doc.current_status === 'Completed') {
            return [__('Completed'), 'green', 'current_status,=,Completed'];
        } else if (doc.current_status === 'In Progress') {
            return [__('In Progress'), 'blue', 'current_status,=,In Progress'];
        } else if (doc.current_status === 'Pending') {
            return [__('Pending'), 'orange', 'current_status,=,Pending'];
        } else {
            return [__('Blocked'), 'red', 'current_status,=,Blocked'];
        }
    },

    formatters: {
        task: function(value) {
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
        },
        expected_completion: function(value) {
            if (value && value < frappe.datetime.get_today()) {
                return `<span class="text-danger">${value}</span>`;
            }
            return value;
        }
    },

    onload: function(listview) {
        // Add filter buttons
        listview.page.add_inner_button(__('Overdue'), function() {
            listview.filter_area.add([[listview.doctype, 'expected_completion', '<', frappe.datetime.get_today()]]);
            listview.filter_area.add([[listview.doctype, 'current_status', '!=', 'Completed']]);
            listview.refresh();
        });

        listview.page.add_inner_button(__('Due Today'), function() {
            listview.filter_area.add([[listview.doctype, 'expected_completion', '=', frappe.datetime.get_today()]]);
            listview.refresh();
        });
    }
};
