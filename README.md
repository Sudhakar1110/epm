# EPMS — Employee Performance Management System

Employee Performance Management System app for **ERPNext / Frappe v15**.

---

## What's Included

| Component | Count | Details |
|-----------|-------|---------|
| **Doctypes** | 8 | Team, Team Member Mapping, Daily Performance (submittable), Daily Performance Subtask (child), Pending Task (submittable), Performance Scorecard (submittable), Employee KPI, EPMS Settings (single) |
| **Reports** | 10 | Daily Performance, Monthly Performance, Employee Wise, Team Wise, Pending Task, Top Performers, Low Performers, Monthly KPI, Leaderboard, Daily Summary |
| **Portal Pages** | 15 | Dashboard, My Day, Teams, Team Work, Performance, Team Scoreboard, Scorecards, Reports, Notifications, Calendar, Search, Profile, Import, Settings, Audit |
| **Scheduler Jobs** | 9 | Daily scorecards/reminders, Weekly summaries/alerts/reports, Monthly summary |
| **Roles** | 3 | EPMS Founder, EPMS Team Leader, EPMS Team Member |

---

## Installation

```bash
# 1. Get the app
bench get-app https://github.com/Sudhakar1110/epm.git

# 2. Install on your site
bench --site <your-site-name> install-app epms

# 3. Migrate (syncs doctypes, reports, workspace, charts, notifications)
bench --site <your-site-name> migrate

# 4. Build assets
bench build --app epms
```

After installation, assign **EPMS Founder**, **EPMS Team Leader**, or **EPMS Team Member** roles to users.

---

## Roles & Permissions

| Feature | EPMS Founder | EPMS Team Leader | EPMS Team Member |
|---------|:---:|:---:|:---:|
| **Dashboard** (overview stats) | Yes | — | — |
| **My Day** (view team login status) | Yes | Yes | — |
| **Teams** (view all teams) | Yes | Yes | Yes |
| **Team Work** (log work for members) | — | Yes | — |
| **Performance** (employee performance view) | Yes | — | — |
| **Scoreboard** (team rankings) | Yes | — | — |
| **Scorecards** (monthly scorecards) | Yes | — | — |
| **Reports** (10 report types) | Yes | — | — |
| **Notifications** | Yes | Yes | Yes |
| **Calendar** | Yes | Yes | Yes |
| **Import** (CSV bulk import) | Yes | — | — |
| **Audit** (change log) | Yes | — | — |
| **Settings** (EPMS configuration) | Yes | — | — |
| **Submit own daily work** | Yes | Yes | Yes |
| **Submit work for team members** | Yes | Yes | — |
| **Create/manage teams** | Yes | Read-only | Read-only |
| **Create scorecards** | Yes | — | — |
| **Assign pending tasks** | Yes | Yes (own team) | — |

---

## Core Workflow

### 1. Team Setup

```
Founder creates Team → Assigns Team Leader → Adds Team Members via Team Member Mapping
```

- **Founder** creates teams and assigns leaders
- **Team Leaders** can add/remove members in their own team
- Each team member is linked to a User account via `Team Member Mapping`

### 2. Daily Performance Tracking

```
Team Member (or Leader) submits Daily Performance → Scorecard auto-generated
```

**Daily flow:**
1. Team Member logs into portal → navigates to My Day or Team Work
2. Fills in: task title, status, hours worked, completion %, rating, quality score
3. Submits the entry (creates a `Daily Performance` document, docstatus=1)
4. On submit, a `Performance Scorecard` is automatically created/updated for the current month

**Team Leader flow:**
1. Leader navigates to **Team Work** page
2. Sees all team members with their submission status (Pending/Completed)
3. Can submit daily work on behalf of any team member

### 3. Scorecard Generation

```
Daily Performance entries → calculate scores → generate monthly Performance Scorecard
```

Scorecards are calculated from all Daily Performance entries for an employee in a given month:

| Metric | Weight | Calculation |
|--------|--------|-------------|
| **Productivity Score** | 30% | Based on tasks completed, hours worked, completion % |
| **Quality Score** | 30% | Based on daily rating and quality score averages |
| **Attendance Score** | 20% | Days with entries / working days (weekdays only) |
| **Completion %** | 20% | Tasks completed / total tasks |

**Grading** (configurable in EPMS Settings):
- Excellent: ≥ 90
- Very Good: ≥ 80
- Good: ≥ 70
- Average: ≥ 60
- Needs Improvement: < 60

**Performance Status:**
- On Track: ≥ 80
- Needs Attention: ≥ 60
- At Risk: < 60

### 4. Pending Tasks

```
Team Leader/Founder creates Pending Task → Assigned member works on it → Status updated
```

- Tasks have: employee, priority (Low/Medium/High/Critical), expected completion date, status
- Statuses: Pending → In Progress → Completed (or Blocked)
- Overdue tasks (past expected_completion) are auto-marked as Blocked by daily scheduler
- Reminders sent for tasks due tomorrow

### 5. Automated Scheduler Jobs

| Schedule | Job | Description |
|----------|-----|-------------|
| Daily | `daily_tasks` | Updates overdue tasks, sends reminders, daily performance reminders |
| Daily | `generate_monthly_scorecards` | Auto-generates scorecards for current + previous month |
| Daily | `recalculate_scorecards` | Recalculates current month scorecards with latest data |
| Weekly | `send_weekly_summary` | Emails performance summary to founders and team leaders |
| Weekly | `send_low_performance_alerts` | Alerts for employees scoring below threshold |
| Weekly | `send_email_reports` | Emails weekly report with top performers and stats |
| Monthly | `send_monthly_summary` | Emails monthly summary |

---

## Portal Pages

| URL | Page | Description |
|-----|------|-------------|
| `/epms` | Dashboard | Stats overview, score distribution, today's work (Founder only) |
| `/epms/my-day` | My Day | Team member login status, daily entries (Founder/Leader) |
| `/epms/teams` | Teams | List of all active teams |
| `/epms/team?team=<name>` | Team Detail | Members, manage options (Founder/Leader) |
| `/epms/team-work` | Team Work | Log work for team members (Leader only) |
| `/epms/performance` | Performance | Employee performance data (Founder only) |
| `/epms/team-scoreboard` | Scoreboard | Team rankings by score (Founder only) |
| `/epms/scorecards` | Scorecards | Monthly scorecards list (Founder only) |
| `/epms/scorecard?employee=<user>` | Scorecard Detail | Individual scorecard breakdown |
| `/epms/reports` | Reports | List of 10 available reports |
| `/epms/report?report=<slug>` | Report Viewer | View any report with filters |
| `/epms/notifications` | Notifications | Notification log |
| `/epms/calendar` | Calendar | Performance entries calendar view |
| `/epms/search` | Search | Search teams, tasks, users |
| `/epms/profile` | Profile | User profile and settings |
| `/epms/import` | Import | CSV bulk import (Founder only) |
| `/epms/settings` | Settings | EPMS configuration (Founder only) |
| `/epms/audit` | Audit | Change log (Founder/Leader only) |

---

## Reports

| Report | Slug | Data Source |
|--------|------|-------------|
| Daily Performance Report | `daily-performance` | Daily Performance entries |
| Monthly Performance Report | `monthly-performance` | Performance Scorecards |
| Employee Wise Report | `employee-wise` | Daily Performance (grouped by employee) |
| Team Wise Report | `team-wise` | Daily Performance + Scorecards (grouped by team) |
| Pending Task Report | `pending-task` | Daily Performance Subtasks |
| Top Performers | `top-performers` | Performance Scorecards (top scores) |
| Low Performers | `low-performers` | Performance Scorecards (low scores) |
| Monthly KPI Report | `monthly-kpi` | Scorecards (KPI metrics per team) |
| Leaderboard Report | `leaderboard` | Performance Scorecards (rankings) |
| Daily Summary Report | `daily-summary` | Daily Performance (aggregated by employee) |

All portal reports accept `month` and `year` filters. Reports can be exported to CSV.

---

## Configuration (EPMS Settings)

Accessible at `/epms/settings` (Founder only):

| Setting | Default | Description |
|---------|---------|-------------|
| Auto-generate scorecards | On | Auto-create scorecards via scheduler |
| Scorecard day | 1 | Day of month to generate scorecards |
| Send daily reminders | On | Remind team members to log work |
| Send weekly summary | On | Email weekly summary to leaders |
| Send monthly summary | On | Email monthly summary |
| Excellent threshold | 90 | Score threshold for "Excellent" grade |
| Very Good threshold | 80 | Score threshold for "Very Good" grade |
| Good threshold | 70 | Score threshold for "Good" grade |
| Average threshold | 60 | Score threshold for "Average" grade |
| Low performance threshold | 60 | Alert threshold for low performers |

---

## API Endpoints

All portal API endpoints are whitelisted and require authentication:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `get_portal_stats` | GET | Dashboard statistics |
| `get_portal_teams` | GET | List active teams |
| `get_portal_team` | GET | Team detail + members |
| `get_portal_scorecards` | GET | Current month scorecards |
| `get_portal_tasks` | GET | Pending tasks |
| `get_portal_daily_work` | GET | Today's work entries |
| `get_portal_notifications` | GET | Notification log |
| `set_portal_notifications_read` | POST | Mark notifications read |
| `create_portal_team` | POST | Create a new team |
| `add_portal_team_member` | POST | Add member to team |
| `remove_portal_team_member` | POST | Deactivate team member |
| `set_portal_team_leader` | POST | Change team leader |
| `submit_portal_daily_performance` | POST | Submit own daily work |
| `submit_team_member_daily_work` | POST | Submit work for team member |
| `create_portal_scorecard` | POST | Create a scorecard |
| `generate_team_scorecards` | POST | Bulk generate scorecards for team |
| `create_portal_pending_task` | POST | Create a pending task |
| `update_portal_task` | POST | Update task status/remarks |
| `import_portal_csv` | POST | Bulk import users/tasks via CSV |
| `portal_save_settings` | POST | Save EPMS Settings |
| `export_portal_report_csv` | GET | Export report as CSV |
| `export_portal_scorecards_csv` | GET | Export scorecards as CSV |
| `update_portal_profile` | POST | Update user profile |

---

## Doctypes

### Team
- `team_name` — Display name
- `team_leader` — Link to User (Team Leader)
- `total_members` — Auto-calculated count
- `status` — Active/Inactive

### Team Member Mapping
- `employee` — Link to Employee
- `user` — Link to User
- `employee_name` — Fetch from Employee
- `team` — Link to Team
- `status` — Active/Inactive

### Daily Performance (Submittable)
- `date` — Entry date
- `team` — Link to Team
- `employee` — Link to User
- `task_title`, `task_description`, `priority`, `task_status`, `work_type`
- `expected_hours`, `actual_hours`, `completion_percentage`
- `daily_rating`, `quality_score`
- `remarks`, `challenges`, `next_day_plan`
- `subtasks` — Child table (Daily Performance Subtask)

### Pending Task (Submittable)
- `employee` — Link to User
- `task` — Task description
- `priority` — Low/Medium/High/Critical
- `current_status` — Pending/In Progress/Completed/Blocked
- `assigned_date`, `expected_completion`, `completion_date`

### Performance Scorecard (Submittable)
- `employee`, `team`, `month`, `year`
- `total_working_days`, `tasks_completed`, `pending_tasks`, `completed_percentage`
- `average_rating`, `average_quality`
- `productivity_score`, `quality_score`, `attendance_score`
- `overall_score`, `final_grade`, `performance_status`

### EPMS Settings (Single)
- Scheduler toggles and grade thresholds (see Configuration section)

---

## Hooks

| Hook | Function |
|------|----------|
| `before_migrate` | Clean broken data, ensure Module Def |
| `after_install` | Create roles, workspace, permissions |
| `after_migrate` | Rebuild workspace |
| `extend_bootinfo` | Add EPMS roles/teams to boot session |
| `has_permission` | Data-level isolation for all doctypes |
| `doc_events` | Daily Performance (before_insert, validate, on_submit, on_cancel), Performance Scorecard (on_submit), Team Member Mapping (on_update), Pending Task (via class) |

---

## Notes

- Requires ERPNext (`required_apps = ["erpnext"]`).
- Version: 15.0.1
- Portal pages are served at `/epms/*` routes
- All portal pages require authentication (redirected to login if not authenticated)
- Grade thresholds are configurable via EPMS Settings
- Scorecards are auto-generated on Daily Performance submit and via scheduler
