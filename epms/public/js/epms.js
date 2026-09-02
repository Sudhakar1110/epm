// EPMS JavaScript Utilities

frappe.provide('epms');

/**
 * EPMS Utility Functions
 */
epms.utils = {
    /**
     * Format score with color
     */
    format_score: function(score) {
        if (score >= 80) {
            return `<span class="text-success font-weight-bold">${score}</span>`;
        } else if (score >= 60) {
            return `<span class="text-warning font-weight-bold">${score}</span>`;
        } else {
            return `<span class="text-danger font-weight-bold">${score}</span>`;
        }
    },

    /**
     * Get grade badge HTML
     */
    get_grade_badge: function(grade) {
        var badge_class = 'badge-secondary';
        if (grade === 'Excellent') badge_class = 'badge-success';
        else if (grade === 'Very Good') badge_class = 'badge-info';
        else if (grade === 'Good') badge_class = 'badge-primary';
        else if (grade === 'Average') badge_class = 'badge-warning';
        else if (grade === 'Needs Improvement') badge_class = 'badge-danger';

        return `<span class="badge ${badge_class}">${grade}</span>`;
    },

    /**
     * Get status badge HTML
     */
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

        return `<span class="badge ${badge_class}">${status}</span>`;
    },

    /**
     * Get priority badge HTML
     */
    get_priority_badge: function(priority) {
        var badge_class = 'badge-secondary';
        if (priority === 'Critical') badge_class = 'badge-danger';
        else if (priority === 'High') badge_class = 'badge-warning';
        else if (priority === 'Medium') badge_class = 'badge-info';
        else if (priority === 'Low') badge_class = 'badge-success';

        return `<span class="badge ${badge_class}">${priority}</span>`;
    },

    /**
     * Check if date is overdue
     */
    is_overdue: function(date) {
        if (!date) return false;
        return new Date(date) < new Date(frappe.datetime.get_today());
    },

    /**
     * Format date for display
     */
    format_date: function(date) {
        if (!date) return '-';
        return frappe.datetime.str_to_user(date);
    },

    /**
     * Get medal for rank
     */
    get_medal: function(rank) {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return rank;
    }
};

/**
 * EPMS Chart Helpers
 */
epms.charts = {
    /**
     * Create a bar chart
     */
    create_bar_chart: function(container, data, options) {
        var default_options = {
            height: 300,
            colors: ['#5e64ff'],
            format_tooltip_x: function(d) {
                return d;
            },
            format_dataset: function(dataset, index) {
                return dataset;
            }
        };

        options = Object.assign(default_options, options || {});

        var chart = new frappe.Chart(container, {
            data: data,
            type: 'bar',
            height: options.height,
            colors: options.colors,
            barOptions: {
                spaceRatio: 0.5
            }
        });

        return chart;
    },

    /**
     * Create a line chart
     */
    create_line_chart: function(container, data, options) {
        var default_options = {
            height: 300,
            colors: ['#5e64ff'],
            dot_size: 5,
            line_size: 2
        };

        options = Object.assign(default_options, options || {});

        var chart = new frappe.Chart(container, {
            data: data,
            type: 'line',
            height: options.height,
            colors: options.colors,
            dotOptions: {
                size: options.dot_size
            },
            lineOptions: {
                dotSize: options.dot_size,
                strokeWidth: options.line_size
            }
        });

        return chart;
    },

    /**
     * Create a pie chart
     */
    create_pie_chart: function(container, data, options) {
        var default_options = {
            height: 300,
            colors: ['#28a745', '#007bff', '#ffc107', '#dc3545', '#6c757d']
        };

        options = Object.assign(default_options, options || {});

        var chart = new frappe.Chart(container, {
            data: data,
            type: 'pie',
            height: options.height,
            colors: options.colors
        });

        return chart;
    }
};

/**
 * EPMS API Helpers
 */
epms.api = {
    /**
     * Get employee performance
     */
    get_employee_performance: function(employee, month, year) {
        return frappe.call({
            method: 'epms.epms.api.get_employee_performance',
            args: {
                employee: employee,
                month: month,
                year: year
            }
        });
    },

    /**
     * Get monthly scorecard
     */
    get_monthly_scorecard: function(employee, month, year) {
        return frappe.call({
            method: 'epms.epms.api.get_monthly_scorecard',
            args: {
                employee: employee,
                month: month,
                year: year
            }
        });
    },

    /**
     * Get team performance
     */
    get_team_performance: function(team, month, year) {
        return frappe.call({
            method: 'epms.epms.api.get_team_performance',
            args: {
                team: team,
                month: month,
                year: year
            }
        });
    },

    /**
     * Get leaderboard
     */
    get_leaderboard: function(month, year) {
        return frappe.call({
            method: 'epms.epms.api.get_leaderboard',
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
    /**
     * Validate rating
     */
    validate_rating: function(value, field_name) {
        if (value < 1 || value > 10) {
            frappe.msgprint(__(field_name + ' must be between 1 and 10'));
            return false;
        }
        return true;
    },

    /**
     * Validate hours
     */
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

    /**
     * Validate completion percentage
     */
    validate_completion: function(value) {
        if (value < 0 || value > 100) {
            frappe.msgprint(__('Completion percentage must be between 0 and 100'));
            return false;
        }
        return true;
    },

    /**
     * Validate date not in future
     */
    validate_date: function(value) {
        if (value > frappe.datetime.get_today()) {
            frappe.msgprint(__('Cannot submit for future dates'));
            return false;
        }
        return true;
    }
};

// Initialize EPMS on page load
$(document).ready(function() {
    console.log('EPMS initialized');
});
