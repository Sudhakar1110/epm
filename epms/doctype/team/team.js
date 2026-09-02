// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Team', {
    refresh: function(frm) {
        // Show team members button
        if (!frm.is_new()) {
            frm.add_custom_button(__('View Team Members'), function() {
                frappe.set_route('List', 'Team Member Mapping', {
                    team: frm.doc.name,
                    status: 'Active'
                });
            }, __('Actions'));

            frm.add_custom_button(__('View Daily Performance'), function() {
                frappe.set_route('List', 'Daily Performance', {
                    team: frm.doc.name
                });
            }, __('Actions'));

            frm.add_custom_button(__('View Scorecards'), function() {
                frappe.set_route('List', 'Performance Scorecard', {
                    team: frm.doc.name
                });
            }, __('Actions'));
        }

        // Set indicator
        if (frm.doc.status === 'Active') {
            frm.page.set_indicator(__('Active'), 'green');
        } else if (frm.doc.status === 'Inactive') {
            frm.page.set_indicator(__('Inactive'), 'orange');
        } else {
            frm.page.set_indicator(__('Archived'), 'red');
        }
    },

    validate: function(frm) {
        // Validate team name
        if (frm.doc.team_name && frm.doc.team_name.length < 3) {
            frappe.msgprint(__('Team name must be at least 3 characters'));
            frappe.validated = false;
        }
    },

    team_leader: function(frm) {
        // Validate team leader role
        if (frm.doc.team_leader) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'User',
                    filters: { name: frm.doc.team_leader },
                    fieldname: ['user_type', 'full_name']
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Team Leader: {0}', [r.message.full_name]),
                            indicator: 'green'
                        });
                    }
                }
            });
        }
    }
});
