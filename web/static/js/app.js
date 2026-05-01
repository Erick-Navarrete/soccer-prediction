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
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.getAttribute('data-tab') === tabName) {
            tab.classList.add('active');
        }
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        if (content.id === `${tabName}-tab`) {
            content.classList.add('active');
        }
    });

    currentTab = tabName;
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
            loadInsights()
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
    // Create insights section if it doesn't exist
    let insightsContainer = document.getElementById('insights-container');
    if (!insightsContainer) {
        // Add insights section after the tabs
        const tabsContainer = document.querySelector('.tabs');
        if (tabsContainer) {
            insightsContainer = document.createElement('div');
            insightsContainer.id = 'insights-container';
            insightsContainer.className = 'insights-section';
            insightsContainer.style.cssText = `
                background: ${darkMode ? 'rgba(30, 30, 50, 0.8)' : '#f8f9fa'};
                padding: 20px;
                margin: 20px 30px;
                border-radius: 10px;
                border: 1px solid ${darkMode ? 'rgba(102, 126, 234, 0.2)' : '#e9ecef'};
            `;
            tabsContainer.parentNode.insertBefore(insightsContainer, tabsContainer.nextSibling);
        }
    }

    if (insightsContainer && insights.length > 0) {
        insightsContainer.innerHTML = `
            <h3 style="margin-bottom: 15px; color: ${darkMode ? '#e0e0e0' : '#333'};">
                <i class="fas fa-lightbulb" style="color: #fbbf24;"></i> Season Insights
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                ${insights.map(insight => `
                    <div style="background: ${darkMode ? 'rgba(20, 20, 35, 0.8)' : 'white'}; padding: 15px; border-radius: 8px; border: 1px solid ${darkMode ? 'rgba(102, 126, 234, 0.2)' : '#e9ecef'};">
                        <h4 style="margin-bottom: 10px; color: ${darkMode ? '#e0e0e0' : '#333'}; font-size: 1rem;">
                            <i class="fas fa-chart-pie" style="color: #667eea; margin-right: 5px;"></i>
                            ${insight.title}
                        </h4>
                        <ul style="list-style: none; padding: 0; margin: 0;">
                            ${insight.content.map(item => `
                                <li style="padding: 5px 0; color: ${darkMode ? '#a0a0a0' : '#6c757d'}; font-size: 0.9rem; border-bottom: 1px solid ${darkMode ? 'rgba(102, 126, 234, 0.1)' : '#e9ecef'};">
                                    ${item}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `).join('')}
            </div>
        `;
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
                <div style="margin-top: 10px; font-size: 0.9rem; color: ${darkMode ? '#a0a0a0' : '#6c757d'};">
                    Confidence: ${pred.confidence}%
                </div>
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
                <div style="margin-top: 15px; padding: 10px; background: ${darkMode ? 'rgba(20, 20, 35, 0.8)' : '#f8f9fa'}; border-radius: 8px; border: 1px solid ${pred.is_correct ? 'rgba(74, 222, 128, 0.3)' : 'rgba(248, 113, 113, 0.3)'};">
                    <div style="font-size: 0.9rem; color: ${darkMode ? '#a0a0a0' : '#6c757d'}; margin-bottom: 5px;">Actual Result</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: ${pred.is_correct ? '#4ade80' : '#f87171'};">
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
            <div class="team-rank" style="color: ${getRankColor(team.rank)}">#${team.rank}</div>
            <div class="team-info">
                <div class="team-name-display">${team.team}</div>
                <div style="font-size: 0.85rem; color: ${darkMode ? '#a0a0a0' : '#6c757d'}; margin-top: 5px;">
                    ${team.wins}W ${team.draws}D ${team.losses}L | ${team.points} pts
                </div>
                ${team.form ? `
                    <div style="font-size: 0.8rem; margin-top: 5px;">
                        Form: <span style="font-weight: 600;">${team.form}</span>
                    </div>
                ` : ''}
            </div>
            <div style="text-align: right;">
                <div class="team-elo-display" style="color: ${getRankColor(team.rank)}">${team.elo}</div>
                <div style="font-size: 0.8rem; color: ${darkMode ? '#a0a0a0' : '#6c757d'}; margin-top: 5px;">
                    ${team.goal_difference > 0 ? '+' : ''}${team.goal_difference} GD
                </div>
            </div>
        </div>
    `).join('');
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
                '#4ade80'
            ),
            createEnhancedPerformanceCard(
                'Total Matches',
                performance.total_matches,
                'Matches analyzed this season',
                'fa-database',
                '#667eea'
            ),
            createEnhancedPerformanceCard(
                'High Confidence',
                `${performance.high_confidence_accuracy}%`,
                'Accuracy on predictions >70% confidence',
                'fa-chart-line',
                '#fbbf24'
            ),
            createEnhancedPerformanceCard(
                'Best Team',
                performance.best_predicting_team || 'N/A',
                `Highest prediction accuracy: ${performance.best_team_accuracy || 0}%`,
                'fa-trophy',
                '#f87171'
            )
        ];

        performanceGrid.innerHTML = enhancedCards.join('');
    }
}

// Update Header Stats
function updateHeaderStats(count) {
    if (performance.accuracy) {
        document.getElementById('accuracy').textContent = `${performance.accuracy}%`;
    }
    if (performance.total_matches) {
        document.getElementById('total-predictions').textContent = performance.total_matches;
    } else {
        document.getElementById('total-predictions').textContent = count;
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

    container.innerHTML = historical.map(pred => `
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
                <div class="prediction-comparison">
                    <div class="comparison-item">
                        <span class="comparison-label">Predicted:</span>
                        <span class="comparison-value prediction">${getPredictionIcon(pred.prediction)} ${pred.prediction}</span>
                    </div>
                    <div class="comparison-item">
                        <span class="comparison-label">Actual:</span>
                        <span class="comparison-value actual">${getPredictionIcon(pred.actual)} ${pred.actual}</span>
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

            <div style="margin-top: 10px; font-size: 0.85rem; color: ${darkMode ? '#a0a0a0' : '#6c757d'};">
                Confidence: ${pred.confidence}% | Importance: ${pred.importance}
            </div>
        </div>
    `).join('');
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

    const enhancedCards = [
        createEnhancedPerformanceCard(
            'Accuracy',
            performance.accuracy ? `${performance.accuracy}%` : '--%',
            'Overall prediction accuracy',
            'fa-bullseye',
            '#4ade80'
        ),
        createEnhancedPerformanceCard(
            'Log Loss',
            performance.log_loss ? performance.log_loss.toFixed(3) : '--',
            'Probability calibration',
            'fa-chart-line',
            '#667eea'
        ),
        createEnhancedPerformanceCard(
            'Total Predictions',
            performance.total_predictions ? performance.total_predictions.toLocaleString() : '--',
            'Matches analyzed',
            'fa-database',
            '#fbbf24'
        ),
        createEnhancedPerformanceCard(
            'Last Updated',
            performance.last_updated || '--',
            'Model training date',
            'fa-clock',
            '#f87171'
        )
    ];

    performanceGrid.innerHTML = enhancedCards.join('');
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
