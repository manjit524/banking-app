document.addEventListener('DOMContentLoaded', function() {
    // Generate UUID for idempotency
    const idempotencyField = document.getElementById('idempotency_key');
    if (idempotencyField && !idempotencyField.value) {
        idempotencyField.value = crypto.randomUUID ? crypto.randomUUID() : 'id-' + Date.now();
    }

    // Account Number Verification
    const accInput = document.getElementById('beneficiary_account');
    const nameDisplay = document.getElementById('beneficiary_name_display');
    const amountInput = document.getElementById('amount');
    const previewAmount = document.getElementById('preview_amount');
    const previewTotal = document.getElementById('preview_total');

    if (accInput && nameDisplay) {
        accInput.addEventListener('blur', function() {
            const accNum = this.value.trim();
            if (accNum.length >= 8) {
                // Fetch the beneficiary account holder name dynamically
                fetch(`/transfers/verify-account?account_number=${accNum}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            nameDisplay.innerHTML = `<span class="text-success"><i class="fa-solid fa-check-circle"></i> Verified: ${data.holder_name}</span>`;
                        } else {
                            nameDisplay.innerHTML = `<span class="text-danger"><i class="fa-solid fa-circle-xmark"></i> ${data.message || 'Account not found'}</span>`;
                        }
                    })
                    .catch(err => {
                        nameDisplay.innerHTML = `<span class="text-danger">Verification failed</span>`;
                    });
            } else {
                nameDisplay.innerHTML = `<span class="text-muted">Enter valid account number</span>`;
            }
        });
    }

    if (amountInput && previewAmount) {
        amountInput.addEventListener('input', function() {
            const val = parseFloat(this.value) || 0;
            previewAmount.textContent = window.formatCurrency ? window.formatCurrency(val) : '₹' + val.toFixed(2);
            previewTotal.textContent = window.formatCurrency ? window.formatCurrency(val) : '₹' + val.toFixed(2);
        });
    }

    // Handle Form Submission and set active tab's recipient
    const transferForm = document.getElementById('transferForm');
    const toAccountHidden = document.getElementById('to_account_number_hidden');
    const savedBenSelect = document.getElementById('saved_beneficiary_select');
    const savedTab = document.getElementById('saved-tab');

    if (transferForm && toAccountHidden) {
        transferForm.addEventListener('submit', function(e) {
            if (savedTab && savedTab.classList.contains('active')) {
                toAccountHidden.value = savedBenSelect.value;
            } else {
                toAccountHidden.value = accInput.value.trim();
            }
        });
    }
});
