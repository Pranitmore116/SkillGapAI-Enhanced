/**
 * theme-toggle.js
 * Handles the theme switching logic and persistence.
 */

document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('theme-toggle-btn');
    if (!toggleBtn) return;

    const moonIcon = toggleBtn.querySelector('.icon-moon');
    const sunIcon = toggleBtn.querySelector('.icon-sun');

    // Function to update the icons based on current theme
    const updateIcons = (isLight) => {
        if (isLight) {
            moonIcon.style.display = 'none';
            sunIcon.style.display = 'inline';
        } else {
            moonIcon.style.display = 'inline';
            sunIcon.style.display = 'none';
        }
    };

    // Initial icon state
    const isLightInitial = document.body.classList.contains('light-mode');
    updateIcons(isLightInitial);

    toggleBtn.addEventListener('click', () => {
        const isLight = document.body.classList.toggle('light-mode');
        document.documentElement.classList.toggle('light-mode');

        // Update user settings in localStorage
        const settings = JSON.parse(localStorage.getItem('user_settings') || '{}');
        settings.theme = isLight ? 'light' : 'dark';
        localStorage.setItem('user_settings', JSON.stringify(settings));

        updateIcons(isLight);
    });
});
