// Theme Management System for AskUP
class ThemeManager {
    constructor() {
        this.config = window.themeConfig || {
            currentTheme: 'light',
            compactMode: false,
            animations: true,
            isAuthenticated: false
        };
        this.init();
    }
    
    init() {
        // Apply saved preferences
        this.applyTheme(this.getSavedTheme());
        this.applyCompactMode(this.getSavedCompactMode());
        this.applyAnimations(this.getSavedAnimations());
        
        // Add theme toggle to navbar if needed
        this.addThemeToggle();
    }
    
    getSavedTheme() {
        // Use server preference first, then localStorage
        return this.config.currentTheme || localStorage.getItem('askup-theme') || 'light';
    }
    
    getSavedCompactMode() {
        return this.config.compactMode || localStorage.getItem('askup-compact') === 'true';
    }
    
    getSavedAnimations() {
        return this.config.animations !== false && localStorage.getItem('askup-animations') !== 'false';
    }
    
    applyTheme(theme) {
        // Apply to both html and body elements for maximum coverage
        document.documentElement.setAttribute('data-theme', theme);
        document.body.setAttribute('data-theme', theme);
        
        // Also add as a class for CSS that might need it
        document.documentElement.className = document.documentElement.className.replace(/theme-\w+/g, '');
        document.documentElement.classList.add(`theme-${theme}`);
        
        localStorage.setItem('askup-theme', theme);
        
        // Update theme color meta tag for mobile browsers
        this.updateMetaThemeColor(theme);
        
        // Force a repaint to ensure styles are applied
        document.body.style.display = 'none';
        document.body.offsetHeight; // Trigger reflow
        document.body.style.display = '';
        
        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    }
    
    applyCompactMode(enabled) {
        document.documentElement.setAttribute('data-compact', enabled);
        localStorage.setItem('askup-compact', enabled);
    }
    
    applyAnimations(enabled) {
        document.documentElement.setAttribute('data-animations', enabled);
        localStorage.setItem('askup-animations', enabled);
    }
    
    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        const colors = {
            light: '#007bff',
            dark: '#212529',
            auto: window.matchMedia('(prefers-color-scheme: dark)').matches ? '#212529' : '#007bff'
        };
        
        metaThemeColor.setAttribute('content', colors[theme] || colors.light);
    }
    
    setTheme(theme) {
        this.applyTheme(theme);
        
        // Save to server if user is authenticated
        if (this.config.isAuthenticated) {
            this.saveToServer({ theme });
        }
    }
    
    setCompactMode(enabled) {
        this.applyCompactMode(enabled);
        
        if (this.config.isAuthenticated) {
            this.saveToServer({ compact_mode: enabled });
        }
    }
    
    setAnimations(enabled) {
        this.applyAnimations(enabled);
        
        if (this.config.isAuthenticated) {
            this.saveToServer({ animations: enabled });
        }
    }
    
    saveToServer(settings) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) return;
        
        const formData = new FormData();
        
        // Include current settings
        formData.append('theme', settings.theme || this.getSavedTheme());
        formData.append('compact_mode', settings.compact_mode !== undefined ? settings.compact_mode : this.getSavedCompactMode());
        formData.append('animations', settings.animations !== undefined ? settings.animations : this.getSavedAnimations());
        formData.append('csrfmiddlewaretoken', csrfToken);
        
        fetch('/users/settings/theme/', {
            method: 'POST',
            body: formData
        }).catch(error => {
            console.warn('Failed to save theme settings:', error);
        });
    }
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        return newTheme;
    }
    
    addThemeToggle() {
        // Add a theme toggle button to the navbar (optional)
        const navbar = document.querySelector('.navbar-nav');
        if (navbar && !document.getElementById('theme-toggle')) {
            const themeToggle = document.createElement('li');
            themeToggle.className = 'nav-item';
            themeToggle.innerHTML = `
                <button class="nav-link btn btn-link" id="theme-toggle" title="Toggle Theme">
                    <i class="fas fa-moon" id="theme-icon"></i>
                </button>
            `;
            
            const toggleBtn = themeToggle.querySelector('#theme-toggle');
            toggleBtn.addEventListener('click', () => {
                const newTheme = this.toggleTheme();
                this.updateThemeIcon(newTheme);
            });
            
            // Insert before the user dropdown or at the end
            const userDropdown = navbar.querySelector('.dropdown');
            if (userDropdown) {
                navbar.insertBefore(themeToggle, userDropdown);
            } else {
                navbar.appendChild(themeToggle);
            }
            
            // Set initial icon
            this.updateThemeIcon(this.getSavedTheme());
        }
    }
    
    updateThemeIcon(theme) {
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
    
    // Auto theme handling
    handleAutoTheme() {
        if (this.getSavedTheme() === 'auto') {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            const updateAutoTheme = () => {
                const effectiveTheme = mediaQuery.matches ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', effectiveTheme);
                this.updateMetaThemeColor('auto');
            };
            
            updateAutoTheme();
            mediaQuery.addEventListener('change', updateAutoTheme);
        }
    }
    
    // Preview theme temporarily
    previewTheme(theme) {
        document.documentElement.setAttribute('data-theme-preview', theme);
        
        // Show preview notification
        this.showPreviewNotification(theme);
        
        // Auto-remove preview after 10 seconds
        setTimeout(() => {
            this.stopPreview();
        }, 10000);
    }
    
    stopPreview() {
        document.documentElement.removeAttribute('data-theme-preview');
        const notification = document.querySelector('.theme-preview-notification');
        if (notification) {
            notification.remove();
        }
    }
    
    showPreviewNotification(theme) {
        // Remove existing notification
        const existing = document.querySelector('.theme-preview-notification');
        if (existing) existing.remove();
        
        const notification = document.createElement('div');
        notification.className = 'alert alert-info position-fixed theme-preview-notification';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        notification.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span><i class="fas fa-eye me-2"></i>Previewing ${theme} theme</span>
                <button class="btn btn-sm btn-outline-info ms-2" onclick="window.themeManager.stopPreview()">
                    Stop Preview
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.themeManager = new ThemeManager();
    
    // Handle auto theme
    window.themeManager.handleAutoTheme();
    
    // Add global theme toggle function
    window.toggleTheme = () => window.themeManager.toggleTheme();
    
    // Add theme preview function
    window.previewTheme = (theme) => window.themeManager.previewTheme(theme);
});

// Handle theme form submissions
document.addEventListener('submit', function(e) {
    if (e.target.closest('form') && e.target.querySelector('[name="theme"]')) {
        // Theme settings form submitted
        setTimeout(() => {
            // Reload theme after form submission
            if (window.themeManager) {
                const newTheme = document.querySelector('[name="theme"]:checked')?.value;
                if (newTheme) {
                    window.themeManager.applyTheme(newTheme);
                }
            }
        }, 100);
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
