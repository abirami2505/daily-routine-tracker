/* ── main.js ──────────────────────────────────────────────────
   Shared JS utilities for Routine Tracker
   ─────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Mobile nav toggle ──────────────────────────────────── */
  const navToggle = document.getElementById('navToggle');
  const headerNav = document.querySelector('.header-nav');
  if (navToggle && headerNav) {
    navToggle.addEventListener('click', () => {
      headerNav.classList.toggle('nav-open');
    });
    // Close when a link is clicked
    headerNav.addEventListener('click', e => {
      if (e.target.classList.contains('nav-link') || e.target.classList.contains('btn-logout')) {
        headerNav.classList.remove('nav-open');
      }
    });
  }

  /* ── Password toggle ────────────────────────────────────── */
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target;
      const input    = document.getElementById(targetId);
      if (!input) return;
      const isText   = input.type === 'text';
      input.type     = isText ? 'password' : 'text';
      btn.textContent = isText ? '👁' : '🙈';
    });
  });

  /* ── Auth form loader state ─────────────────────────────── */
  ['loginForm', 'registerForm'].forEach(id => {
    const form = document.getElementById(id);
    if (!form) return;
    form.addEventListener('submit', () => {
      const btn    = form.querySelector('button[type=submit]');
      const txtEl  = btn?.querySelector('.btn-text');
      const ldEl   = btn?.querySelector('.btn-loader');
      if (btn && txtEl && ldEl) {
        txtEl.hidden = true;
        ldEl.hidden  = false;
        btn.disabled = true;
      }
    });
  });

  /* ── Animate stat values on load ───────────────────────── */
  const statVals = document.querySelectorAll('.stat-val');
  statVals.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(8px)';
  });
  setTimeout(() => {
    statVals.forEach((el, i) => {
      setTimeout(() => {
        el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      }, i * 80);
    });
  }, 100);

  /* ── Animate progress bars in history table ────────────── */
  const bars = document.querySelectorAll('.progress-bar');
  bars.forEach(bar => {
    const target = bar.style.width;
    bar.style.width = '0';
    setTimeout(() => { bar.style.width = target; }, 200);
  });

  /* ── History table row hover highlight ─────────────────── */
  const hiRows = document.querySelectorAll('.history-row');
  hiRows.forEach(row => {
    const pct = parseFloat(row.dataset.pct || 0);
    // subtle left border colour based on score
    if (pct >= 80)      row.style.borderLeft = '3px solid #22c55e';
    else if (pct >= 60) row.style.borderLeft = '3px solid #FF7A00';
    else if (pct >= 40) row.style.borderLeft = '3px solid #f59e0b';
    else                row.style.borderLeft = '3px solid #ef4444';
  });

});
