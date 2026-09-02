// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.listview_settings['Team Member Mapping'] = {
    get_indicator: function(doc) {
        if (doc.status === 'Active') {
            return [__('Active'), 'green', 'status,=,Active'];
        } else if (doc.status === 'Inactive') {
            return [__('Inactive'), 'orange', 'status,=,Inactive'];
        } else {
            return [__('Left'), 'red', 'status,=,Left'];
        }
    },

    formatters: {
        employee_name: function(value) {
            return `<strong>${value}</strong>`;
        }
    },

    onload: function(listview) {
        // Add filter buttons
        listview.page.add_inner_button(__('Active Only'), function() {
            listview.filter_area.add([[listview.doctype, 'status', '=', 'Active']]);
            listview.refresh();
        });
    }
};
