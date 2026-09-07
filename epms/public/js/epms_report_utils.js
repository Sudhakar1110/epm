/* EPMS Report Utilities — shared formatters and export buttons */

window.epms_report_utils = {
    badge: function(value) {
        if (!value) return '';
        var cls = 'epms-badge-info';
        var v = String(value).toLowerCase();
        if (['on track', 'excellent', 'very good', 'completed'].indexOf(v) > -1) cls = 'epms-badge-success';
        else if (['needs attention', 'good', 'average', 'in progress'].indexOf(v) > -1) cls = 'epms-badge-warning';
        else if (['at risk', 'needs improvement', 'blocked'].indexOf(v) > -1) cls = 'epms-badge-danger';
        else if (['pending'].indexOf(v) > -1) cls = 'epms-badge-muted';
        return '<span class="epms-badge ' + cls + '">' + value + '</span>';
    },

    progress: function(value) {
        if (value === null || value === undefined || value === '') return '';
        var pct = parseFloat(value) || 0;
        var cls = 'blue';
        if (pct >= 80) cls = 'green';
        else if (pct >= 60) cls = 'yellow';
        else cls = 'red';
        return '<div class="epms-progress">' +
            '<div class="epms-progress-track"><div class="epms-progress-fill ' + cls + '" style="width:' + Math.min(pct, 100) + '%"></div></div>' +
            '<span class="epms-progress-label">' + pct.toFixed(1) + '%</span></div>';
    },

    priority: function(value) {
        if (!value) return '';
        var v = String(value).toLowerCase();
        var cls = 'epms-priority-medium';
        if (v === 'low') cls = 'epms-priority-low';
        else if (v === 'medium') cls = 'epms-priority-medium';
        else if (v === 'high') cls = 'epms-priority-high';
        else if (v === 'critical') cls = 'epms-priority-critical';
        return '<span class="epms-priority ' + cls + '">' + value + '</span>';
    },

    addExportButtons: function(report) {
        report.page.add_inner_button(__('Export Excel'), function() {
            frappe.query_report.export_report('xlsx');
        });
        report.page.add_inner_button(__('Export PDF'), function() {
            frappe.query_report.export_report('pdf');
        });
        report.page.add_inner_button(__('Print'), function() {
            frappe.query_report.print_report();
        });
    },

    injectPrintLayout: function() {
        if (document.querySelector('.epms-print-header')) return;
        var title = document.querySelector('.page-head .page-title, .report-title, h1');
        var titleText = title ? title.textContent : 'Report';
        var header = document.createElement('div');
        header.className = 'epms-print-header';
        header.innerHTML = '<img class="epms-print-logo" src="/assets/epms/images/bizaxl_logo.png" alt="EPMS">' +
            '<div><div class="epms-print-title">EPMS — Employee Performance Management</div>' +
            '<div class="epms-print-subtitle">' + titleText + ' &bull; ' + new Date().toLocaleDateString() + '</div></div>';
        var footer = document.createElement('div');
        footer.className = 'epms-print-footer';
        footer.innerHTML = 'EPMS Portal &bull; Generated on ' + new Date().toLocaleString();
        var wrapper = document.querySelector('.page-wrap, .report-wrapper, .frappe-control');
        if (wrapper) {
            wrapper.insertBefore(header, wrapper.firstChild);
            wrapper.appendChild(footer);
        }
    }
};

document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.frappe-report-wrapper, .report-page')) {
        epms_report_utils.injectPrintLayout();
    }
});
