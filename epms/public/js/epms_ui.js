/* EPMS Portal UI — 10 UX features */
(function () {
  'use strict';

  /* ================================================================
     1. DARK MODE
     ================================================================ */
  function initDarkMode() {
    var saved = localStorage.getItem('epms-theme');
    if (saved === 'dark') document.documentElement.setAttribute('data-theme', 'dark');

    var btn = document.querySelector('.theme-toggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      if (isDark) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('epms-theme', 'light');
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
      } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('epms-theme', 'dark');
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
      }
    });
    // Set initial icon
    if (saved === 'dark') {
      btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    }
  }

  /* ================================================================
     2. GLOBAL SEARCH / COMMAND PALETTE (Ctrl+K)
     ================================================================ */
  function initSearchPalette() {
    var mask = document.querySelector('.search-palette-mask');
    var input = document.querySelector('.search-palette-input');
    var results = document.querySelector('.search-palette-results');
    if (!mask || !input || !results) return;

    var navItems = [
      { label: 'Dashboard', desc: 'Performance overview', url: '/app/epms' },
      { label: 'My Day', desc: 'Log today\'s work', url: '/app/epms-my-day' },
      { label: 'My Performance', desc: 'View your scores', url: '/app/epms-my-performance' },
      { label: 'Task Board', desc: 'Manage tasks', url: '/app/epms-task-board' },
      { label: 'Team Work', desc: 'Team activities', url: '/app/epms-team-work' },
      { label: 'Leaderboard', desc: 'Rankings & scores', url: '/app/epms-leaderboard' },
      { label: 'Scorecards', desc: 'Monthly scorecards', url: '/app/epms-scorecards' },
      { label: 'Calendar', desc: 'Task calendar view', url: '/app/epms-calendar' },
      { label: 'Reports', desc: 'Performance reports', url: '/app/epms-report' },
      { label: 'Settings', desc: 'Configure thresholds', url: '/app/epms-settings' }
    ];

    function open() { mask.classList.add('open'); input.value = ''; input.focus(); render(''); }
    function close() { mask.classList.remove('open'); }

    function render(q) {
      var filtered = navItems;
      if (q) {
        var lq = q.toLowerCase();
        filtered = navItems.filter(function (n) {
          return n.label.toLowerCase().indexOf(lq) !== -1 || n.desc.toLowerCase().indexOf(lq) !== -1;
        });
      }
      if (!filtered.length) {
        results.innerHTML = '<div class="search-palette-empty">No results found</div>';
        return;
      }
      results.innerHTML = filtered.map(function (n, i) {
        return '<a class="search-palette-item' + (i === 0 ? ' active' : '') + '" href="' + n.url + '">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>' +
          '<div class="search-palette-item-text"><div class="search-palette-item-label">' + n.label + '</div><div class="search-palette-item-desc">' + n.desc + '</div></div></a>';
      }).join('');
    }

    input.addEventListener('input', function () { render(this.value); });

    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); open(); }
      if (e.key === 'Escape' && mask.classList.contains('open')) close();
    });
    mask.addEventListener('click', function (e) { if (e.target === mask) close(); });

    // Open palette button
    document.addEventListener('click', function (e) {
      var btn = e.target.closest('.search-palette-trigger');
      if (btn) { e.preventDefault(); open(); }
    });
  }

  /* ================================================================
     3. TOAST NOTIFICATIONS
     ================================================================ */
  function createToastContainer() {
    if (!document.querySelector('.toast-container')) {
      var c = document.createElement('div');
      c.className = 'toast-container';
      document.body.appendChild(c);
    }
  }

  window.epmsToast = function (msg, type, duration) {
    createToastContainer();
    type = type || 'info';
    duration = duration || 4000;
    var icons = { success: '\u2713', error: '\u2717', warning: '\u26A0', info: 'i' };
    var t = document.createElement('div');
    t.className = 'toast toast-' + type;
    t.innerHTML = '<span class="toast-icon">' + (icons[type] || icons.info) + '</span>' +
      '<span style="flex:1">' + msg + '</span>' +
      '<button class="toast-close">&times;</button>';
    document.querySelector('.toast-container').appendChild(t);
    t.querySelector('.toast-close').addEventListener('click', function () { dismiss(t); });
    setTimeout(function () { dismiss(t); }, duration);
    function dismiss(el) {
      if (!el.parentNode) return;
      el.classList.add('toast-out');
      setTimeout(function () { el.remove(); }, 300);
    }
  };

  // Override window.alert to use toast
  window._originalAlert = window.alert;
  window.alert = function (msg) { window.epmsToast(msg, 'info', 5000); };

  /* ================================================================
     4. SKELETON LOADING (utility)
     ================================================================ */
  window.epmsSkeleton = function (el, lines) {
    lines = lines || 3;
    var h = '';
    for (var i = 0; i < lines; i++) {
      var w = ['w-60', 'w-80', 'w-40', 'w-100'][i % 4];
      h += '<div class="skeleton skeleton-text ' + w + '"></div>';
    }
    el.innerHTML = h;
  };

  /* ================================================================
     5. SORTABLE TABLES
     ================================================================ */
  function initSortableTables() {
    document.querySelectorAll('table.table').forEach(function (table) {
      var headers = table.querySelectorAll('th');
      headers.forEach(function (th, colIdx) {
        th.classList.add('sortable');
        th.addEventListener('click', function () {
          var tbody = table.querySelector('tbody');
          if (!tbody) return;
          var rows = Array.from(tbody.querySelectorAll('tr:not(.expand-row)'));
          var isAsc = th.classList.contains('sort-asc');
          headers.forEach(function (h) { h.classList.remove('sort-asc', 'sort-desc'); });
          th.classList.add(isAsc ? 'sort-desc' : 'sort-asc');
          var dir = isAsc ? -1 : 1;
          rows.sort(function (a, b) {
            var av = (a.cells[colIdx] ? a.cells[colIdx].textContent.trim() : '').toLowerCase();
            var bv = (b.cells[colIdx] ? b.cells[colIdx].textContent.trim() : '').toLowerCase();
            var an = parseFloat(av), bn = parseFloat(bv);
            if (!isNaN(an) && !isNaN(bn)) return (an - bn) * dir;
            return av.localeCompare(bv) * dir;
          });
          rows.forEach(function (r) { tbody.appendChild(r); });
          // Re-attach expand rows after sorted rows
          rows.forEach(function (r) {
            var exp = r.nextElementSibling;
            if (exp && exp.classList.contains('expand-row')) tbody.appendChild(exp);
          });
        });
      });
    });
  }

  /* ================================================================
     7. ANIMATED NUMBER COUNTERS
     ================================================================ */
  function initCounters() {
    document.querySelectorAll('.stat-value[data-count]').forEach(function (el) {
      var target = parseFloat(el.getAttribute('data-count'));
      var duration = 800;
      var start = 0;
      var startTime = null;

      function animate(time) {
        if (!startTime) startTime = time;
        var progress = Math.min((time - startTime) / duration, 1);
        var eased = 1 - Math.pow(1 - progress, 3);
        var current = Math.round(start + (target - start) * eased);
        el.textContent = current;
        if (progress < 1) requestAnimationFrame(animate);
      }
      requestAnimationFrame(animate);
    });
  }

  /* ================================================================
     8. EXPANDABLE TABLE ROWS
     ================================================================ */
  function initExpandableRows() {
    document.querySelectorAll('table.table tbody tr.expandable').forEach(function (row) {
      row.addEventListener('click', function () {
        var expandRow = row.nextElementSibling;
        if (!expandRow || !expandRow.classList.contains('expand-row')) return;
        var isOpen = expandRow.classList.toggle('open');
        row.classList.toggle('expanded', isOpen);
      });
    });
  }

  /* ================================================================
     9. AUTO-SAVE DRAFTS
     ================================================================ */
  function initAutoSave() {
    var forms = document.querySelectorAll('[data-autosave]');
    forms.forEach(function (form) {
      var key = 'epms-draft-' + (form.getAttribute('data-autosave') || 'default');
      var indicator = form.querySelector('.draft-indicator');

      // Restore saved values
      try {
        var saved = JSON.parse(localStorage.getItem(key));
        if (saved) {
          Object.keys(saved).forEach(function (fieldName) {
            var field = form.querySelector('[name="' + fieldName + '"]');
            if (field) field.value = saved[fieldName];
          });
          if (indicator) indicator.classList.add('visible');
        }
      } catch (e) { /* ignore */ }

      // Save on input/change
      form.addEventListener('input', saveDraft);
      form.addEventListener('change', saveDraft);

      function saveDraft() {
        var data = {};
        form.querySelectorAll('input, select, textarea').forEach(function (f) {
          if (f.name) data[f.name] = f.value;
        });
        localStorage.setItem(key, JSON.stringify(data));
        if (indicator) {
          indicator.classList.add('visible');
          indicator.querySelector('.draft-time') && (indicator.querySelector('.draft-time').textContent = new Date().toLocaleTimeString());
        }
      }
    });

    // Expose clear function
    window.epmsClearDraft = function (formId) {
      var key = 'epms-draft-' + (formId || 'default');
      localStorage.removeItem(key);
      window.epmsToast('Draft cleared', 'info', 2000);
    };
  }

  /* ================================================================
     INIT ALL
     ================================================================ */
  document.addEventListener('DOMContentLoaded', function () {
    initDarkMode();
    initSearchPalette();
    initSortableTables();
    initCounters();
    initExpandableRows();
    initAutoSave();
  });
})();
