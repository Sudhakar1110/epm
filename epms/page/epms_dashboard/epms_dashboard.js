// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.pages['epms-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Employee Performance Dashboard'),
        single_column: true
    });

    // Add custom buttons
    page.add_button(__('Refresh'), function() {
        load_dashboard();
    }, 'fa fa-refresh');

    page.add_button(__('Export Report'), function() {
        frappe.set_route('query-report', 'Monthly Performance Report');
    }, 'fa fa-download');

    // Load dashboard
    load_dashboard();
};

function load_dashboard() {
    frappe.call({
        method: 'epms.epms.page.epms_dashboard.epms_dashboard.get_dashboard_data',
        callback: function(r) {
            if (r.message) {
                render_dashboard(r.message);
            }
        }
    });
}

function render_dashboard(data) {
    var wrapper = $('#page-epms-dashboard .page-content');
    wrapper.empty();

    // Determine user role
    var isFounder = frappe.boot.epms_is_founder;
    var isTeamLeader = frappe.boot.epms_is_team_leader;
    var isTeamMember = frappe.boot.epms_is_team_member;

    var html = '<div class="row">';

    if (isFounder) {
        html += render_founder_dashboard(data);
    } else if (isTeamLeader) {
        html += render_team_leader_dashboard(data);
    } else if (isTeamMember) {
        html += render_employee_dashboard(data);
    }

    html += '</div>';
    wrapper.html(html);

    // Initialize charts
    init_charts();
}

function render_founder_dashboard(data) {
    var html = '';

    // Stats Cards
    html += '<div class="col-md-3"><div class="card text-white bg-primary mb-3"><div class="card-body"><h5 class="card-title">Total Employees</h5><h2 class="card-text">' + (data.total_employees || 0) + '</h2></div></div></div>';
    html += '<div class="col-md-3"><div class="card text-white bg-success mb-3"><div class="card-body"><h5 class="card-title">Total Teams</h5><h2 class="card-text">' + (data.total_teams || 0) + '</h2></div></div></div>';
    html += '<div class="col-md-3"><div class="card text-white bg-info mb-3"><div class="card-body"><h5 class="card-title">Tasks Today</h5><h2 class="card-text">' + (data.tasks_today || 0) + '</h2></div></div></div>';
    html += '<div class="col-md-3"><div class="card text-white bg-warning mb-3"><div class="card-body"><h5 class="card-title">Pending Tasks</h5><h2 class="card-text">' + (data.pending_tasks || 0) + '</h2></div></div></div>';

    html += '<div class="row">';
    html += '<div class="col-md-3"><div class="card text-white bg-danger mb-3"><div class="card-body"><h5 class="card-title">Blocked Tasks</h5><h2 class="card-text">' + (data.blocked_tasks || 0) + '</h2></div></div></div>';
    html += '<div class="col-md-3"><div class="card text-white bg-secondary mb-3"><div class="card-body"><h5 class="card-title">Avg Performance</h5><h2 class="card-text">' + (data.avg_performance || 0) + '%</h2></div></div></div>';

    if (data.top_performer) {
        html += '<div class="col-md-3"><div class="card text-white bg-success mb-3"><div class="card-body"><h5 class="card-title">Top Performer</h5><p class="card-text">' + data.top_performer.employee_name + '</p><small>' + data.top_performer.overall_score + '</small></div></div></div>';
    }

    if (data.lowest_performer) {
        html += '<div class="col-md-3"><div class="card text-white bg-danger mb-3"><div class="card-body"><h5 class="card-title">Needs Improvement</h5><p class="card-text">' + data.lowest_performer.employee_name + '</p><small>' + data.lowest_performer.overall_score + '</small></div></div></div>';
    }

    html += '</div>';

    // Charts section
    html += '<div class="row"><div class="col-md-6"><div class="card mb-3"><div class="card-header">Performance Distribution</div><div class="card-body"><div id="performance-distribution-chart"></div></div></div></div>';
    html += '<div class="col-md-6"><div class="card mb-3"><div class="card-header">Monthly Trend</div><div class="card-body"><div id="monthly-trend-chart"></div></div></div></div></div>';

    return html;
}

function render_team_leader_dashboard(data) {
    var html = '';

    html += '<div class="col-md-3"><div class="card text-white bg-primary mb-3"><div class="card-body"><h5 class="card-title">Today\'s Tasks</h5><h2 class="card-text">' + (data.today_tasks || 0) + '</h2></div></div></div>';
    html += '<div class="col-md-3"><div class="card text-white bg-warning mb-3"><div class="card-body"><h5 class="card-title">Pending Tasks</h5><h2 class="card-text">' + (data.pending_tasks || 0) + '</h2></div></div></div>';
    html += '<div class="col-md-3"><div class="card text-white bg-success mb-3"><div class="card-body"><h5 class="card-title">Completed Tasks</h5><h2 class="card-text">' + (data.completed_tasks || 0) + '</h2></div></div></div>';
    html += '<div class="col-md-3"><div class="card text-white bg-info mb-3"><div class="card-body"><h5 class="card-title">Team Score</h5><h2 class="card-text">' + (data.team_score || 0) + '</h2></div></div></div>';

    html += '</div>';

    // Charts section
    html += '<div class="row"><div class="col-md-6"><div class="card mb-3"><div class="card-header">Employee Productivity</div><div class="card-body"><div id="employee-productivity-chart"></div></div></div></div>';
    html += '<div class="col-md-6"><div class="card mb-3"><div class="card-header">Task Status</div><div class="card-body"><div id="task-status-chart"></div></div></div></div></div>';

    return html;
}

function render_employee_dashboard(data) {
    var html = '';

    if (data.today_performance && data.today_performance.length > 0) {
        var today = data.today_performance[0];
        html += '<div class="col-md-3"><div class="card text-white bg-primary mb-3"><div class="card-body"><h5 class="card-title">Today\'s Rating</h5><h2 class="card-text">' + (today.daily_rating || 'N/A') + '</h2></div></div></div>';
    } else {
        html += '<div class="col-md-3"><div class="card text-white bg-secondary mb-3"><div class="card-body"><h5 class="card-title">Today\'s Rating</h5><h2 class="card-text">No Entry</h2></div></div></div>';
    }

    if (data.monthly_score) {
        html += '<div class="col-md-3"><div class="card text-white bg-success mb-3"><div class="card-body"><h5 class="card-title">Monthly Score</h5><h2 class="card-text">' + (data.monthly_score.overall_score || 0) + '</h2></div></div></div>';
        html += '<div class="col-md-3"><div class="card text-white bg-info mb-3"><div class="card-body"><h5 class="card-title">Completed Tasks</h5><h2 class="card-text">' + (data.monthly_score.tasks_completed || 0) + '</h2></div></div></div>';
        html += '<div class="col-md-3"><div class="card text-white bg-warning mb-3"><div class="card-body"><h5 class="card-title">Overall Grade</h5><h2 class="card-text">' + (data.monthly_score.final_grade || 'N/A') + '</h2></div></div></div>';
    }

    html += '</div>';

    // Charts section
    html += '<div class="row"><div class="col-md-6"><div class="card mb-3"><div class="card-header">Monthly Performance</div><div class="card-body"><div id="monthly-performance-chart"></div></div></div></div>';
    html += '<div class="col-md-6"><div class="card mb-3"><div class="card-header">Score Trend</div><div class="card-body"><div id="score-trend-chart"></div></div></div></div></div>';

    return html;
}

function init_charts() {
    // Initialize charts here
    // Charts will be loaded via frappe.chart
}
