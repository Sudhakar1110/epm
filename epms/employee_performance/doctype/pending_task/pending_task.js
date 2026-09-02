// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pending Task', {
    refresh: function(frm) {
        // Show action buttons
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Mark as Complete'), function() {
                frappe.confirm(
                    __('Are you sure you want to mark this task as complete?'),
                    function() {
                        frm.set_value('current_status', 'Completed');
                        frm.set_value('completion_date', frappe.datetime.get_today());
                        frm.save();
                    }
                );
            }, __('Actions'));

            frm.add_custom_button(__('View Performance'), function() {
                frappe.set_route('List', 'Daily Performance', {
                    employee: frm.doc.employee
                });
            }, __('Actions'));
        }

        // Set indicators based on status
        if (frm.doc.current_status === 'Completed') {
            frm.page.set_indicator(__('Completed'), 'green');
        } else if (frm.doc.current_status === 'In Progress') {
            frm.page.set_indicator(__('In Progress'), 'blue');
        } else if (frm.doc.current_status === 'Pending') {
            frm.page.set_indicator(__('Pending'), 'orange');
        } else if (frm.doc.current_status === 'Blocked') {
            frm.page.set_indicator(__('Blocked'), 'red');
        }

        // Check if overdue
        if (frm.doc.expected_completion && 
            frm.doc.expected_completion < frappe.datetime.get_today() &&
            frm.doc.current_status !== 'Completed') {
            frm.page.set_indicator(__('Overdue'), 'red');
        }

        // Set priority indicator
        if (frm.doc.priority === 'Critical') {
            frm.page.set_indicator(__('Critical Priority'), 'red');
        } else if (frm.doc.priority === 'High') {
            frm.page.set_indicator(__('High Priority'), 'orange');
        }
    },

    validate: function(frm) {
        // Validate expected completion date
        if (frm.doc.expected_completion && 
            frm.doc.expected_completion < frappe.datetime.get_today()) {
            frappe.msgprint(__('Expected completion date cannot be in the past'));
            frappe.validated = false;
        }

        // Validate completion date
        if (frm.doc.completion_date && 
            frm.doc.completion_date > frappe.datetime.get_today()) {
            frappe.msgprint(__('Completion date cannot be in the future'));
            frappe.validated = false;
        }

        // Validate task field
        if (!frm.doc.task || frm.doc.task.length < 3) {
            frappe.msgprint(__('Task description must be at least 3 characters'));
            frappe.validated = false;
        }
    },

    employee: function(frm) {
        // Auto-fill employee name
        if (frm.doc.employee) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'User',
                    filters: { name: frm.doc.employee },
                    fieldname: ['full_name']
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('employee_name', r.message.full_name);
                    }
                }
            });
        }
    },

    current_status: function(frm) {
        // Auto-set completion date when status changes to Completed
        if (frm.doc.current_status === 'Completed') {
            frm.set_value('completion_date', frappe.datetime.get_today());
        }
    }
});
