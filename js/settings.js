/**
 * settings.js
 * Handles user preferences and theme management.
 */

'use strict';

const $ = id => document.getElementById(id);

document.addEventListener('DOMContentLoaded', () => {
    // 1. Session Check
    const sessionStr = localStorage.getItem('user_session');
    if (!sessionStr) {
        window.location.href = 'auth.html';
        return;
    }

    // 2. Load Existing Settings
    loadSettings();

    // 3. Theme Toggle Handling
    const themeToggle = $('themeToggle');
    themeToggle.addEventListener('change', () => {
        const isLight = themeToggle.checked;
        document.body.classList.toggle('light-mode', isLight);
        $('themeLabel').textContent = isLight ? 'Light Mode' : 'Dark Mode';
    });

    // 4. Form Submission
    $('settingsForm').addEventListener('submit', (e) => {
        e.preventDefault();
        saveSettings();
    });

    // 5. Cancel Button
    $('cancelBtn').addEventListener('click', () => {
        if (confirm('Discard unsaved changes?')) {
            window.location.href = 'dashboard.html';
        }
    });

    // 6. Logout
    $('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('user_session');
        window.location.href = 'auth.html';
    });
});

/**
 * Loads settings from localStorage and populates the form.
 */
function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('user_settings') || '{}');
    const session = JSON.parse(localStorage.getItem('user_session') || '{}');

    // Default to session email if name not set
    $('userNameInput').value = settings.name || session.email.split('@')[0];
    $('targetRoleInput').value = settings.targetRole || '';
    $('skillFocusSelect').value = settings.skillFocus || 'frontend';

    // Theme
    const isLight = settings.theme === 'light';
    $('themeToggle').checked = isLight;
    if (isLight) {
        document.body.classList.add('light-mode');
        $('themeLabel').textContent = 'Light Mode';
    }
}

/**
 * Saves form data specifically to user_settings key.
 */
function saveSettings() {
    const settings = {
        name: $('userNameInput').value,
        targetRole: $('targetRoleInput').value,
        skillFocus: $('skillFocusSelect').value,
        theme: $('themeToggle').checked ? 'light' : 'dark'
    };

    localStorage.setItem('user_settings', JSON.stringify(settings));

    // Show success feedback
    const saveBtn = document.querySelector('button[type="submit"]');
    const originalText = saveBtn.textContent;
    saveBtn.textContent = 'Settings Saved! ✓';
    saveBtn.style.background = 'var(--success)';

    setTimeout(() => {
        saveBtn.textContent = originalText;
        saveBtn.style.background = '';
        window.location.href = 'dashboard.html';
    }, 1200);
}
