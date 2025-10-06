document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('mode-toggle');
    const key = 'labang-mode';

    function applyMode(mode) {
        const html = document.documentElement;
        if (mode === 'light') {
            html.classList.add('light');
            btn.textContent = 'Dark mode';
            btn.setAttribute('aria-pressed','true');
        } else {
            html.classList.remove('light');
            btn.textContent = 'Light mode';
            btn.setAttribute('aria-pressed','false');
        }
    }

    // Initialize mode
    const saved = localStorage.getItem(key);
    if (saved) {
        applyMode(saved);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        applyMode('light');
    } else {
        applyMode('dark');
    }

    // Toggle
    btn.addEventListener('click', () => {
        const next = document.documentElement.classList.contains('light') ? 'dark' : 'light';
        localStorage.setItem(key, next);
        applyMode(next);
    });
});
