/**
 * user-dashboard.js
 * Logic for the User Dashboard trend charts and profile data.
 */

'use strict';

const $ = id => document.getElementById(id);

const getHistory = () => {
    try {
        return JSON.parse(localStorage.getItem('skillgap_history') || '[]');
    } catch (e) { return []; }
};

const deleteRecord = (id) => {
    const history = getHistory().filter(r => r.id !== id);
    localStorage.setItem('skillgap_history', JSON.stringify(history));
    return history;
};

document.addEventListener('DOMContentLoaded', () => {
    // 1. Session Check
    const sessionStr = localStorage.getItem('user_session');
    if (!sessionStr) {
        window.location.href = 'auth.html';
        return;
    }

    const session = JSON.parse(sessionStr);

    // 2. Populate Profile
    const settings = JSON.parse(localStorage.getItem('user_settings') || '{}');
    const displayName = settings.name || session.email.split('@')[0];
    if ($('userName')) $('userName').textContent = displayName;
    if ($('welcomeName')) $('welcomeName').textContent = displayName;
    if ($('userEmail')) $('userEmail').textContent = session.email;

    // Update target role if present in summary
    if (settings.targetRole && document.querySelector('.summary-row')) {
        const lastAnalysisCard = document.querySelector('.mini-card .val').parentElement;
        const roleLabel = lastAnalysisCard.querySelector('.lbl:last-child');
        if (roleLabel) roleLabel.textContent = `Target: ${settings.targetRole}`;
    }

    if ($('userInitial')) {
        const nameSource = settings.name || session.email;
        const initial = nameSource.charAt(0).toUpperCase();
        $('userInitial').textContent = initial;
    }

    // 3. Load & Render History
    updateHistoryUI();

    // 4. Render Trend Chart
    renderTrendChart();

    // 5. Clear History Handler
    if ($('clearHistoryBtn')) {
        $('clearHistoryBtn').addEventListener('click', () => {
            if (confirm('Are you sure you want to clear all analysis history?')) {
                localStorage.removeItem('skillgap_history');
                updateHistoryUI();
                renderTrendChart();
            }
        });
    }

    // 6. Logout Handler
});

/**
 * Renders the real history table and updates summary stats.
 */
function updateHistoryUI() {
    const history = getHistory();
    const tableBody = $('historyTableBody');
    if (!tableBody) return;

    // Update Profile Stats
    const avg = history.length > 0
        ? Math.round(history.reduce((acc, r) => acc + r.matchPct, 0) / history.length)
        : 0;

    if ($('totalAnalyses')) $('totalAnalyses').textContent = history.length;
    if ($('avgScore')) $('avgScore').textContent = avg + '%';

    // Update Table
    if (history.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--t3); padding:3rem;">No history found. Try your first analysis!</td></tr>';
        return;
    }

    tableBody.innerHTML = history.map(record => {
        const gradeClass = record.matchPct >= 80 ? 'badge-high' : record.matchPct >= 50 ? 'badge-med' : 'badge-low';
        return `
            <tr data-id="${record.id}">
                <td>${record.date}</td>
                <td>${record.role}</td>
                <td><span class="status-badge ${gradeClass}">${record.matchPct}%</span></td>
                <td style="color: var(--t2);">${record.atsPct}%</td>
                <td>
                    <button class="btn-ghost btn-sm delete-entry" style="color:var(--danger);">Delete</button>
                </td>
            </tr>
        `;
    }).join('');

    // Bind Delete Buttons
    tableBody.querySelectorAll('.delete-entry').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const row = e.target.closest('tr');
            const id = parseInt(row.dataset.id);
            if (confirm('Delete this record?')) {
                deleteRecord(id);
                updateHistoryUI();
                renderTrendChart(); // Refresh chart with new data
            }
        });
    });
}

/**
 * Renders a line chart showing Match Score improvement over time.
 */
function renderTrendChart() {
    const ctx = $('trendChart');
    if (!ctx) return;

    // Clear existing chart if any (chart.js 4+ needs cleanup)
    const existingChart = Chart.getChart(ctx);
    if (existingChart) existingChart.destroy();

    const history = [...getHistory()].reverse(); // cronological order

    if (history.length === 0) {
        ctx.parentElement.innerHTML = '<div style="height:100%; display:flex; align-items:center; justify-content:center; color:var(--t3);">Analyis history needed for trend data.</div>';
        return;
    }

    const data = {
        labels: history.map(r => r.date),
        datasets: [{
            label: 'Match Score %',
            data: history.map(r => r.matchPct),
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#6366f1',
            pointRadius: 5,
            pointHoverRadius: 8
        }]
    };

    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    };

    new Chart(ctx, config);
}
