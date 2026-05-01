// API Base URL
const API_BASE = '/api';

// State
let currentTab = 'predictions';
let predictions = [];
let teams = [];
let performance = {};
let historical = [];
let darkMode = false;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeDarkMode();
    loadAllData();
    setInterval(loadAllData, 60000); // Refresh every minute
});

// Tab Navigation
function initializeTabs() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            switchSection(section);
        });
    });
}

function switchSection(sectionName) {
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-section') === sectionName) {
            link.classList.add('active');
        }
    });

    // Update sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
        if (section.id === `${sectionName}-section`) {
            section.classList.add('active');
        }
    });

    currentTab = sectionName;
}

// Dark Mode Functions
function initializeDarkMode() {
    // Check for saved preference
    const savedMode = localStorage.getItem('darkMode');
    if (savedMode === 'true') {
        darkMode = true;
        enableDarkMode();
    }

    // Check system preference
    if (!savedMode && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        darkMode = true;
        enableDarkMode();
    }
}

function toggleDarkMode() {
    darkMode = !darkMode;
    localStorage.setItem('darkMode', darkMode);

    if (darkMode) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
}

function enableDarkMode() {
    const darkStylesheet = document.getElementById('dark-mode-stylesheet');
    const toggleBtn = document.getElementById('dark-mode-toggle');

    if (darkStylesheet) {
        darkStylesheet.disabled = false;
    }

    if (toggleBtn) {
        toggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
    }

    // Add dark mode class to body
    document.body.classList.add('dark-mode');
}

function disableDarkMode() {
    const darkStylesheet = document.getElementById('dark-mode-stylesheet');
    const toggleBtn = document.getElementById('dark-mode-toggle');

    if (darkStylesheet) {
        darkStylesheet.disabled = true;
    }

    if (toggleBtn) {
        toggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
    }

    // Remove dark mode class from body
    document.body.classList.remove('dark-mode');
}

// Load All Data
async function loadAllData() {
    try {
        // Load current season data
        await Promise.all([
            loadPredictions(),
            loadHistorical(),
            loadHistoricalStats(),
            loadTeams(),
            loadPerformance(),
            loadInsights(),
            loadHistoricalInsights()
        ]);

        // Update performance display with enhanced features
        if (performance && Object.keys(performance).length > 0) {
            renderEnhancedPerformance();
        }

        updateLastUpdated();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Load Insights
async function loadInsights() {
    try {
        const response = await fetch(`${API_BASE}/insights`);
        const result = await response.json();

        if (result.success && result.data) {
            renderInsights(result.data);
        }
    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

// Render Insights
function renderInsights(insights) {
    const container = document.getElementById('insights-grid');

    if (!insights || insights.length === 0) {
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading insights...</p>
            </div>
        `;
        return;
    }

    container.innerHTML = insights.map(insight => `
        <div class="insight-card ${darkMode ? 'dark-mode' : ''}">
            <h4>
                <i class="fas fa-chart-pie"></i>
                ${insight.title}
            </h4>
            <ul>
                ${insight.content.map(item => `
                    <li>${item}</li>
                `).join('')}
            </ul>
        </div>
    `).join('');
}

// Load Historical Insights
async function loadHistoricalInsights() {
    try {
        const response = await fetch(`${API_BASE}/historical-insights`);
        const result = await response.json();

        if (result.success && result.data) {
            window.historicalInsights = result.data;
            console.log('Historical insights loaded:', result.data);
        }
    } catch (error) {
        console.error('Error loading historical insights:', error);
    }
}

// Load Predictions
async function loadPredictions() {
    try {
        const response = await fetch(`${API_BASE}/predictions`);
        const result = await response.json();

        if (result.success) {
            predictions = result.data;
            renderPredictions();
            updateHeaderStats(result.count);
        }
    } catch (error) {
        console.error('Error loading predictions:', error);
        showErrorMessage('predictions-list', 'Failed to load predictions');
    }
}

// Load Teams
async function loadTeams() {
    try {
        const response = await fetch(`${API_BASE}/teams`);
        const result = await response.json();

        if (result.success) {
            teams = result.data;
            renderTeams();
        }
    } catch (error) {
        console.error('Error loading teams:', error);
        showErrorMessage('teams-list', 'Failed to load teams');
    }
}

// Load Performance
async function loadPerformance() {
    try {
        const response = await fetch(`${API_BASE}/performance`);
        const result = await response.json();

        if (result.success) {
            performance = result.data;
            renderPerformance();
        }
    } catch (error) {
        console.error('Error loading performance:', error);
    }
}

// Load Historical Predictions
async function loadHistorical() {
    try {
        const response = await fetch(`${API_BASE}/historical`);
        const result = await response.json();

        if (result.success) {
            historical = result.data;
            renderHistorical();
        }
    } catch (error) {
        console.error('Error loading historical:', error);
        showErrorMessage('historical-list', 'Failed to load historical predictions');
    }
}

// Load Historical Stats
async function loadHistoricalStats() {
    try {
        const response = await fetch(`${API_BASE}/historical/stats`);
        const result = await response.json();

        if (result.success) {
            renderHistoricalStats(result.data);
        }
    } catch (error) {
        console.error('Error loading historical stats:', error);
    }
}

// Render Predictions
function renderPredictions() {
    const container = document.getElementById('predictions-list');

    if (predictions.length === 0) {
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-calendar-times"></i>
                <p>No upcoming matches found</p>
            </div>
        `;
        return;
    }

    container.innerHTML = predictions.map(pred => `
        <div class="prediction-card ${darkMode ? 'dark-mode' : ''}" onclick="showMatchDetail(${pred.id})">
            <div class="prediction-header">
                <span class="match-date">
                    <i class="fas fa-calendar"></i> ${pred.date}
                </span>
                <span class="league-badge">${pred.league}</span>
            </div>

            <div class="match-teams">
                <div class="team">
                    <div class="team-name">${pred.home_team}</div>
                    <div class="team-elo">ELO: ${pred.home_elo}</div>
                </div>
                <div class="vs">VS</div>
                <div class="team">
                    <div class="team-name">${pred.away_team}</div>
                    <div class="team-elo">ELO: ${pred.away_elo}</div>
                </div>
            </div>

            <div class="prediction-result">
                <div class="prediction-label">Prediction</div>
                <div class="prediction-value">${getPredictionIcon(pred.prediction)} ${pred.prediction}</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${pred.confidence}%; background: ${getConfidenceColor(pred.confidence)}"></div>
                </div>
                <div class="confidence-text">Confidence: ${pred.confidence}%</div>
            </div>

            <div class="probabilities">
                <div class="prob-item">
                    <div class="prob-label">Home Win</div>
                    <div class="prob-value prob-home">${pred.home_win_prob}%</div>
                </div>
                <div class="prob-item">
                    <div class="prob-label">Draw</div>
                    <div class="prob-value prob-draw">${pred.draw_prob}%</div>
                </div>
                <div class="prob-item">
                    <div class="prob-label">Away Win</div>
                    <div class="prob-value prob-away">${pred.away_win_prob}%</div>
                </div>
            </div>

            ${pred.actual_result ? `
                <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-secondary); border-radius: var(--radius-lg); border-left: 4px solid ${pred.is_correct ? 'var(--success-color)' : 'var(--danger-color)'};">
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Actual Result</div>
                    <div style="font-size: 1.125rem; font-weight: 600; color: ${pred.is_correct ? 'var(--success-color)' : 'var(--danger-color)'};">
                        ${pred.is_correct ? '✓' : '✗'} ${pred.actual_result}
                    </div>
                </div>
            ` : ''}
        </div>
    `).join('');
}

// Render Teams
function renderTeams() {
    const container = document.getElementById('teams-list');

    if (teams.length === 0) {
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-users"></i>
                <p>No teams data available</p>
            </div>
        `;
        return;
    }

    container.innerHTML = teams.map(team => `
        <div class="team-card ${darkMode ? 'dark-mode' : ''}">
            <div class="team-rank" style="background: ${getRankGradient(team.rank)}">#${team.rank}</div>
            <div class="team-info">
                <div class="team-name-display">${team.team}</div>
                <div class="team-stats">${team.wins}W ${team.draws}D ${team.losses}L | ${team.points} pts</div>
                ${team.form ? `<div class="team-form">Form: ${team.form}</div>` : ''}
            </div>
            <div style="text-align: right;">
                <div class="team-elo-display">${team.elo}</div>
                <div class="team-gd">${team.goal_difference > 0 ? '+' : ''}${team.goal_difference} GD</div>
            </div>
        </div>
    `).join('');
}

function getRankGradient(rank) {
    if (rank <= 4) return 'linear-gradient(135deg, #10b981, #059669)';
    if (rank <= 6) return 'linear-gradient(135deg, #6366f1, #4f46e5)';
    if (rank >= 18) return 'linear-gradient(135deg, #ef4444, #dc2626)';
    return 'linear-gradient(135deg, #6366f1, #8b5cf6)';
}

// Render Performance
function renderPerformance() {
    if (performance.accuracy) {
        document.getElementById('perf-accuracy').textContent = `${performance.accuracy}%`;
    }
    if (performance.log_loss) {
        document.getElementById('perf-logloss').textContent = performance.log_loss.toFixed(3);
    }
    if (performance.total_predictions) {
        document.getElementById('perf-total').textContent = performance.total_predictions.toLocaleString();
    }
    if (performance.last_updated) {
        document.getElementById('perf-updated').textContent = performance.last_updated;
    }

    // Update performance cards with enhanced data
    const performanceGrid = document.querySelector('.performance-grid');
    if (performanceGrid && performance.total_matches) {
        const enhancedCards = [
            createEnhancedPerformanceCard(
                'Accuracy',
                `${performance.accuracy}%`,
                'Overall prediction accuracy',
                'fa-bullseye',
                '#10b981'
            ),
            createEnhancedPerformanceCard(
                'Total Matches',
                performance.total_matches,
                'Matches analyzed this season',
                'fa-database',
                '#6366f1'
            ),
            createEnhancedPerformanceCard(
                'High Confidence',
                `${performance.high_confidence_accuracy}%`,
                'Accuracy on predictions >70% confidence',
                'fa-chart-line',
                '#f59e0b'
            ),
            createEnhancedPerformanceCard(
                'Best Team',
                performance.best_predicting_team || 'N/A',
                `Highest prediction accuracy: ${performance.best_team_accuracy || 0}%`,
                'fa-trophy',
                '#ec4899'
            )
        ];

        performanceGrid.innerHTML = enhancedCards.join('');
    }
}

// Update Header Stats
function updateHeaderStats(count) {
    if (performance.accuracy) {
        document.getElementById('nav-accuracy').textContent = `${performance.accuracy}%`;
        document.getElementById('hero-accuracy').textContent = `${performance.accuracy}%`;
    }
    if (performance.total_matches) {
        document.getElementById('hero-matches').textContent = performance.total_matches;
    } else {
        document.getElementById('hero-matches').textContent = count;
    }
    if (teams.length > 0) {
        document.getElementById('hero-teams').textContent = teams.length;
    }
}

// Render Historical Predictions
function renderHistorical() {
    const container = document.getElementById('historical-list');

    if (historical.length === 0) {
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-history"></i>
                <p>No historical predictions found</p>
            </div>
        `;
        return;
    }

    // Sort by date (most recent first)
    const sortedHistorical = [...historical].sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return dateB - dateA;
    });

    // Apply filters if set
    let filteredHistorical = sortedHistorical;
    const dateFrom = document.getElementById('date-from').value;
    const dateTo = document.getElementById('date-to').value;

    if (dateFrom) {
        const fromDate = new Date(dateFrom);
        filteredHistorical = filteredHistorical.filter(pred => new Date(pred.date) >= fromDate);
    }

    if (dateTo) {
        const toDate = new Date(dateTo);
        filteredHistorical = filteredHistorical.filter(pred => new Date(pred.date) <= toDate);
    }

    // Update filter info
    const filterInfo = document.getElementById('filter-info');
    if (dateFrom || dateTo) {
        filterInfo.innerHTML = `<i class="fas fa-filter"></i> Showing ${filteredHistorical.length} of ${historical.length} matches`;
    } else {
        filterInfo.innerHTML = `<i class="fas fa-list"></i> Showing all ${historical.length} matches`;
    }

    // Group by date if selected
    const groupBy = document.getElementById('date-group').value;
    let groupedData = filteredHistorical;

    if (groupBy !== 'none') {
        groupedData = groupByDate(filteredHistorical, groupBy);
    }

    if (Array.isArray(groupedData)) {
        // No grouping, render directly
        container.innerHTML = groupedData.map(pred => renderHistoricalCard(pred)).join('');
    } else {
        // Grouped data, render with headers
        let html = '';
        for (const [groupKey, groupData] of Object.entries(groupedData)) {
            const correctCount = groupData.filter(p => p.is_correct).length;
            const totalCount = groupData.length;
            const accuracy = ((correctCount / totalCount) * 100).toFixed(1);

            html += `
                <div class="date-group-header">
                    <h3><i class="fas fa-calendar-alt"></i> ${groupKey}</h3>
                    <div class="group-stats">
                        <span><i class="fas fa-futbol"></i> ${totalCount} matches</span>
                        <span><i class="fas fa-check-circle"></i> ${correctCount} correct</span>
                        <span><i class="fas fa-percentage"></i> ${accuracy}% accuracy</span>
                    </div>
                </div>
            `;
            html += groupData.map(pred => renderHistoricalCard(pred)).join('');
        }
        container.innerHTML = html;
    }
}

function renderHistoricalCard(pred) {
    return `
        <div class="prediction-card ${pred.is_correct ? 'correct' : 'incorrect'} ${darkMode ? 'dark-mode' : ''}">
            <div class="prediction-header">
                <span class="match-date">
                    <i class="fas fa-calendar"></i> ${pred.date}
                </span>
                <span class="result-badge ${pred.is_correct ? 'correct' : 'incorrect'}">
                    <i class="fas ${pred.is_correct ? 'fa-check' : 'fa-times'}"></i>
                    ${pred.is_correct ? 'Correct' : 'Incorrect'}
                </span>
            </div>

            <div class="match-teams">
                <div class="team">
                    <div class="team-name">${pred.home_team}</div>
                    <div class="team-elo">ELO: ${pred.home_elo}</div>
                </div>
                <div class="vs">VS</div>
                <div class="team">
                    <div class="team-name">${pred.away_team}</div>
                    <div class="team-elo">ELO: ${pred.away_elo}</div>
                </div>
            </div>

            <div class="prediction-result">
                <div class="prediction-label">Prediction vs Actual</div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                    <div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">Predicted</div>
                        <div style="font-size: 1.125rem; font-weight: 600; color: var(--primary-color);">
                            ${getPredictionIcon(pred.prediction)} ${pred.prediction}
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">Actual</div>
                        <div style="font-size: 1.125rem; font-weight: 600; color: ${pred.is_correct ? 'var(--success-color)' : 'var(--danger-color)'};">
                            ${getPredictionIcon(pred.actual)} ${pred.actual}
                        </div>
                    </div>
                </div>
            </div>

            <div class="probabilities">
                <div class="prob-item">
                    <div class="prob-label">Home Win</div>
                    <div class="prob-value prob-home">${pred.home_prob}%</div>
                </div>
                <div class="prob-item">
                    <div class="prob-label">Draw</div>
                    <div class="prob-value prob-draw">${pred.draw_prob}%</div>
                </div>
                <div class="prob-item">
                    <div class="prob-label">Away Win</div>
                    <div class="prob-value prob-away">${pred.away_prob}%</div>
                </div>
            </div>

            <div style="margin-top: 1rem; font-size: 0.875rem; color: var(--text-secondary);">
                Confidence: ${pred.confidence}% | Importance: ${pred.importance}
            </div>
        </div>
    `;
}

function groupByDate(data, groupBy) {
    const grouped = {};

    data.forEach(item => {
        const date = new Date(item.date);
        let key;

        if (groupBy === 'day') {
            key = date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        } else if (groupBy === 'week') {
            const weekStart = new Date(date);
            weekStart.setDate(date.getDate() - date.getDay());
            const weekEnd = new Date(weekStart);
            weekEnd.setDate(weekStart.getDate() + 6);
            key = `Week of ${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
        } else if (groupBy === 'month') {
            key = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
        }

        if (!grouped[key]) {
            grouped[key] = [];
        }
        grouped[key].push(item);
    });

    return grouped;
}

function applyDateFilter() {
    renderHistorical();
}

function clearDateFilter() {
    document.getElementById('date-from').value = '';
    document.getElementById('date-to').value = '';
    document.getElementById('date-group').value = 'none';
    renderHistorical();
}

// Render Historical Stats
function renderHistoricalStats(stats) {
    if (stats.accuracy !== undefined) {
        document.getElementById('hist-accuracy').textContent = `${stats.accuracy}%`;
    }
    if (stats.total !== undefined) {
        document.getElementById('hist-total').textContent = stats.total;
    }
    if (stats.correct !== undefined) {
        document.getElementById('hist-correct').textContent = stats.correct;
    }
}

// Update Last Updated
function updateLastUpdated() {
    const now = new Date();
    const formatted = now.toLocaleString();
    document.getElementById('last-updated').textContent = formatted;
}

// Show Match Detail
async function showMatchDetail(matchId) {
    try {
        const response = await fetch(`${API_BASE}/match/${matchId}`);
        const result = await response.json();

        if (result.success) {
            const match = result.data;
            const modal = document.getElementById('match-modal');
            const modalBody = document.getElementById('modal-body');

            document.getElementById('modal-title').textContent =
                `${match.home_team} vs ${match.away_team}`;

            modalBody.innerHTML = `
                <div style="margin-bottom: 20px;">
                    <strong>Date:</strong> ${match.date}<br>
                    <strong>League:</strong> ${match.league}
                </div>

                <div style="margin-bottom: 20px;">
                    <h4 style="margin-bottom: 10px;">ELO Ratings</h4>
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>${match.home_team}:</strong> ${match.home_elo}
                        </div>
                        <div>
                            <strong>${match.away_team}:</strong> ${match.away_elo}
                        </div>
                    </div>
                    <div style="margin-top: 10px; color: #6c757d;">
                        Difference: ${match.elo_diff > 0 ? '+' : ''}${match.elo_diff}
                    </div>
                </div>

                <div style="margin-bottom: 20px;">
                    <h4 style="margin-bottom: 10px;">Prediction</h4>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #667eea; margin-bottom: 10px;">
                        ${match.prediction}
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>Confidence:</strong> ${match.confidence}%
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${match.confidence}%"></div>
                    </div>
                </div>

                <div>
                    <h4 style="margin-bottom: 10px;">Probabilities</h4>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                        <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                            <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 5px;">Home Win</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #28a745;">${match.home_prob}%</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                            <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 5px;">Draw</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #ffc107;">${match.draw_prob}%</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                            <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 5px;">Away Win</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #dc3545;">${match.away_prob}%</div>
                        </div>
                    </div>
                </div>
            `;

            modal.classList.add('active');
        }
    } catch (error) {
        console.error('Error loading match detail:', error);
        alert('Failed to load match details');
    }
}

// Close Modal
function closeModal() {
    const modal = document.getElementById('match-modal');
    modal.classList.remove('active');
}

// Close modal on outside click
document.getElementById('match-modal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// Refresh Predictions
async function refreshPredictions() {
    const btn = document.querySelector('.btn-refresh');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
    btn.disabled = true;

    try {
        await loadAllData();
        btn.innerHTML = '<i class="fas fa-check"></i> Refreshed!';
        setTimeout(() => {
            btn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
            btn.disabled = false;
        }, 2000);
    } catch (error) {
        console.error('Error refreshing:', error);
        btn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
        setTimeout(() => {
            btn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
            btn.disabled = false;
        }, 2000);
    }
}

// Update Historical Predictions
async function updateHistorical() {
    const btn = document.querySelector('#historical-tab .btn-refresh');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/historical/update`);
        const result = await response.json();

        if (result.success) {
            await loadHistorical();
            await loadHistoricalStats();
            btn.innerHTML = '<i class="fas fa-check"></i> Updated!';
            setTimeout(() => {
                btn.innerHTML = '<i class="fas fa-sync-alt"></i> Update';
                btn.disabled = false;
            }, 2000);
        } else {
            btn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
            setTimeout(() => {
                btn.innerHTML = '<i class="fas fa-sync-alt"></i> Update';
                btn.disabled = false;
            }, 2000);
        }
    } catch (error) {
        console.error('Error updating historical:', error);
        btn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
        setTimeout(() => {
            btn.innerHTML = '<i class="fas fa-sync-alt"></i> Update';
            btn.disabled = false;
        }, 2000);
    }
}

// Show Error Message
function showErrorMessage(containerId, message) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="loading">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
}

// Enhanced Data Visualization Functions
function createEnhancedPredictionCard(pred) {
    const confidenceColor = getConfidenceColor(pred.confidence);
    const predictionIcon = getPredictionIcon(pred.prediction);

    return `
        <div class="prediction-card ${darkMode ? 'dark-mode' : ''}" onclick="showMatchDetail(${pred.id})">
            <div class="prediction-header">
                <span class="match-date">
                    <i class="fas fa-calendar"></i> ${pred.date}
                </span>
                <span class="league-badge">${pred.league}</span>
            </div>

            <div class="match-teams">
                <div class="team">
                    <div class="team-name">${pred.home_team}</div>
                    <div class="team-elo">ELO: ${pred.home_elo}</div>
                </div>
                <div class="vs">VS</div>
                <div class="team">
                    <div class="team-name">${pred.away_team}</div>
                    <div class="team-elo">ELO: ${pred.away_elo}</div>
                </div>
            </div>

            <div class="prediction-result">
                <div class="prediction-label">Prediction</div>
                <div class="prediction-value" style="color: ${confidenceColor}">
                    ${predictionIcon} ${pred.prediction}
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${pred.confidence}%; background: ${confidenceColor}"></div>
                </div>
                <div style="margin-top: 10px; font-size: 0.9rem; color: ${darkMode ? '#a0a0a0' : '#6c757d'};">
                    Confidence: ${pred.confidence}%
                </div>
            </div>

            <div class="probabilities">
                <div class="prob-item">
                    <div class="prob-label">Home Win</div>
                    <div class="prob-value prob-home">${pred.home_prob}%</div>
                </div>
                <div class="prob-item">
                    <div class="prob-label">Draw</div>
                    <div class="prob-value prob-draw">${pred.draw_prob}%</div>
                </div>
                <div class="prob-item">
                    <div class="prob-label">Away Win</div>
                    <div class="prob-value prob-away">${pred.away_prob}%</div>
                </div>
            </div>
        </div>
    `;
}

function getConfidenceColor(confidence) {
    if (confidence >= 70) return '#4ade80'; // Green for high confidence
    if (confidence >= 50) return '#667eea'; // Blue for medium confidence
    return '#fbbf24'; // Yellow for low confidence
}

function getPredictionIcon(prediction) {
    switch(prediction) {
        case 'Home Win': return '<i class="fas fa-home"></i>';
        case 'Away Win': return '<i class="fas fa-plane"></i>';
        case 'Draw': return '<i class="fas fa-handshake"></i>';
        default: return '';
    }
}

function createEnhancedTeamCard(team) {
    const rankColor = getRankColor(team.rank);

    return `
        <div class="team-card ${darkMode ? 'dark-mode' : ''}">
            <div class="team-rank" style="color: ${rankColor}">#${team.rank}</div>
            <div class="team-info">
                <div class="team-name-display">${team.team}</div>
            </div>
            <div class="team-elo-display" style="color: ${rankColor}">${team.elo}</div>
        </div>
    `;
}

function getRankColor(rank) {
    if (rank <= 4) return '#4ade80'; // Champions League spots
    if (rank <= 6) return '#667eea'; // Europa League spots
    if (rank >= 18) return '#f87171'; // Relegation zone
    return '#e0e0e0'; // Mid-table
}

function createEnhancedPerformanceCard(title, value, label, icon, color) {
    return `
        <div class="performance-card ${darkMode ? 'dark-mode' : ''}" style="border-left: 4px solid ${color}">
            <div class="card-icon" style="color: ${color}">
                <i class="fas ${icon}"></i>
            </div>
            <div class="card-content">
                <h3>${title}</h3>
                <p class="card-value" style="color: ${color}">${value}</p>
                <p class="card-label">${label}</p>
            </div>
        </div>
    `;
}

function createEnhancedHistoricalCard(pred) {
    const resultClass = pred.is_correct ? 'correct' : 'incorrect';
    const resultIcon = pred.is_correct ? 'fa-check-circle' : 'fa-times-circle';
    const resultColor = pred.is_correct ? '#4ade80' : '#f87171';

    return `
        <div class="prediction-card ${resultClass} ${darkMode ? 'dark-mode' : ''}">
            <div class="prediction-header">
                <span class="match-date">
                    <i class="fas fa-calendar"></i> ${pred.date}
                </span>
                <span class="result-badge ${resultClass}" style="background: ${resultColor}">
                    <i class="fas ${resultIcon}"></i>
                    ${pred.is_correct ? 'Correct' : 'Incorrect'}
                </span>
            </div>

            <div class="match-teams">
                <div class="team">
                    <div class="team-name">${pred.home_team}</div>
                    <div class="team-score">${pred.home_goals}</div>
                </div>
                <div class="vs">${pred.home_goals} - ${pred.away_goals}</div>
                <div class="team">
                    <div class="team-name">${pred.away_team}</div>
                    <div class="team-score">${pred.away_goals}</div>
                </div>
            </div>

            <div class="prediction-result">
                <div class="prediction-label">Prediction vs Actual</div>
                <div class="prediction-comparison">
                    <div class="comparison-item">
                        <span class="comparison-label">Predicted:</span>
                        <span class="comparison-value prediction">${pred.prediction}</span>
                    </div>
                    <div class="comparison-item">
                        <span class="comparison-label">Actual:</span>
                        <span class="comparison-value actual">${pred.actual}</span>
                    </div>
                </div>
            </div>

            <div class="probabilities">
                <div class="prob-item">
                    <div class="prob-label">Home Win</div>
                    <div class="prob-value prob-home">${pred.home_prob}%</div>
                </div>
                <div class="prob-item">
                    <div class="prob-label">Draw</div>
                    <div class="prob-value prob-draw">${pred.draw_prob}%</div>
                </div>
                <div class="prob-item">
                    <div class="prob-label">Away Win</div>
                    <div class="prob-value prob-away">${pred.away_prob}%</div>
                </div>
            </div>
        </div>
    `;
}

// Load Enhanced Premier League Data
async function loadEnhancedPremierLeagueData() {
    try {
        const response = await fetch('/data/premier_league_matches_2526_improved.json');
        const data = await response.json();

        if (data && data.length > 0) {
            // Update predictions with enhanced data
            predictions = data.slice(0, 20); // Take first 20 matches
            renderEnhancedPredictions();
            return true;
        }
        return false;
    } catch (error) {
        console.error('Error loading enhanced Premier League data:', error);
        return false;
    }
}

function renderEnhancedPredictions() {
    const container = document.getElementById('predictions-list');

    if (predictions.length === 0) {
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-calendar-times"></i>
                <p>No upcoming matches found</p>
            </div>
        `;
        return;
    }

    container.innerHTML = predictions.map(pred => createEnhancedPredictionCard(pred)).join('');
}

// Load Enhanced Team Statistics
async function loadEnhancedTeamStats() {
    try {
        const response = await fetch('/data/team_statistics_2526.json');
        const data = await response.json();

        if (data && data.length > 0) {
            teams = data.slice(0, 10); // Take top 10 teams
            renderEnhancedTeams();
            return true;
        }
        return false;
    } catch (error) {
        console.error('Error loading enhanced team statistics:', error);
        return false;
    }
}

function renderEnhancedTeams() {
    const container = document.getElementById('teams-list');

    if (teams.length === 0) {
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-users"></i>
                <p>No teams data available</p>
            </div>
        `;
        return;
    }

    container.innerHTML = teams.map(team => createEnhancedTeamCard(team)).join('');
}

// Enhanced Performance Display
function renderEnhancedPerformance() {
    const performanceGrid = document.querySelector('.performance-grid');
    if (!performanceGrid) return;

    let html = '';

    // Basic performance metrics
    const enhancedCards = [
        createEnhancedPerformanceCard(
            'Accuracy',
            performance.accuracy ? `${performance.accuracy}%` : '--%',
            'Overall prediction accuracy',
            'fa-bullseye',
            '#4ade80'
        ),
        createEnhancedPerformanceCard(
            'Total Predictions',
            performance.total_predictions ? performance.total_predictions.toLocaleString() : '--',
            'Matches analyzed',
            'fa-database',
            '#fbbf24'
        ),
        createEnhancedPerformanceCard(
            'High Confidence Accuracy',
            performance.high_confidence_accuracy ? `${performance.high_confidence_accuracy}%` : '--%',
            'Predictions with 70%+ confidence',
            'fa-star',
            '#667eea'
        ),
        createEnhancedPerformanceCard(
            'Last Updated',
            performance.last_updated || '--',
            'Model training date',
            'fa-clock',
            '#f87171'
        )
    ];

    html += enhancedCards.join('');

    // Add historical insights section if available
    if (window.historicalInsights) {
        const insights = window.historicalInsights;
        const overview = insights.overview || {};
        const teamPerf = insights.team_performance || {};
        const matchStats = insights.match_statistics || {};

        html += `
            <div class="historical-insights-section">
                <h3 class="insights-title">
                    <i class="fas fa-chart-bar"></i> Historical Data Analysis
                </h3>

                <div class="insights-overview">
                    <div class="insight-stat">
                        <i class="fas fa-futbol"></i>
                        <div>
                            <div class="insight-value">${overview.total_matches || 0}</div>
                            <div class="insight-label">Total Matches</div>
                        </div>
                    </div>
                    <div class="insight-stat">
                        <i class="fas fa-bullseye"></i>
                        <div>
                            <div class="insight-value">${overview.avg_goals_per_match || 0}</div>
                            <div class="insight-label">Avg Goals/Match</div>
                        </div>
                    </div>
                    <div class="insight-stat">
                        <i class="fas fa-home"></i>
                        <div>
                            <div class="insight-value">${overview.home_win_rate || 0}%</div>
                            <div class="insight-label">Home Win Rate</div>
                        </div>
                    </div>
                    <div class="insight-stat">
                        <i class="fas fa-plane"></i>
                        <div>
                            <div class="insight-value">${overview.away_win_rate || 0}%</div>
                            <div class="insight-label">Away Win Rate</div>
                        </div>
                    </div>
                </div>

                <div class="insights-details">
                    <div class="insight-block">
                        <h4><i class="fas fa-trophy"></i> Top Teams</h4>
                        <ul>
                            ${(teamPerf.top_teams || []).slice(0, 5).map((team, i) => `
                                <li>
                                    <span class="rank">${i + 1}.</span>
                                    <span class="team-name">${team.team}</span>
                                    <span class="team-points">${team.points} pts</span>
                                    <span class="team-record">(${team.wins}W-${team.draws}D-${team.losses}L)</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>

                    <div class="insight-block">
                        <h4><i class="fas fa-chart-line"></i> Key Findings</h4>
                        <ul>
                            ${(insights.key_findings || []).map(finding => `
                                <li><i class="fas fa-lightbulb"></i> ${finding}</li>
                            `).join('')}
                        </ul>
                    </div>

                    <div class="insight-block">
                        <h4><i class="fas fa-chart-pie"></i> Match Statistics</h4>
                        <ul>
                            <li><i class="fas fa-home"></i> Avg Home Goals: ${matchStats.avg_home_goals || 0}</li>
                            <li><i class="fas fa-plane"></i> Avg Away Goals: ${matchStats.avg_away_goals || 0}</li>
                            <li><i class="fas fa-fire"></i> High Scoring Matches: ${matchStats.high_scoring_matches || 0}</li>
                            <li><i class="fas fa-shield-alt"></i> Low Scoring Matches: ${matchStats.low_scoring_matches || 0}</li>
                            <li><i class="fas fa-percentage"></i> Over 2.5 Goals: ${matchStats.over_2_5_percentage || 0}%</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    performanceGrid.innerHTML = html;
}

// Initialize Enhanced Features
function initializeEnhancedFeatures() {
    // Try to load enhanced data first
    loadEnhancedPremierLeagueData().then(success => {
        if (!success) {
            // Fall back to regular predictions
            loadPredictions();
        }
    });

    loadEnhancedTeamStats().then(success => {
        if (!success) {
            // Fall back to regular teams
            loadTeams();
        }
    });

    // Enhance performance display
    if (performance && Object.keys(performance).length > 0) {
        renderEnhancedPerformance();
    }
}
