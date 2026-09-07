// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Performance', {
    refresh: function(frm) {
        // Show action buttons
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('View Scorecard'), function() {
                frappe.set_route('List', 'Performance Scorecard', {
                    employee: frm.doc.employee
                });
            }, __('Actions'));

            frm.add_custom_button(__('View History'), function() {
                frappe.set_route('List', 'Daily Performance', {
                    employee: frm.doc.employee,
                    team: frm.doc.team
                });
            }, __('Actions'));
        }

        // Set indicators based on status
        if (frm.doc.task_status === 'Completed') {
            frm.page.set_indicator(__('Completed'), 'green');
        } else if (frm.doc.task_status === 'In Progress') {
            frm.page.set_indicator(__('In Progress'), 'blue');
        } else if (frm.doc.task_status === 'Pending') {
            frm.page.set_indicator(__('Pending'), 'orange');
        } else if (frm.doc.task_status === 'Blocked') {
            frm.page.set_indicator(__('Blocked'), 'red');
        }

        // Set priority indicator
        if (frm.doc.priority === 'Critical') {
            frm.page.set_indicator(__('Critical Priority'), 'red');
        } else if (frm.doc.priority === 'High') {
            frm.page.set_indicator(__('High Priority'), 'orange');
        }

        // Validate hours worked
        if (frm.doc.actual_hours > 24) {
            frappe.msgprint(__('Warning: Hours worked cannot exceed 24'));
        }
    },

    validate: function(frm) {
        // Validate completion percentage
        if (frm.doc.completion_percentage < 0 || frm.doc.completion_percentage > 100) {
            frappe.msgprint(__('Completion percentage must be between 0 and 100'));
            frappe.validated = false;
        }

        // Validate rating
        if (frm.doc.daily_rating < 1 || frm.doc.daily_rating > 10) {
            frappe.msgprint(__('Daily rating must be between 1 and 10'));
            frappe.validated = false;
        }

        // Validate quality score
        if (frm.doc.quality_score < 1 || frm.doc.quality_score > 10) {
            frappe.msgprint(__('Quality score must be between 1 and 10'));
            frappe.validated = false;
        }

        // Validate hours
        if (frm.doc.actual_hours > 24) {
            frappe.msgprint(__('Actual hours cannot exceed 24'));
            frappe.validated = false;
        }

        // Validate date
        if (frm.doc.date > frappe.datetime.get_today()) {
            frappe.msgprint(__('Cannot submit performance for future dates'));
            frappe.validated = false;
        }
    },

    team: function(frm) {
        // Auto-fill team leader when team changes
        if (frm.doc.team) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Team',
                    filters: { name: frm.doc.team },
                    fieldname: ['team_leader']
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('team_leader', r.message.team_leader);
                    }
                }
            });
        }
    },

    employee: function(frm) {
        // Auto-fill employee name when employee changes
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

    task_status: function(frm) {
        // Auto-set completion percentage based on status
        if (frm.doc.task_status === 'Completed') {
            frm.set_value('completion_percentage', 100);
        } else if (frm.doc.task_status === 'Pending') {
            frm.set_value('completion_percentage', 0);
        }
    },

    expected_hours: function(frm) {
        // Validate expected hours
        if (frm.doc.expected_hours > 24) {
            frappe.msgprint(__('Expected hours cannot exceed 24'));
            frm.set_value('expected_hours', 24);
        }
    },

    actual_hours: function(frm) {
        // Validate actual hours
        if (frm.doc.actual_hours > 24) {
            frappe.msgprint(__('Actual hours cannot exceed 24'));
            frm.set_value('actual_hours', 24);
        }
    }
});

// Child table events for Pending Tasks
frappe.ui.form.on('Pending Task', {
    // No additional events needed for child table
});
