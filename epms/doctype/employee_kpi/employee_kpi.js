// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee KPI', {
    refresh: function(frm) {
        // Show achievement indicator
        if (frm.doc.achieved_percentage) {
            var color = 'green';
            if (frm.doc.achieved_percentage < 50) color = 'red';
            else if (frm.doc.achieved_percentage < 80) color = 'orange';
            
            frm.dashboard.add_comment(
                __('Achievement: {0}%', [frm.doc.achieved_percentage.toFixed(1)]),
                color,
                true
            );
        }

        // Set status indicator
        if (frm.doc.status === 'Exceeded') {
            frm.page.set_indicator(__('Exceeded'), 'green');
        } else if (frm.doc.status === 'Completed') {
            frm.page.set_indicator(__('Completed'), 'blue');
        } else if (frm.doc.status === 'In Progress') {
            frm.page.set_indicator(__('In Progress'), 'orange');
        } else {
            frm.page.set_indicator(__('Pending'), 'red');
        }
    },

    validate: function(frm) {
        // Validate target value
        if (frm.doc.target_value && frm.doc.target_value < 0) {
            frappe.msgprint(__('Target value cannot be negative'));
            frappe.validated = false;
        }

        // Validate actual value
        if (frm.doc.actual_value && frm.doc.actual_value < 0) {
            frappe.msgprint(__('Actual value cannot be negative'));
            frappe.validated = false;
        }

        // Validate weight
        if (frm.doc.weight && (frm.doc.weight < 0 || frm.doc.weight > 100)) {
            frappe.msgprint(__('Weight must be between 0 and 100'));
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

            // Get team
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Team Member Mapping',
                    filters: { user: frm.doc.employee, status: 'Active' },
                    fieldname: ['team']
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('team', r.message.team);
                    }
                }
            });
        }
    },

    target_value: function(frm) {
        // Recalculate achievement
        if (frm.doc.target_value && frm.doc.actual_value) {
            var achievement = (frm.doc.actual_value / frm.doc.target_value) * 100;
            frm.set_value('achieved_percentage', Math.min(achievement, 100));
        }
    },

    actual_value: function(frm) {
        // Recalculate achievement
        if (frm.doc.target_value && frm.doc.actual_value) {
            var achievement = (frm.doc.actual_value / frm.doc.target_value) * 100;
            frm.set_value('achieved_percentage', Math.min(achievement, 100));
        }
    }
});
