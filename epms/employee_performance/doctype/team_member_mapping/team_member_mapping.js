// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Team Member Mapping', {
    refresh: function(frm) {
        // Show performance button
        if (!frm.is_new()) {
            frm.add_custom_button(__('View Performance'), function() {
                frappe.set_route('List', 'Daily Performance', {
                    employee: frm.doc.user
                });
            }, __('Actions'));

            frm.add_custom_button(__('View Scorecard'), function() {
                frappe.set_route('List', 'Performance Scorecard', {
                    employee: frm.doc.user
                });
            }, __('Actions'));
        }

        // Set indicator
        if (frm.doc.status === 'Active') {
            frm.page.set_indicator(__('Active'), 'green');
        } else if (frm.doc.status === 'Inactive') {
            frm.page.set_indicator(__('Inactive'), 'orange');
        } else {
            frm.page.set_indicator(__('Left'), 'red');
        }
    },

    employee: function(frm) {
        // Auto-fill employee name and user
        if (frm.doc.employee) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Employee',
                    filters: { name: frm.doc.employee },
                    fieldname: ['employee_name', 'user_id', 'designation']
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('employee_name', r.message.employee_name);
                        if (r.message.user_id) {
                            frm.set_value('user', r.message.user_id);
                        }
                        if (r.message.designation) {
                            frm.set_value('designation', r.message.designation);
                        }
                    }
                }
            });
        }
    },

    validate: function(frm) {
        // Validate all required fields
        if (!frm.doc.employee) {
            frappe.msgprint(__('Please select an Employee'));
            frappe.validated = false;
        }
        if (!frm.doc.team) {
            frappe.msgprint(__('Please select a Team'));
            frappe.validated = false;
        }
        if (!frm.doc.user) {
            frappe.msgprint(__('Please select a User'));
            frappe.validated = false;
        }
    }
});
