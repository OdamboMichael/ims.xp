/**
 * Xpert Farmer IMS - Charts JavaScript
 * Handles all chart visualizations
 */

// Chart instances storage
const chartInstances = new Map();

// Chart colors using our primary palette
const chartColors = {
    primary: '#22C55E',
    primaryLight: '#4ADE80',
    primaryDark: '#16A34A',
    lightGreen: '#D5F4D5',
    success: '#10B981',
    info: '#3B82F6',
    warning: '#F59E0B',
    danger: '#EF4444',
    gray: {
        100: '#F3F4F6',
        200: '#E5E7EB',
        300: '#D1D5DB',
        400: '#9CA3AF',
        500: '#6B7280',
        600: '#4B5563',
        700: '#374151',
        800: '#1F2937',
        900: '#111827'
    }
};

// Chart configuration defaults
const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                padding: 20,
                usePointStyle: true,
                font: {
                    size: 12
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            titleFont: {
                size: 12
            },
            bodyFont: {
                size: 12
            },
            padding: 10,
            cornerRadius: 6
        }
    }
};

/**
 * Initialize all charts on the page
 */
function initializeAllCharts() {
    // Initialize dashboard charts
    initializeDashboardCharts();
    
    // Initialize production charts
    initializeProductionCharts();
    
    // Initialize reports charts
    initializeReportCharts();
    
    // Initialize user statistics charts
    initializeUserCharts();
    
    // Set up chart resize handler
    window.addEventListener('resize', debounce(handleChartResize, 250));
}

/**
 * Initialize dashboard charts
 */
function initializeDashboardCharts() {
    // Revenue Over Time Chart
    const revenueChartEl = document.getElementById('revenueChart');
    if (revenueChartEl) {
        createRevenueChart(revenueChartEl);
    }
    
    // Yield by Crop Type Chart
    const yieldPieChartEl = document.getElementById('yieldPieChart');
    if (yieldPieChartEl) {
        createYieldPieChart(yieldPieChartEl);
    }
    
    // Sales by Product Chart
    const salesByProductChartEl = document.getElementById('salesByProductChart');
    if (salesByProductChartEl) {
        createSalesByProductChart(salesByProductChartEl);
    }
    
    // Monthly Revenue Trend Chart
    const monthlyRevenueChartEl = document.getElementById('monthlyRevenueChart');
    if (monthlyRevenueChartEl) {
        createMonthlyRevenueChart(monthlyRevenueChartEl);
    }
}

/**
 * Initialize production charts
 */
function initializeProductionCharts() {
    // Yield vs Rainfall Chart
    const yieldRainfallChartEl = document.getElementById('yieldRainfallChart');
    if (yieldRainfallChartEl) {
        createYieldRainfallChart(yieldRainfallChartEl);
    }
    
    // Crop Yield Distribution Chart
    const cropYieldChartEl = document.getElementById('cropYieldChart');
    if (cropYieldChartEl) {
        createCropYieldChart(cropYieldChartEl);
    }
    
    // Gross Margin per Crop Chart
    const grossMarginChartEl = document.getElementById('grossMarginChart');
    if (grossMarginChartEl) {
        createGrossMarginChart(grossMarginChartEl);
    }
    
    // Profit Distribution Chart
    const profitDistributionChartEl = document.getElementById('profitDistributionChart');
    if (profitDistributionChartEl) {
        createProfitDistributionChart(profitDistributionChartEl);
    }
}

/**
 * Initialize report charts
 */
function initializeReportCharts() {
    // Resource Utilization Chart
    const resourceUtilizationChartEl = document.getElementById('resourceUtilizationChart');
    if (resourceUtilizationChartEl) {
        createResourceUtilizationChart(resourceUtilizationChartEl);
    }
    
    // Equipment Efficiency Chart
    const equipmentEfficiencyChartEl = document.getElementById('equipmentEfficiencyChart');
    if (equipmentEfficiencyChartEl) {
        createEquipmentEfficiencyChart(equipmentEfficiencyChartEl);
    }
    
    // Expense Breakdown Chart
    const expenseBreakdownChartEl = document.getElementById('expenseBreakdownChart');
    if (expenseBreakdownChartEl) {
        createExpenseBreakdownChart(expenseBreakdownChartEl);
    }
    
    // Income vs Expense Trend Chart
    const incomeExpenseChartEl = document.getElementById('incomeExpenseChart');
    if (incomeExpenseChartEl) {
        createIncomeExpenseChart(incomeExpenseChartEl);
    }
}

/**
 * Initialize user statistics charts
 */
function initializeUserCharts() {
    // Role Distribution Chart
    const roleDistributionChartEl = document.getElementById('roleDistributionChart');
    if (roleDistributionChartEl) {
        createRoleDistributionChart(roleDistributionChartEl);
    }
}

/**
 * Create Revenue Over Time Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createRevenueChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Revenue ($)',
                data: [12000, 19000, 15000, 25000, 22000, 30000, 28000],
                borderColor: chartColors.primary,
                backgroundColor: hexToRgba(chartColors.primary, 0.1),
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: chartColors.primary,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Revenue Over Time',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });
    
    chartInstances.set('revenueChart', chart);
}

/**
 * Create Yield by Crop Type Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createYieldPieChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Corn', 'Wheat', 'Soybeans', 'Potatoes', 'Cotton'],
            datasets: [{
                data: [35, 25, 20, 15, 5],
                backgroundColor: [
                    chartColors.primary,
                    chartColors.success,
                    chartColors.info,
                    chartColors.warning,
                    chartColors.danger
                ],
                borderColor: '#ffffff',
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            ...chartDefaults,
            cutout: '65%',
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Yield by Crop Type',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.raw}%`;
                        }
                    }
                }
            }
        }
    });
    
    chartInstances.set('yieldPieChart', chart);
}

/**
 * Create Sales by Product Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createSalesByProductChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Corn', 'Milk', 'Beef', 'Eggs', 'Wool'],
            datasets: [{
                label: 'Sales ($)',
                data: [153000, 35000, 25000, 30000, 10000],
                backgroundColor: chartColors.primary,
                borderColor: chartColors.primaryDark,
                borderWidth: 1,
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + (value / 1000).toFixed(0) + 'K';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Sales by Product',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });
    
    chartInstances.set('salesByProductChart', chart);
}

/**
 * Create Monthly Revenue Trend Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createMonthlyRevenueChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Revenue ($)',
                data: [85000, 92000, 78000, 95000, 88000, 110000, 105000, 125000, 118000, 140000, 135000, 150000],
                borderColor: chartColors.primary,
                backgroundColor: hexToRgba(chartColors.primary, 0.1),
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }, {
                label: 'Target ($)',
                data: [80000, 85000, 90000, 95000, 100000, 105000, 110000, 115000, 120000, 125000, 130000, 135000],
                borderColor: chartColors.warning,
                backgroundColor: 'transparent',
                borderWidth: 2,
                borderDash: [5, 5],
                tension: 0.4
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + (value / 1000).toFixed(0) + 'K';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Monthly Revenue Trend',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });
    
    chartInstances.set('monthlyRevenueChart', chart);
}

/**
 * Create Yield vs Rainfall Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createYieldRainfallChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Corn Yield',
                data: [
                    {x: 20, y: 150},
                    {x: 25, y: 180},
                    {x: 30, y: 200},
                    {x: 35, y: 220},
                    {x: 40, y: 210},
                    {x: 45, y: 190},
                    {x: 50, y: 170},
                    {x: 55, y: 160}
                ],
                backgroundColor: chartColors.primary,
                borderColor: chartColors.primaryDark,
                borderWidth: 1,
                pointRadius: 8
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Yield (bushels/acre)'
                    },
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Rainfall (inches)'
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Yield vs Rainfall',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });
    
    chartInstances.set('yieldRainfallChart', chart);
}

/**
 * Create Crop Yield Distribution Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createCropYieldChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: ['Corn', 'Wheat', 'Soybeans', 'Potatoes', 'Cotton'],
            datasets: [{
                data: [1600, 750, 300, 400, 225],
                backgroundColor: [
                    hexToRgba(chartColors.primary, 0.8),
                    hexToRgba(chartColors.success, 0.8),
                    hexToRgba(chartColors.info, 0.8),
                    hexToRgba(chartColors.warning, 0.8),
                    hexToRgba(chartColors.danger, 0.8)
                ],
                borderColor: [
                    chartColors.primary,
                    chartColors.success,
                    chartColors.info,
                    chartColors.warning,
                    chartColors.danger
                ],
                borderWidth: 2
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                r: {
                    ticks: {
                        display: false
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Crop Yield Distribution',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });
    
    chartInstances.set('cropYieldChart', chart);
}

/**
 * Create Gross Margin per Crop Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createGrossMarginChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Corn', 'Milk', 'Beef', 'Soybeans', 'Wheat'],
            datasets: [{
                label: 'Gross Margin (%)',
                data: [34.6, 30.0, 30.0, 12.5, 16.7],
                backgroundColor: [
                    chartColors.primary,
                    chartColors.primaryLight,
                    chartColors.success,
                    chartColors.warning,
                    chartColors.info
                ],
                borderColor: [
                    chartColors.primaryDark,
                    chartColors.primary,
                    chartColors.success,
                    chartColors.warning,
                    chartColors.info
                ],
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 50,
                    grid: {
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Gross Margin per Crop',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });
    
    chartInstances.set('grossMarginChart', chart);
}

/**
 * Create Profit Distribution Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createProfitDistributionChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Crops', 'Livestock', 'Dairy', 'Other'],
            datasets: [{
                data: [60.5, 27.7, 13.8, 4.0],
                backgroundColor: [
                    chartColors.primary,
                    chartColors.success,
                    chartColors.info,
                    chartColors.gray[400]
                ],
                borderColor: '#ffffff',
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Profit Distribution',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.raw}%`;
                        }
                    }
                }
            }
        }
    });
    
    chartInstances.set('profitDistributionChart', chart);
}

/**
 * Create Resource Utilization Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createResourceUtilizationChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Water', 'Energy', 'Labor', 'Equipment', 'Land', 'Fertilizer'],
            datasets: [{
                label: 'Current Utilization',
                data: [92, 85, 93, 88, 95, 78],
                backgroundColor: hexToRgba(chartColors.primary, 0.2),
                borderColor: chartColors.primary,
                borderWidth: 2,
                pointBackgroundColor: chartColors.primary
            }, {
                label: 'Target',
                data: [90, 85, 95, 90, 90, 85],
                backgroundColor: hexToRgba(chartColors.warning, 0.2),
                borderColor: chartColors.warning,
                borderWidth: 2,
                pointBackgroundColor: chartColors.warning,
                borderDash: [5, 5]
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        display: false
                    },
                    pointLabels: {
                        font: {
                            size: 12
                        }
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Resource Utilization',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });
    
    chartInstances.set('resourceUtilizationChart', chart);
}

/**
 * Create Equipment Efficiency Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createEquipmentEfficiencyChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: ['Tractor', 'Combine', 'Baler', 'Irrigation', 'Seeder'],
            datasets: [{
                label: 'Efficiency (%)',
                data: [95, 88, 76, 92, 84],
                backgroundColor: chartColors.primary,
                borderColor: chartColors.primaryDark,
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            ...chartDefaults,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        display: false
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                y: {
                    grid: {
                        drawBorder: false
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Equipment Efficiency',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });
    
    chartInstances.set('equipmentEfficiencyChart', chart);
}

/**
 * Create Expense Breakdown Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createExpenseBreakdownChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Labor', 'Fertilizers', 'Seeds', 'Chemicals', 'Equipment', 'Utilities'],
            datasets: [{
                data: [45, 33, 19, 26, 28, 15],
                backgroundColor: [
                    chartColors.primary,
                    chartColors.success,
                    chartColors.info,
                    chartColors.warning,
                    chartColors.danger,
                    chartColors.gray[500]
                ],
                borderColor: '#ffffff',
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            ...chartDefaults,
            cutout: '60%',
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Expense Breakdown',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: $${context.raw}K`;
                        }
                    }
                }
            }
        }
    });
    
    chartInstances.set('expenseBreakdownChart', chart);
}

/**
 * Create Income vs Expense Trend Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createIncomeExpenseChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Q1', 'Q2', 'Q3', 'Q4'],
            datasets: [{
                label: 'Income',
                data: [450, 520, 610, 730],
                borderColor: chartColors.success,
                backgroundColor: hexToRgba(chartColors.success, 0.1),
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }, {
                label: 'Expenses',
                data: [320, 380, 420, 480],
                borderColor: chartColors.danger,
                backgroundColor: hexToRgba(chartColors.danger, 0.1),
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value + 'K';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: true,
                    text: 'Income vs Expense Trend',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                }
            }
        }
    });
    
    chartInstances.set('incomeExpenseChart', chart);
}

/**
 * Create Role Distribution Chart
 * @param {HTMLElement} canvas - Canvas element
 */
function createRoleDistributionChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Admin', 'Manager', 'Analyst', 'Viewer'],
            datasets: [{
                data: [4, 8, 6, 6],
                backgroundColor: [
                    chartColors.danger,
                    chartColors.warning,
                    chartColors.success,
                    chartColors.info
                ],
                borderColor: '#ffffff',
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            ...chartDefaults,
            cutout: '70%',
            plugins: {
                ...chartDefaults.plugins,
                title: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((context.raw / total) * 100);
                            return `${context.label}: ${context.raw} users (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    chartInstances.set('roleDistributionChart', chart);
}

/**
 * Handle chart resize
 */
function handleChartResize() {
    chartInstances.forEach(chart => {
        chart.resize();
    });
}

/**
 * Update chart data
 * @param {string} chartId - Chart identifier
 * @param {Object} newData - New chart data
 */
function updateChartData(chartId, newData) {
    const chart = chartInstances.get(chartId);
    if (chart) {
        chart.data = newData;
        chart.update();
    }
}

/**
 * Export chart as image
 * @param {string} chartId - Chart identifier
 * @param {string} format - Image format (png, jpeg, webp)
 */
function exportChartAsImage(chartId, format = 'png') {
    const chart = chartInstances.get(chartId);
    if (chart) {
        const image = chart.toBase64Image();
        const link = document.createElement('a');
        link.href = image;
        link.download = `${chartId}.${format}`;
        link.click();
    }
}

/**
 * Print chart
 * @param {string} chartId - Chart identifier
 */
function printChart(chartId) {
    const chart = chartInstances.get(chartId);
    if (chart) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print Chart - ${chartId}</title>
                    <style>
                        body { margin: 0; padding: 20px; }
                        img { max-width: 100%; height: auto; }
                    </style>
                </head>
                <body>
                    <img src="${chart.toBase64Image()}">
                    <script>
                        window.onload = function() { window.print(); window.close(); }
                    </script>
                </body>
            </html>
        `);
        printWindow.document.close();
    }
}

/**
 * Convert hex color to rgba
 * @param {string} hex - Hex color code
 * @param {number} alpha - Alpha value (0-1)
 * @returns {string} rgba color string
 */
function hexToRgba(hex, alpha = 1) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Generate random chart data for demo purposes
 * @param {number} count - Number of data points
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {Array} Random data array
 */
function generateRandomData(count, min = 0, max = 100) {
    return Array.from({ length: count }, () => 
        Math.floor(Math.random() * (max - min + 1)) + min
    );
}

/**
 * Debounce function for resize events
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeAllCharts);

// Make chart functions available globally
window.XpertFarmerCharts = {
    updateChartData,
    exportChartAsImage,
    printChart,
    chartInstances
};