// API Base URL
const API_BASE = '/api';

// State
let currentTab = 'predictions';
let predictions = [];
let teams = [];
let performance = {};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
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

// Load All Data
async function loadAllData() {
    try {
        await Promise.all([
            loadPredictions(),
            loadTeams(),
            loadPerformance()
        ]);
        updateLastUpdated();
    } catch (error) {
        console.error('Error loading data:', error);
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
        <div class="prediction-card" onclick="showMatchDetail(${pred.id})">
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
                <div class="prediction-value">${pred.prediction}</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${pred.confidence}%"></div>
                </div>
                <div style="margin-top: 10px; font-size: 0.9rem; color: #6c757d;">
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
        <div class="team-card">
            <div class="team-rank">#${team.rank}</div>
            <div class="team-info">
                <div class="team-name-display">${team.team}</div>
            </div>
            <div class="team-elo-display">${team.elo}</div>
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
}

// Update Header Stats
function updateHeaderStats(count) {
    if (performance.accuracy) {
        document.getElementById('accuracy').textContent = `${performance.accuracy}%`;
    }
    document.getElementById('total-predictions').textContent = count;
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
