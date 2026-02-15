// TriNetra UI Improvements Module

class UIEnhancements {
    constructor() {
        this.toastContainer = null;
        this.init();
    }

    init() {
        // Create toast container
        this.createToastContainer();
        
        // Add improvements CSS
        this.addImprovementsCSS();
    }

    createToastContainer() {
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
            this.toastContainer = container;
        } else {
            this.toastContainer = document.getElementById('toast-container');
        }
    }

    addImprovementsCSS() {
        if (!document.getElementById('improvements-css')) {
            const link = document.createElement('link');
            link.id = 'improvements-css';
            link.rel = 'stylesheet';
            link.href = '/css/improvements.css';
            document.head.appendChild(link);
        }
    }

    /**
     * Show toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type: success, error, warning, info
     * @param {number} duration - Duration in ms (default: 3000)
     */
    showToast(message, type = 'info', duration = 3000) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || 'ℹ'}</div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        this.toastContainer.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            toast.classList.add('closing');
            setTimeout(() => toast.remove(), 300);
        }, duration);

        return toast;
    }

    /**
     * Show loading spinner
     * @param {string} targetId - ID of element to show spinner in
     */
    showLoading(targetId) {
        const target = document.getElementById(targetId);
        if (target) {
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner';
            spinner.id = `${targetId}-spinner`;
            target.appendChild(spinner);
        }
    }

    /**
     * Hide loading spinner
     * @param {string} targetId - ID of element with spinner
     */
    hideLoading(targetId) {
        const spinner = document.getElementById(`${targetId}-spinner`);
        if (spinner) {
            spinner.remove();
        }
    }

    /**
     * Show skeleton loader
     * @param {string} targetId - ID of element to show skeleton in
     * @param {number} count - Number of skeleton items
     */
    showSkeleton(targetId, count = 3) {
        const target = document.getElementById(targetId);
        if (target) {
            target.innerHTML = '';
            for (let i = 0; i < count; i++) {
                const skeleton = document.createElement('div');
                skeleton.className = 'skeleton skeleton-card';
                target.appendChild(skeleton);
            }
        }
    }

    /**
     * Show error state
     * @param {string} targetId - ID of element
     * @param {string} message - Error message
     * @param {function} retryFn - Optional retry function
     */
    showError(targetId, message, retryFn = null) {
        const target = document.getElementById(targetId);
        if (target) {
            target.innerHTML = `
                <div class="error-container">
                    <div class="error-icon">⚠</div>
                    <div class="error-title">Oops! Something went wrong</div>
                    <div class="error-message">${message}</div>
                    ${retryFn ? '<button class="error-retry" onclick="retryAction()">Try Again</button>' : ''}
                </div>
            `;

            if (retryFn) {
                window.retryAction = retryFn;
            }
        }
    }

    /**
     * Show empty state
     * @param {string} targetId - ID of element
     * @param {string} message - Empty state message
     */
    showEmpty(targetId, message = 'No data available') {
        const target = document.getElementById(targetId);
        if (target) {
            target.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <div class="empty-title">No Data Found</div>
                    <div class="empty-message">${message}</div>
                </div>
            `;
        }
    }

    /**
     * Show progress bar
     * @param {number} progress - Progress percentage (0-100)
     * @param {string} targetId - Optional target element ID
     */
    showProgress(progress, targetId = null) {
        const percentage = Math.min(100, Math.max(0, progress));
        
        if (targetId) {
            const target = document.getElementById(targetId);
            if (target) {
                let progressBar = target.querySelector('.progress-bar');
                if (!progressBar) {
                    progressBar = document.createElement('div');
                    progressBar.className = 'progress-bar';
                    progressBar.innerHTML = '<div class="progress-bar-fill"></div>';
                    target.appendChild(progressBar);
                }
                const fill = progressBar.querySelector('.progress-bar-fill');
                fill.style.width = `${percentage}%`;
            }
        }
    }

    /**
     * Confirm dialog
     * @param {string} message - Confirmation message
     * @returns {Promise<boolean>}
     */
    async confirm(message) {
        return new Promise((resolve) => {
            const confirmed = window.confirm(message);
            resolve(confirmed);
        });
    }

    /**
     * Animate element entrance
     * @param {string} elementId - Element ID
     * @param {string} animation - Animation type
     */
    animate(elementId, animation = 'fadeIn') {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.animation = `${animation} 0.3s ease-out`;
        }
    }
}

// Create global instance
const ui = new UIEnhancements();

// Export for module usage
export default ui;

// Also make available globally
window.ui = ui;
