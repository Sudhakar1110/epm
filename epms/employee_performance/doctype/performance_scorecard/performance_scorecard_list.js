// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.listview_settings['Performance Scorecard'] = {
    get_indicator: function(doc) {
        if (doc.performance_status === 'On Track') {
            return [__('On Track'), 'green', 'performance_status,=,On Track'];
        } else if (doc.performance_status === 'Needs Attention') {
            return [__('Needs Attention'), 'orange', 'performance_status,=,Needs Attention'];
        } else {
            return [__('At Risk'), 'red', 'performance_status,=,At Risk'];
        }
    },

    formatters: {
        employee_name: function(value) {
            return `<strong>${value}</strong>`;
        },
        final_grade: function(value) {
            if (value === 'Excellent') {
                return `<span class="indicator-pill green">${value}</span>`;
            } else if (value === 'Very Good') {
                return `<span class="indicator-pill blue">${value}</span>`;
            } else if (value === 'Good') {
                return `<span class="indicator-pill orange">${value}</span>`;
            } else if (value === 'Average') {
                return `<span class="indicator-pill yellow">${value}</span>`;
            } else {
                return `<span class="indicator-pill red">${value}</span>`;
            }
        },
        overall_score: function(value) {
            if (value >= 80) {
                return `<strong class="text-success">${value}</strong>`;
            } else if (value >= 60) {
                return `<strong class="text-warning">${value}</strong>`;
            } else {
                return `<strong class="text-danger">${value}</strong>`;
            }
        }
    },

    onload: function(listview) {
        // Add filter buttons
        listview.page.add_inner_button(__('Excellent'), function() {
            listview.filter_area.add([[listview.doctype, 'final_grade', '=', 'Excellent']]);
            listview.refresh();
        });

        listview.page.add_inner_button(__('Needs Improvement'), function() {
            listview.filter_area.add([[listview.doctype, 'final_grade', '=', 'Needs Improvement']]);
            listview.refresh();
        });

        listview.page.add_inner_button(__('Current Month'), function() {
            var today = frappe.datetime.get_today();
            var month = today.split('-')[1];
            var year = today.split('-')[0];
            listview.filter_area.add([[listview.doctype, 'month', '=', month]]);
            listview.filter_area.add([[listview.doctype, 'year', '=', year]]);
            listview.refresh();
        });
    }
};
