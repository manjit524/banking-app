document.addEventListener('DOMContentLoaded', function() {
    // Formatting currency
    window.formatCurrency = function(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 2
        }).format(amount);
    };

    // Greeting
    const greetingEl = document.getElementById('greeting-text');
    if (greetingEl) {
        const hour = new Date().getHours();
        let greeting = 'Good evening';
        if (hour < 12) greeting = 'Good morning';
        else if (hour < 17) greeting = 'Good afternoon';
        const name = document.querySelector('.dropdown-toggle span')?.textContent || '';
        greetingEl.textContent = `${greeting}, ${name}!`;
    }

    // Auto-dismiss alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm dialogs
    document.querySelectorAll('.needs-confirmation').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirmMessage || 'Are you sure you want to proceed?')) {
                e.preventDefault();
            }
        });
    });

    // Form Validation helper
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});
