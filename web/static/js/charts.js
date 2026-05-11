// ===== Chart.js Interactive Charts =====
let charts = {};
let chartData = null;


// Mobile chart rendering fix
function getChartOptions(isSmall) {
  var isMobile = window.innerWidth <= 768;
  return {
    responsive: true,
    maintainAspectRatio: false,
    devicePixelRatio: isMobile ? 1 : window.devicePixelRatio || 1,
    interaction: {
      intersect: false,
      mode: 'index'
    },
    plugins: {
      legend: {
        position: isMobile ? 'bottom' : 'top',
        labels: {
          boxWidth: isMobile ? 10 : 40,
          font: { size: isMobile ? 10 : 12 }
        }
      },
      tooltip: {
        enabled: true,
        mode: 'nearest'
      }
    },
    animation: {
      duration: isMobile ? 200 : 750
    }
  };
}

function renderChartIfVisible(ctx, config) {
  if (!ctx) return null;
  var rect = ctx.getBoundingClientRect();
  if (rect.width < 10 || rect.height < 10) {
    ctx.style.height = (window.innerWidth <= 480 ? '180px' : window.innerWidth <= 768 ? '220px' : '280px');
    ctx.style.width = '100%';
  }
  return new Chart(ctx, config);
}


async function loadChartData() {
  try {
    const response = await fetch(`${API_BASE}/chart-data`);
    const result = await response.json();
    if (result.success) {
      chartData = result.data;
      renderAllCharts();
    }
  } catch (error) {
    console.error('Error loading chart data:', error);
  }
}

async function refreshChartData() {
  await loadChartData();
}

function renderAllCharts() {
  if (!chartData) return;
  renderAccuracyChart();
  renderDistributionChart();
  renderCalibrationChart();
  renderEloChart();
}

function renderAccuracyChart() {
  const ctx = document.getElementById('accuracy-chart');
  if (!ctx || !chartData.accuracy_over_time) return;

  if (charts.accuracy) charts.accuracy.destroy();

  const data = chartData.accuracy_over_time;
  var isMobile = window.innerWidth <= 768;
  charts.accuracy = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(d => d.month),
      datasets: [{
        label: 'Accuracy %',
        data: data.map(d => d.accuracy),
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#6366f1',
        pointRadius: isMobile ? 2 : 4,
        pointHoverRadius: 6,
        borderWidth: isMobile ? 2 : 3
      }, {
        label: 'Matches',
        data: data.map(d => d.total),
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        fill: false,
        tension: 0.4,
        pointRadius: isMobile ? 1 : 3,
        yAxisID: 'y1',
        borderWidth: isMobile ? 1.5 : 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      devicePixelRatio: isMobile ? 1 : (window.devicePixelRatio || 1),
      animation: { duration: isMobile ? 200 : 750 },
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { position: isMobile ? 'bottom' : 'top', labels: { boxWidth: isMobile ? 10 : 40, font: { size: isMobile ? 10 : 12 } } }
      },
      scales: {
        y: { beginAtZero: true, max: 100, title: { display: !isMobile, text: 'Accuracy %' }, ticks: { font: { size: isMobile ? 9 : 11 } } },
        y1: { position: 'right', beginAtZero: true, title: { display: !isMobile, text: 'Matches' }, grid: { drawOnChartArea: false }, ticks: { font: { size: isMobile ? 9 : 11 } } },
        x: { ticks: { font: { size: isMobile ? 9 : 11 } } }
      }
    }
  });
}

function renderDistributionChart() {
  const ctx = document.getElementById('distribution-chart');
  if (!ctx || !chartData.prediction_distribution) return;

  if (charts.distribution) charts.distribution.destroy();

  const dist = chartData.prediction_distribution;
  var isMobile = window.innerWidth <= 768;
  charts.distribution = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Home Wins', 'Draws', 'Away Wins'],
      datasets: [{
        data: [dist.home_wins, dist.draws, dist.away_wins],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderWidth: isMobile ? 1 : 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      devicePixelRatio: isMobile ? 1 : (window.devicePixelRatio || 1),
      animation: { duration: isMobile ? 200 : 750 },
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: isMobile ? 10 : 40, padding: isMobile ? 10 : 20, font: { size: isMobile ? 10 : 12 } } },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
              return ctx.label + ': ' + ctx.parsed + ' (' + pct + '%)';
            }
          }
        }
      }
    }
  });
}

function renderCalibrationChart() {
  const ctx = document.getElementById('calibration-chart');
  if (!ctx || !chartData.confidence_calibration) return;

  if (charts.calibration) charts.calibration.destroy();

  const cal = chartData.confidence_calibration;
  var isMobile = window.innerWidth <= 768;
  charts.calibration = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: cal.map(d => d.bucket),
      datasets: [{
        label: 'Actual Accuracy %',
        data: cal.map(d => d.accuracy),
        backgroundColor: cal.map(d => d.accuracy >= 60 ? 'rgba(16, 185, 129, 0.8)' : d.accuracy >= 40 ? 'rgba(245, 158, 11, 0.8)' : 'rgba(239, 68, 68, 0.8)'),
        borderRadius: isMobile ? 4 : 6,
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      devicePixelRatio: isMobile ? 1 : (window.devicePixelRatio || 1),
      animation: { duration: isMobile ? 200 : 750 },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              const item = cal[ctx.dataIndex];
              return ['Accuracy: ' + item.accuracy + '%', 'Matches: ' + item.total];
            }
          }
        }
      },
      scales: {
        y: { beginAtZero: true, max: 100, title: { display: !isMobile, text: 'Accuracy %' }, ticks: { font: { size: isMobile ? 9 : 11 } } },
        x: { title: { display: !isMobile, text: 'Confidence Bucket' }, ticks: { font: { size: isMobile ? 8 : 11 } } }
      }
    }
  });
}

function renderEloChart() {
  const ctx = document.getElementById('elo-chart');
  if (!ctx || !chartData.top_teams_elo) return;

  if (charts.elo) charts.elo.destroy();

  const teams = chartData.top_teams_elo;
  const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#8b5cf6', '#6366f1', '#f59e0b', '#ef4444'];
  var isMobile = window.innerWidth <= 768;
  charts.elo = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: teams.map(t => t.team),
      datasets: [{
        label: 'ELO Rating',
        data: teams.map(t => t.elo),
        backgroundColor: teams.map((_, i) => colors[i % colors.length] + 'cc'),
        borderRadius: isMobile ? 4 : 6,
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      devicePixelRatio: isMobile ? 1 : (window.devicePixelRatio || 1),
      animation: { duration: isMobile ? 200 : 750 },
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: {
        x: { title: { display: !isMobile, text: 'ELO Rating' }, ticks: { font: { size: isMobile ? 9 : 11 } } },
        y: { ticks: { font: { size: isMobile ? 9 : 11 } } }
      }
    }
  });
}

// ===== Historical Search with Pagination =====
let histSearchPage = 1;
let histSearchTotal = 0;
let histSearchPerPage = 20;
let histSearchDebounce = null;

function debounceHistoricalSearch() {
  clearTimeout(histSearchDebounce);
  histSearchDebounce = setTimeout(function() {
    histSearchPage = 1;
    searchHistorical();
  }, 300);
}

async function searchHistorical() {
  const container = document.getElementById('historical-list');
  const paginationEl = document.getElementById('historical-pagination');

  const team = document.getElementById('hist-team-search').value;
  const resultFilter = document.getElementById('hist-result-filter').value;
  const predictionFilter = document.getElementById('hist-prediction-filter').value;
  const minConf = document.getElementById('hist-conf-min').value;
  const maxConf = document.getElementById('hist-conf-max').value;

  const params = new URLSearchParams({
    page: histSearchPage,
    per_page: histSearchPerPage
  });
  if (team) params.set('team', team);
  if (resultFilter) params.set('result', resultFilter);
  if (predictionFilter) params.set('prediction', predictionFilter);
  if (minConf && minConf !== '0') params.set('min_confidence', minConf);
  if (maxConf && maxConf !== '100') params.set('max_confidence', maxConf);

  const dateFrom = document.getElementById('date-from').value;
  const dateTo = document.getElementById('date-to').value;
  if (dateFrom) params.set('date_from', dateFrom);
  if (dateTo) params.set('date_to', dateTo);

  container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i><p>Searching...</p></div>';

  try {
    const response = await fetch(API_BASE + '/historical/search?' + params);
    const result = await response.json();

    if (result.success) {
      histSearchTotal = result.total;
      const stats = result.stats;

      document.getElementById('filter-info').innerHTML =
        '<i class="fas fa-filter"></i> Showing ' + result.data.length + ' of ' + result.total +
        ' matches (Page ' + result.page + '/' + result.total_pages + ') &mdash; ' + stats.accuracy + '% accuracy';

      document.getElementById('hist-accuracy').textContent = stats.accuracy + '%';
      document.getElementById('hist-total').textContent = stats.total;
      document.getElementById('hist-correct').textContent = stats.correct;

      if (result.data.length === 0) {
        container.innerHTML = '<div class="loading"><i class="fas fa-search"></i><p>No matches found</p></div>';
        paginationEl.innerHTML = '';
        return;
      }

      container.innerHTML = result.data.map(function(pred) { return renderHistoricalCard(pred); }).join('');
      renderPagination(paginationEl, result.page, result.total_pages);
    }
  } catch (error) {
    console.error('Error searching historical data:', error);
    container.innerHTML = '<div class="loading"><i class="fas fa-exclamation-triangle"></i><p>Search failed</p></div>';
  }
}

function renderPagination(container, currentPage, totalPages) {
  if (totalPages <= 1) { container.innerHTML = ''; return; }

  let html = '';
  html += '<button onclick="goToPage(' + (currentPage - 1) + ')" ' + (currentPage === 1 ? 'disabled' : '') + '><i class="fas fa-chevron-left"></i></button>';

  const maxVisible = 5;
  let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
  let end = Math.min(totalPages, start + maxVisible - 1);
  start = Math.max(1, end - maxVisible + 1);

  if (start > 1) {
    html += '<button onclick="goToPage(1)">1</button>';
    if (start > 2) html += '<span class="page-info">...</span>';
  }

  for (let i = start; i <= end; i++) {
    html += '<button class="' + (i === currentPage ? 'active' : '') + '" onclick="goToPage(' + i + ')">' + i + '</button>';
  }

  if (end < totalPages) {
    if (end < totalPages - 1) html += '<span class="page-info">...</span>';
    html += '<button onclick="goToPage(' + totalPages + ')">' + totalPages + '</button>';
  }

  html += '<button onclick="goToPage(' + (currentPage + 1) + ')" ' + (currentPage === totalPages ? 'disabled' : '') + '><i class="fas fa-chevron-right"></i></button>';

  container.innerHTML = html;
}

function goToPage(page) {
  histSearchPage = page;
  searchHistorical();
  var section = document.getElementById('historical-section');
  if (section) {
    window.scrollTo({ top: section.offsetTop - 80, behavior: 'smooth' });
  }
}

function clearHistoricalSearch() {
  document.getElementById('hist-team-search').value = '';
  document.getElementById('hist-result-filter').value = '';
  document.getElementById('hist-prediction-filter').value = '';
  document.getElementById('hist-conf-min').value = '0';
  document.getElementById('hist-conf-max').value = '100';
  document.getElementById('date-from').value = '';
  document.getElementById('date-to').value = '';
  histSearchPage = 1;
  searchHistorical();
}

// ===== Enhanced Match Detail Modal =====
async function showMatchDetail(matchId) {
  var modal = document.getElementById('match-modal');
  var modalBody = document.getElementById('modal-body');

  modalBody.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i><p>Loading match details...</p></div>';
  modal.classList.add('active');

  try {
    var response = await fetch(API_BASE + '/match/' + matchId + '/detail');
    var result = await response.json();

    if (result.success) {
      renderMatchDetail(result.data);
    } else {
      modalBody.innerHTML = '<div class="loading"><i class="fas fa-exclamation-triangle"></i><p>Failed to load match details</p></div>';
    }
  } catch (error) {
    console.error('Error loading match detail:', error);
    modalBody.innerHTML = '<div class="loading"><i class="fas fa-exclamation-triangle"></i><p>Failed to load match details</p></div>';
  }
}

function renderMatchDetail(data) {
  var match = data.match;
  var eloCmp = data.elo_comparison;
  var homeStats = data.home_stats;
  var awayStats = data.away_stats;

  document.getElementById('modal-title').textContent = match.home_team + ' vs ' + match.away_team;

  var html = '';

  // Match info header
  html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;padding:0.75rem 1rem;background:var(--bg-secondary);border-radius:var(--radius-lg);">';
  html += '<div><i class="fas fa-calendar" style="color:var(--primary-color);"></i> ' + (match.date || 'TBD') + '</div>';
  html += '<div><span class="league-badge">' + (match.league || 'Premier League') + '</span></div>';
  html += '</div>';

  // Team names & scores
  if (match.home_goals !== undefined && match.actual && match.actual !== 'Not Played') {
    html += '<div style="display:flex;justify-content:space-between;align-items:center;text-align:center;margin-bottom:1.5rem;">';
    html += '<div style="flex:1;"><div style="font-size:1.25rem;font-weight:800;">' + match.home_team + '</div></div>';
    html += '<div style="font-size:2rem;font-weight:900;color:var(--primary-color);padding:0 1.5rem;">' + match.home_goals + ' - ' + match.away_goals + '</div>';
    html += '<div style="flex:1;"><div style="font-size:1.25rem;font-weight:800;">' + match.away_team + '</div></div>';
    html += '</div>';
  } else {
    html += '<div style="display:flex;justify-content:space-between;align-items:center;text-align:center;margin-bottom:1.5rem;">';
    html += '<div style="flex:1;"><div style="font-size:1.25rem;font-weight:800;">' + match.home_team + '</div></div>';
    html += '<div style="font-size:1.5rem;font-weight:900;color:var(--primary-color);padding:0 1.5rem;">VS</div>';
    html += '<div style="flex:1;"><div style="font-size:1.25rem;font-weight:800;">' + match.away_team + '</div></div>';
    html += '</div>';
  }

  // ELO Comparison
  html += '<div class="detail-section-title"><i class="fas fa-signal"></i> ELO Ratings</div>';
  html += '<div class="detail-elo-comparison">';
  html += '<div class="detail-elo-bar home">';
  html += '<div class="elo-label">' + match.home_team + '</div>';
  html += '<div class="elo-visual"><div class="elo-fill" style="width:' + eloCmp.home.percentage + '%"></div></div>';
  html += '<div class="elo-value">' + eloCmp.home.elo + '</div>';
  html += '</div>';
  html += '<div class="detail-elo-diff">' + (eloCmp.diff > 0 ? '+' : '') + eloCmp.diff + '</div>';
  html += '<div class="detail-elo-bar away">';
  html += '<div class="elo-label">' + match.away_team + '</div>';
  html += '<div class="elo-visual"><div class="elo-fill" style="width:' + eloCmp.away.percentage + '%"></div></div>';
  html += '<div class="elo-value">' + eloCmp.away.elo + '</div>';
  html += '</div>';
  html += '</div>';

  // Probability breakdown
  var homeProb = match.home_win_prob || match.home_prob || 0;
  var drawProb = match.draw_prob || 0;
  var awayProb = match.away_win_prob || match.away_prob || 0;

  html += '<div class="detail-section-title"><i class="fas fa-chart-bar"></i> Probability Breakdown</div>';
  html += '<div class="detail-prob-section">';
  html += '<div class="detail-prob-bar"><div class="prob-label">Home Win</div>';
  html += '<div class="prob-track"><div class="prob-fill home" style="width:' + homeProb + '%">' + (homeProb > 15 ? homeProb + '%' : '') + '</div></div>';
  html += '<div class="prob-pct" style="color:var(--success-color)">' + homeProb + '%</div></div>';
  html += '<div class="detail-prob-bar"><div class="prob-label">Draw</div>';
  html += '<div class="prob-track"><div class="prob-fill draw" style="width:' + drawProb + '%">' + (drawProb > 15 ? drawProb + '%' : '') + '</div></div>';
  html += '<div class="prob-pct" style="color:var(--warning-color)">' + drawProb + '%</div></div>';
  html += '<div class="detail-prob-bar"><div class="prob-label">Away Win</div>';
  html += '<div class="prob-track"><div class="prob-fill away" style="width:' + awayProb + '%">' + (awayProb > 15 ? awayProb + '%' : '') + '</div></div>';
  html += '<div class="prob-pct" style="color:var(--danger-color)">' + awayProb + '%</div></div>';
  html += '</div>';

  // Prediction & confidence
  html += '<div class="detail-section-title"><i class="fas fa-brain"></i> Model Prediction</div>';
  html += '<div style="display:flex;gap:1rem;margin-bottom:1rem;">';
  html += '<div style="flex:1;padding:1rem;background:var(--bg-secondary);border-radius:var(--radius-lg);text-align:center;">';
  html += '<div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:0.25rem;">Prediction</div>';
  html += '<div style="font-size:1.25rem;font-weight:700;color:var(--primary-color);">' + getPredictionIcon(match.prediction) + ' ' + match.prediction + '</div>';
  html += '</div>';
  html += '<div style="flex:1;padding:1rem;background:var(--bg-secondary);border-radius:var(--radius-lg);text-align:center;">';
  html += '<div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:0.25rem;">Confidence</div>';
  html += '<div style="font-size:1.25rem;font-weight:700;color:' + getConfidenceColor(match.confidence) + '">' + match.confidence + '%</div>';
  html += '<div class="confidence-bar" style="margin-top:0.5rem;"><div class="confidence-fill" style="width:' + match.confidence + '%;background:' + getConfidenceColor(match.confidence) + '"></div></div>';
  html += '</div></div>';

  // Actual result (if historical)
  if (match.actual && match.actual !== 'Not Played') {
    html += '<div style="padding:1rem;background:' + (match.is_correct ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)') + ';border-radius:var(--radius-lg);border-left:4px solid ' + (match.is_correct ? 'var(--success-color)' : 'var(--danger-color)') + ';margin-bottom:1rem;">';
    html += '<div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:0.25rem;">Actual Result</div>';
    html += '<div style="font-size:1.25rem;font-weight:700;color:' + (match.is_correct ? 'var(--success-color)' : 'var(--danger-color)') + ';">';
    html += (match.is_correct ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-times-circle"></i>') + ' ' + match.actual;
    html += '</div></div>';
  }

  // Team stats comparison (if available)
  if (homeStats && awayStats) {
    html += '<div class="detail-section-title"><i class="fas fa-table"></i> Team Stats Comparison</div>';
    html += '<div class="detail-team-stats">';

    var statRows = [
      ['Points', homeStats.points, awayStats.points],
      ['Wins', homeStats.wins, awayStats.wins],
      ['Draws', homeStats.draws, awayStats.draws],
      ['Losses', homeStats.losses, awayStats.losses],
      ['Goals/Game', homeStats.goals_per_game, awayStats.goals_per_game],
      ['Conceded/G', homeStats.goals_conceded_per_game, awayStats.goals_conceded_per_game],
      ['Goal Diff', homeStats.goal_difference, awayStats.goal_difference],
      ['Win Rate', homeStats.win_rate + '%', awayStats.win_rate + '%']
    ];

    for (var i = 0; i < statRows.length; i++) {
      var name = statRows[i][0];
      var homeVal = statRows[i][1];
      var awayVal = statRows[i][2];
      html += '<div class="stat-row">';
      html += '<div class="home-val">' + homeVal + '</div>';
      html += '<div class="stat-name">' + name + '</div>';
      html += '<div class="away-val">' + awayVal + '</div>';
      html += '</div>';
    }
    html += '</div>';

    // Form
    html += '<div style="display:flex;justify-content:space-between;margin-top:1rem;">';
    html += '<div><div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:0.5rem;">' + match.home_team + ' Form</div>';
    html += renderFormDots(homeStats.form_string || homeStats.form || '');
    html += '</div>';
    html += '<div style="text-align:right;"><div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:0.5rem;">' + match.away_team + ' Form</div>';
    html += renderFormDots(awayStats.form_string || awayStats.form || '');
    html += '</div></div>';
  }

  document.getElementById('modal-body').innerHTML = html;
}

function renderFormDots(formStr) {
  var html = '<div class="form-indicator">';
  for (var i = 0; i < formStr.length; i++) {
    var ch = formStr[i];
    html += '<span class="form-dot ' + ch + '">' + ch + '</span>';
  }
  html += '</div>';
  return html;
}


// Re-render charts on resize/orientation change
var chartResizeTimer = null;
window.addEventListener('resize', function() {
  clearTimeout(chartResizeTimer);
  chartResizeTimer = setTimeout(function() {
    if (chartData) renderAllCharts();
  }, 250);
});
