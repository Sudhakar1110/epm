// EPMS JavaScript Utilities

frappe.provide('epms');

/**
 * EPMS Utility Functions
 */
epms.utils = {
    format_score: function(score) {
        if (score >= 80) {
            return '<span class="text-success font-weight-bold">' + score + '</span>';
        } else if (score >= 60) {
            return '<span class="text-warning font-weight-bold">' + score + '</span>';
        } else {
            return '<span class="text-danger font-weight-bold">' + score + '</span>';
        }
    },

    get_grade_badge: function(grade) {
        var badge_class = 'badge-secondary';
        if (grade === 'Excellent') badge_class = 'badge-success';
        else if (grade === 'Very Good') badge_class = 'badge-info';
        else if (grade === 'Good') badge_class = 'badge-primary';
        else if (grade === 'Average') badge_class = 'badge-warning';
        else if (grade === 'Needs Improvement') badge_class = 'badge-danger';

        return '<span class="badge ' + badge_class + '">' + grade + '</span>';
    },

    get_status_badge: function(status) {
        var badge_class = 'badge-secondary';
        if (status === 'Completed' || status === 'Active' || status === 'On Track') {
            badge_class = 'badge-success';
        } else if (status === 'In Progress') {
            badge_class = 'badge-info';
        } else if (status === 'Pending' || status === 'Needs Attention') {
            badge_class = 'badge-warning';
        } else if (status === 'Blocked' || status === 'At Risk' || status === 'Inactive') {
            badge_class = 'badge-danger';
        }

        return '<span class="badge ' + badge_class + '">' + status + '</span>';
    },

    get_priority_badge: function(priority) {
        var badge_class = 'badge-secondary';
        if (priority === 'Critical') badge_class = 'badge-danger';
        else if (priority === 'High') badge_class = 'badge-warning';
        else if (priority === 'Medium') badge_class = 'badge-info';
        else if (priority === 'Low') badge_class = 'badge-success';

        return '<span class="badge ' + badge_class + '">' + priority + '</span>';
    },

    is_overdue: function(date) {
        if (!date) return false;
        return new Date(date) < new Date(frappe.datetime.get_today());
    },

    format_date: function(date) {
        if (!date) return '-';
        return frappe.datetime.str_to_user(date);
    },

    get_medal: function(rank) {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return rank;
    }
};

/**
 * EPMS API Helpers
 */
epms.api = {
    get_employee_performance: function(employee, month, year) {
        return frappe.call({
            method: 'epms.employee_performance.api.get_employee_performance',
            args: {
                employee: employee,
                month: month,
                year: year
            }
        });
    },

    get_monthly_scorecard: function(employee, month, year) {
        return frappe.call({
            method: 'epms.employee_performance.api.get_monthly_scorecard',
            args: {
                employee: employee,
                month: month,
                year: year
            }
        });
    },

    get_team_performance: function(team, month, year) {
        return frappe.call({
            method: 'epms.employee_performance.api.get_team_performance',
            args: {
                team: team,
                month: month,
                year: year
            }
        });
    },

    get_leaderboard: function(month, year) {
        return frappe.call({
            method: 'epms.employee_performance.api.get_leaderboard',
            args: {
                month: month,
                year: year
            }
        });
    }
};

/**
 * EPMS Form Helpers
 */
epms.form = {
    validate_rating: function(value, field_name) {
        if (value < 1 || value > 10) {
            frappe.msgprint(__(field_name + ' must be between 1 and 10'));
            return false;
        }
        return true;
    },

    validate_hours: function(value) {
        if (value > 24) {
            frappe.msgprint(__('Hours cannot exceed 24'));
            return false;
        }
        if (value < 0) {
            frappe.msgprint(__('Hours cannot be negative'));
            return false;
        }
        return true;
    },

    validate_completion: function(value) {
        if (value < 0 || value > 100) {
            frappe.msgprint(__('Completion percentage must be between 0 and 100'));
            return false;
        }
        return true;
    },

    validate_date: function(value) {
        if (value > frappe.datetime.get_today()) {
            frappe.msgprint(__('Cannot submit for future dates'));
            return false;
        }
        return true;
    }
};
