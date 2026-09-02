// Copyright (c) 2024, EPMS Team and contributors
// For license information, please see license.txt

frappe.pages['leaderboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Performance Leaderboard'),
        single_column: true
    });

    // Add filters
    page.add_field({
        fieldname: 'month',
        label: __('Month'),
        fieldtype: 'Select',
        options: '1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12',
        default: new Date().getMonth() + 1,
        onchange: function() {
            load_leaderboard();
        }
    });

    page.add_field({
        fieldname: 'year',
        label: __('Year'),
        fieldtype: 'Int',
        default: new Date().getFullYear(),
        onchange: function() {
            load_leaderboard();
        }
    });

    page.add_field({
        fieldname: 'team',
        label: __('Team'),
        fieldtype: 'Link',
        options: 'Team',
        onchange: function() {
            load_leaderboard();
        }
    });

    // Add refresh button
    page.add_button(__('Refresh'), function() {
        load_leaderboard();
    }, 'fa fa-refresh');

    // Load leaderboard
    load_leaderboard();
};

function load_leaderboard() {
    var month = cur_page.fields_dict.month.get_value();
    var year = cur_page.fields_dict.year.get_value();
    var team = cur_page.fields_dict.team.get_value();

    frappe.call({
        method: 'epms.epms.page.leaderboard.leaderboard.get_leaderboard_data',
        args: {
            month: month,
            year: year,
            team: team
        },
        callback: function(r) {
            if (r.message) {
                render_leaderboard(r.message);
            }
        }
    });
}

function render_leaderboard(data) {
    var wrapper = $('#page-leaderboard .page-content');
    wrapper.empty();

    if (!data || data.length === 0) {
        wrapper.html('<div class="text-center text-muted"><h4>No data available</h4></div>');
        return;
    }

    var html = '<div class="row">';

    // Top 3 podium
    html += '<div class="col-md-12 mb-4">';
    html += '<div class="card">';
    html += '<div class="card-header"><h5>🏆 Top Performers</h5></div>';
    html += '<div class="card-body">';

    if (data.length >= 3) {
        html += '<div class="row text-center">';
        html += '<div class="col-md-4"><div class="alert alert-secondary"><h2>🥈</h2><h5>' + data[1].employee_name + '</h5><h3>' + data[1].overall_score + '</h3><small>' + data[1].final_grade + '</small></div></div>';
        html += '<div class="col-md-4"><div class="alert alert-warning"><h2>🥇</h2><h5>' + data[0].employee_name + '</h5><h3>' + data[0].overall_score + '</h3><small>' + data[0].final_grade + '</small></div></div>';
        html += '<div class="col-md-4"><div class="alert alert-info"><h2>🥉</h2><h5>' + data[2].employee_name + '</h5><h3>' + data[2].overall_score + '</h3><small>' + data[2].final_grade + '</small></div></div>';
        html += '</div>';
    }

    html += '</div></div></div>';

    // Full leaderboard table
    html += '<div class="col-md-12">';
    html += '<div class="card">';
    html += '<div class="card-header"><h5>Full Leaderboard</h5></div>';
    html += '<div class="card-body">';
    html += '<table class="table table-striped table-hover">';
    html += '<thead><tr><th>Rank</th><th>Employee</th><th>Team</th><th>Score</th><th>Grade</th><th>Tasks</th><th>Productivity</th><th>Quality</th><th>Attendance</th></tr></thead>';
    html += '<tbody>';

    for (var i = 0; i < data.length; i++) {
        var row = data[i];
        var rowClass = '';
        if (i === 0) rowClass = 'table-warning';
        else if (i === 1) rowClass = 'table-secondary';
        else if (i === 2) rowClass = 'table-info';

        html += '<tr class="' + rowClass + '">';
        html += '<td>' + row.medal + '</td>';
        html += '<td><strong>' + row.employee_name + '</strong></td>';
        html += '<td>' + (row.team || '-') + '</td>';
        html += '<td><strong>' + row.overall_score + '</strong></td>';
        html += '<td>' + row.final_grade + '</td>';
        html += '<td>' + row.tasks_completed + '</td>';
        html += '<td>' + row.productivity_score + '</td>';
        html += '<td>' + row.quality_score + '</td>';
        html += '<td>' + row.attendance_score + '</td>';
        html += '</tr>';
    }

    html += '</tbody></table>';
    html += '</div></div></div>';

    html += '</div>';
    wrapper.html(html);
}
