class NexusBankSSE {
    constructor() {
        this.pollInterval = null;
        this.lastNotificationIds = new Set();
    }

    connect(userId) {
        if (!userId) return;
        console.log("Initializing realtime polling updates...");
        
        // Run initial poll immediately
        this.doPoll();
        
        // Poll every 3 seconds to stay real-time without locking the WSGI server
        this.pollInterval = setInterval(() => {
            this.doPoll();
        }, 3000);
    }

    doPoll() {
        fetch('/api/notifications/poll')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    this.handlePollData(data);
                }
            })
            .catch(err => console.log("Realtime update polling error:", err));
    }

    handlePollData(data) {
        // Update unread notification count badge in sidebar/topbar
        const badges = document.querySelectorAll('.unread-badge');
        badges.forEach(badge => {
            if (data.unread_count > 0) {
                badge.textContent = data.unread_count;
                badge.classList.remove('d-none');
            } else {
                badge.classList.add('d-none');
            }
        });

        // Update total balance display in DOM if on dashboard
        const balEl = document.getElementById('total-balance-display');
        if (balEl && data.total_balance !== undefined) {
            const formatted = window.formatCurrency ? window.formatCurrency(data.total_balance) : '₹' + data.total_balance.toFixed(2);
            if (balEl.textContent !== formatted) {
                balEl.textContent = formatted;
                // Add quick green flash animation effect
                balEl.classList.add('text-success');
                setTimeout(() => balEl.classList.remove('text-success'), 1000);
            }
        }

        // Display new notifications as Bootstrap toasts
        if (data.new_notifications && data.new_notifications.length > 0) {
            data.new_notifications.forEach(n => {
                if (!this.lastNotificationIds.has(n.id)) {
                    this.lastNotificationIds.add(n.id);
                    this.showToast(n.title, n.message);
                }
            });
        }
    }

    showToast(title, message) {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }

        const toastId = 'toast-' + Date.now() + Math.random().toString(36).substr(2, 5);
        const toastHTML = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-success text-white">
                    <i class="fa-solid fa-leaf me-2"></i>
                    <strong class="me-auto">${title}</strong>
                    <small>Just now</small>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        document.getElementById('toast-container').insertAdjacentHTML('beforeend', toastHTML);
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toast.show();
        
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
}

const nexusSSE = new NexusBankSSE();
document.addEventListener('DOMContentLoaded', () => {
    if (typeof NEXUS_USER_ID !== 'undefined' && NEXUS_USER_ID !== '') {
        nexusSSE.connect(NEXUS_USER_ID);
    }
});
