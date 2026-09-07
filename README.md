# EPMS — Employee Performance Management System

Employee Performance Management System app for **ERPNext / Frappe v15**.

## What's included

This app ships with:

- **8 Doctypes**: Team, Team Member Mapping, Daily Performance (submittable), Daily Performance Subtask (child table), Pending Task (submittable), Performance Scorecard (submittable), Employee KPI, EPMS Settings (single)
- **9 Reports**: Daily Performance Report, Monthly Performance Report, Employee Wise Report, Team Wise Report, Pending Task Report, Top Performers, Low Performers, Monthly KPI Report, Leaderboard Report
- **Workspace**: "Employee Performance Management" with shortcuts/links to all doctypes and reports
- **6 Dashboard Charts**, **9 Notifications**, **2 Print Formats**, and **2 custom pages** (EPMS Dashboard, Leaderboard)

## Installation

On your bench (Frappe v15):

```bash
# 1. Get the app (single main branch)
bench get-app https://github.com/Sudhakar1110/epm.git

# 2. Install on your site
bench --site <your-site-name> install-app epms

# 3. Migrate (syncs doctypes, reports, workspace, charts, notifications)
bench --site <your-site-name> migrate

# 4. Build assets (so /assets/epms/css/epms.css and /assets/epms/js/epms.js load)
bench build --app epms
```

After installation, assign the **EPMS Founder**, **EPMS Team Leader**, or **EPMS Team Member** roles to users. The "Employee Performance Management" workspace appears in the module list on the desk.

> **If doctypes do not appear after install:** run `bench --site <site> migrate` again, then hard-refresh the browser (Ctrl+Shift+R). Previous failed installs leave orphaned module records — this app's `before_install` hook cleans those up automatically on reinstall.

## Notes

- Requires ERPNext (`required_apps = ["erpnext"]`).
- Version: 15.0.1