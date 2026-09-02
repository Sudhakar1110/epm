// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Scorecard', {
    refresh: function(frm) {
        // Show action buttons
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('View Daily Performance'), function() {
                frappe.set_route('List', 'Daily Performance', {
                    employee: frm.doc.employee,
                    team: frm.doc.team
                });
            }, __('Actions'));

            frm.add_custom_button(__('View Team Scorecards'), function() {
                frappe.set_route('List', 'Performance Scorecard', {
                    team: frm.doc.team,
                    month: frm.doc.month,
                    year: frm.doc.year
                });
            }, __('Actions'));

            frm.add_custom_button(__('Recalculate'), function() {
                frappe.confirm(
                    __('Are you sure you want to recalculate this scorecard?'),
                    function() {
                        frappe.call({
                            method: 'frappe.client.get_doc',
                            args: {
                                doctype: 'Performance Scorecard',
                                name: frm.doc.name
                            },
                            callback: function(r) {
                                if (r.message) {
                                    frappe.show_alert({
                                        message: __('Scorecard recalculated'),
                                        indicator: 'green'
                                    });
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                );
            }, __('Actions'));
        }

        // Set grade indicator
        if (frm.doc.final_grade === 'Excellent') {
            frm.page.set_indicator(__('Excellent'), 'green');
        } else if (frm.doc.final_grade === 'Very Good') {
            frm.page.set_indicator(__('Very Good'), 'blue');
        } else if (frm.doc.final_grade === 'Good') {
            frm.page.set_indicator(__('Good'), 'orange');
        } else if (frm.doc.final_grade === 'Average') {
            frm.page.set_indicator(__('Average'), 'yellow');
        } else {
            frm.page.set_indicator(__('Needs Improvement'), 'red');
        }

        // Show score breakdown
        if (frm.doc.overall_score) {
            frm.dashboard.add_comment(
                __('Overall Score: {0} ({1})', [frm.doc.overall_score.toFixed(2), frm.doc.final_grade]),
                'blue',
                true
            );
        }
    },

    validate: function(frm) {
        // Validate month
        if (frm.doc.month && (frm.doc.month < 1 || frm.doc.month > 12)) {
            frappe.msgprint(__('Please select a valid month'));
            frappe.validated = false;
        }

        // Validate year
        if (frm.doc.year && (frm.doc.year < 2000 || frm.doc.year > 2100)) {
            frappe.msgprint(__('Please enter a valid year'));
            frappe.validated = false;
        }
    },

    employee: function(frm) {
        // Auto-fill employee name and team
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
    }
});
