// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.listview_settings['Team'] = {
    get_indicator: function(doc) {
        if (doc.status === 'Active') {
            return [__('Active'), 'green', 'status,=,Active'];
        } else if (doc.status === 'Inactive') {
            return [__('Inactive'), 'orange', 'status,=,Inactive'];
        } else {
            return [__('Archived'), 'red', 'status,=,Archived'];
        }
    },

    formatters: {
        team_name: function(value) {
            return `<strong>${value}</strong>`;
        }
    },

    onload: function(listview) {
        // Add custom buttons
        listview.page.add_inner_button(__('Active Teams'), function() {
            listview.filter_area.add([[listview.doctype, 'status', '=', 'Active']]);
            listview.refresh();
        });
    }
};
