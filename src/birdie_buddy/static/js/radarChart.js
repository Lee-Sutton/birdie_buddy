function radarChart() {
    return {
        initChart(data) {
            const ctx = document.getElementById('radarChartCanvas').getContext('2d');
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['Driving', 'Approach', 'Putting', 'Around the Green'],
                    datasets: [{
                        data,
                        label: 'Strokes Gained',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    plugins: {
                        legend: { display: false },
                    },
                    scales: {
                        r: {
                            angleLines: {
                                display: false
                            },
                            suggestedMin: -2,
                            suggestedMax: 2,
                            pointLabels: {
                                font: {
                                }
                            }
                        }
                    }
                }
            });
        }
    }
}
