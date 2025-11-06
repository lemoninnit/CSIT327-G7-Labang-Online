document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('mode-toggle');
    const key = 'labang-theme-mode';

    function applyMode(mode) {
        const html = document.documentElement;
        if (mode === 'light') {
            html.classList.add('light');
            if (btn) {
                btn.textContent = 'Dark mode';
                btn.setAttribute('aria-pressed','true');
            }
        } else {
            html.classList.remove('light');
            if (btn) {
                btn.textContent = 'Light mode';
                btn.setAttribute('aria-pressed','false');
            }
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

    // Toggle (only if button exists on the page)
    if (btn) {
        btn.addEventListener('click', () => {
            const next = document.documentElement.classList.contains('light') ? 'dark' : 'light';
            localStorage.setItem(key, next);
            applyMode(next);
        });
    }
});

// Auto-dismiss messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.msg');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000); // 5 seconds
    });
});