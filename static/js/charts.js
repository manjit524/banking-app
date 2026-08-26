document.addEventListener('DOMContentLoaded', function() {
    const lineCtx = document.getElementById('lineChart');
    if(lineCtx) {
        new Chart(lineCtx, {
            type: 'line',
            data: {
                labels: ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                datasets: [
                    {
                        label: 'Income',
                        data: [110000, 115000, 120000, 115000, 125000, 125000],
                        borderColor: '#1d785a',
                        backgroundColor: 'rgba(29, 120, 90, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Expenses',
                        data: [40000, 42000, 45000, 38000, 48000, 45200],
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: { responsive: true }
        });
    }

    const donutCtx = document.getElementById('donutChart');
    if(donutCtx) {
        new Chart(donutCtx, {
            type: 'doughnut',
            data: {
                labels: ['Housing', 'Food', 'Transport', 'Utilities', 'Entertainment'],
                datasets: [{
                    data: [35, 25, 15, 15, 10],
                    backgroundColor: ['#0d3b2e', '#1d785a', '#37d699', '#f39c12', '#e74c3c']
                }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });
    }
});
