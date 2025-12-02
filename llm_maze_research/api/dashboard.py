"""Dashboard routes for experiment visualization."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_home():
    """Main dashboard page."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LLM Maze Navigation - Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 1400px;
                margin: 0 auto;
            }

            header {
                background: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }

            h1 {
                color: #333;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 15px;
            }

            .logo {
                font-size: 40px;
            }

            .subtitle {
                color: #666;
                font-size: 16px;
            }

            .controls {
                background: white;
                padding: 25px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }

            .control-group {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }

            .input-group {
                display: flex;
                flex-direction: column;
            }

            label {
                color: #333;
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 14px;
            }

            input, select {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                transition: border-color 0.3s;
            }

            input:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }

            .button-group {
                display: flex;
                gap: 10px;
                align-items: flex-end;
            }

            button {
                padding: 12px 25px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }

            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
            }

            button:active {
                transform: translateY(0);
            }

            .secondary-btn {
                background: #f0f0f0;
                color: #333;
            }

            .secondary-btn:hover {
                background: #e0e0e0;
            }

            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .metric-card {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border-left: 5px solid #667eea;
            }

            .metric-card.success {
                border-left-color: #4caf50;
            }

            .metric-card.warning {
                border-left-color: #ff9800;
            }

            .metric-card.error {
                border-left-color: #f44336;
            }

            .metric-title {
                color: #999;
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 10px;
            }

            .metric-value {
                font-size: 32px;
                font-weight: 700;
                color: #333;
                margin-bottom: 8px;
            }

            .metric-subtext {
                color: #666;
                font-size: 14px;
            }

            .charts-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .chart-card {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }

            .chart-title {
                font-size: 18px;
                font-weight: 600;
                color: #333;
                margin-bottom: 20px;
            }

            canvas {
                max-width: 100%;
            }

            .tool-stats {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }

            .stat-item {
                text-align: center;
                padding: 20px;
                background: #f5f5f5;
                border-radius: 8px;
            }

            .stat-number {
                font-size: 28px;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 5px;
            }

            .stat-label {
                color: #666;
                font-size: 14px;
            }

            .accuracy-slider {
                width: 100%;
                height: 8px;
                border-radius: 5px;
                background: linear-gradient(to right, #f44336, #ff9800, #4caf50);
                outline: none;
                -webkit-appearance: none;
                appearance: none;
            }

            .accuracy-slider::-webkit-slider-thumb {
                -webkit-appearance: none;
                appearance: none;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: white;
                cursor: pointer;
                border: 3px solid #667eea;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }

            .accuracy-slider::-moz-range-thumb {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: white;
                cursor: pointer;
                border: 3px solid #667eea;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }

            .slider-label {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }

            .slider-value {
                font-weight: 700;
                color: #667eea;
                font-size: 18px;
            }

            .episode-list {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }

            .episode-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 15px;
                border-bottom: 1px solid #eee;
                transition: background 0.2s;
            }

            .episode-item:hover {
                background: #f9f9f9;
            }

            .episode-item:last-child {
                border-bottom: none;
            }

            .episode-info {
                display: flex;
                align-items: center;
                gap: 20px;
            }

            .episode-badge {
                background: #667eea;
                color: white;
                padding: 8px 12px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 12px;
                min-width: 60px;
                text-align: center;
            }

            .episode-badge.success {
                background: #4caf50;
            }

            .episode-badge.failed {
                background: #f44336;
            }

            .episode-details {
                flex: 1;
            }

            .episode-name {
                font-weight: 600;
                color: #333;
                margin-bottom: 4px;
            }

            .episode-meta {
                color: #999;
                font-size: 12px;
            }

            .episode-stats {
                display: flex;
                gap: 20px;
            }

            .stat {
                text-align: right;
            }

            .stat-label {
                color: #999;
                font-size: 12px;
            }

            .stat-value {
                color: #333;
                font-weight: 600;
            }

            .loading {
                text-align: center;
                padding: 40px;
                color: white;
                font-size: 18px;
            }

            .spinner {
                border: 4px solid rgba(255,255,255,0.3);
                border-top: 4px solid white;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .status-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }

            .status-running {
                background: #fff3cd;
                color: #856404;
            }

            .status-complete {
                background: #d4edda;
                color: #155724;
            }

            .results-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }

            @media (max-width: 1200px) {
                .results-container {
                    grid-template-columns: 1fr;
                }
            }

            .maze-visualization {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }

            .maze-title {
                font-weight: 600;
                color: #333;
                margin-bottom: 15px;
                font-size: 16px;
            }

            #mazeCanvas {
                border: 2px solid #ddd;
                border-radius: 6px;
                background: white;
                max-width: 100%;
                height: auto;
            }

            .maze-legend {
                display: flex;
                gap: 20px;
                margin-top: 15px;
                font-size: 12px;
                flex-wrap: wrap;
            }

            .legend-item {
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .legend-color {
                width: 20px;
                height: 20px;
                border-radius: 3px;
            }

            .legend-start { background: #4caf50; }
            .legend-goal { background: #ff9800; }
            .legend-path { background: #667eea; }
            .legend-wall { background: #333; }

            .metrics-section {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }

            .all-episodes-section {
                background: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }

            .section-title {
                font-weight: 600;
                color: #333;
                margin-bottom: 20px;
                font-size: 18px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }

            .episodes-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
                gap: 15px;
            }

            .episode-canvas-container {
                background: #f9f9f9;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
            }

            .episode-canvas-container:hover {
                border-color: #667eea;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
            }

            .episode-canvas-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
                font-size: 13px;
            }

            .episode-number {
                font-weight: 600;
                color: #333;
            }

            .episode-status-mini {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }

            .episode-status-mini.success {
                background: #e8f5e9;
                color: #2e7d32;
            }

            .episode-status-mini.failed {
                background: #ffebee;
                color: #c62828;
            }

            .mini-canvas {
                width: 100%;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                display: block;
            }

            .episode-canvas-stats {
                display: flex;
                gap: 8px;
                margin-top: 8px;
                font-size: 11px;
                color: #666;
            }

            .canvas-stat {
                flex: 1;
                text-align: center;
            }

            .canvas-stat-value {
                font-weight: 600;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>
                    <span class="logo">🤖</span>
                    <div>
                        <div>LLM Maze Navigation Dashboard</div>
                        <div class="subtitle">Tool Overreliance Research Framework</div>
                    </div>
                </h1>
            </header>

            <div class="controls">
                <div class="control-group">
                    <div class="input-group">
                        <label>Maze Size</label>
                        <input type="number" id="mazeSize" value="12" min="8" max="32" step="4">
                    </div>
                    <div class="input-group">
                        <label>Difficulty</label>
                        <select id="difficulty">
                            <option value="easy">Easy</option>
                            <option value="medium" selected>Medium</option>
                            <option value="hard">Hard</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>Episodes</label>
                        <input type="number" id="episodes" value="10" min="1" max="100">
                    </div>
                </div>

                <div class="control-group">
                    <div class="input-group">
                        <label>Agent Strategy</label>
                        <select id="strategy">
                            <option value="adaptive" selected>Adaptive</option>
                            <option value="tool_trusting">Tool Trusting</option>
                            <option value="tool_avoiding">Tool Avoiding</option>
                            <option value="llm_solver">LLM Solver</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>LLM Model (for LLM Solver)</label>
                        <select id="llmModel">
                            <option value="openai" selected>OpenAI (gpt-3.5-turbo)</option>
                            <option value="openai-gpt4">OpenAI (gpt-4)</option>
                            <option value="openai-o1mini">OpenAI (o1-mini)</option>
                            <option value="openrouter">OpenRouter (free models)</option>
                            <option value="ollama">Ollama (local - free)</option>
                        </select>
                    </div>
                </div>

                <div class="control-group">
                    <div class="input-group">
                        <label>Noise Type</label>
                        <select id="noiseType">
                            <option value="none" selected>None (Perfect)</option>
                            <option value="random">Random</option>
                            <option value="biased">Biased</option>
                            <option value="delayed">Delayed</option>
                        </select>
                    </div>
                </div>

                <div class="control-group">
                    <div class="input-group">
                        <label>Tool Accuracy</label>
                        <div class="slider-label">
                            <span>Broken (0%)</span>
                            <span class="slider-value" id="accuracyValue">100%</span>
                            <span>Perfect (100%)</span>
                        </div>
                        <input type="range" id="toolAccuracy" class="accuracy-slider"
                               min="0" max="100" value="100" step="10">
                    </div>
                </div>

                <div class="button-group">
                    <button onclick="runExperiment()">🚀 Run Experiment</button>
                    <button class="secondary-btn" onclick="loadSampleData()">📊 Load Sample</button>
                </div>
            </div>

            <div id="results" style="display: none;">
                <div class="tool-stats">
                    <div class="chart-title">Tool Usage & Accuracy</div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-number" id="toolUsageCount">0</div>
                            <div class="stat-label">Tool Queries</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number" id="toolUsageRate">0%</div>
                            <div class="stat-label">Usage Rate</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number" id="toolAccuracyRate">0%</div>
                            <div class="stat-label">Tool Accuracy</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number" id="toolFollowRate">0%</div>
                            <div class="stat-label">Follow Rate</div>
                        </div>
                    </div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-card success">
                        <div class="metric-title">Success Rate</div>
                        <div class="metric-value" id="successRate">0%</div>
                        <div class="metric-subtext" id="successEpisodes">0/0 episodes solved</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-title">Average Steps</div>
                        <div class="metric-value" id="avgSteps">0</div>
                        <div class="metric-subtext">
                            Min: <span id="minSteps">0</span> | Max: <span id="maxSteps">0</span>
                        </div>
                    </div>

                    <div class="metric-card warning">
                        <div class="metric-title">Path Optimality</div>
                        <div class="metric-value" id="pathOptimality">0%</div>
                        <div class="metric-subtext">Efficiency vs optimal path</div>
                    </div>

                    <div class="metric-card error">
                        <div class="metric-title">Avg Final Distance</div>
                        <div class="metric-value" id="finalDistance">0</div>
                        <div class="metric-subtext">Steps from goal</div>
                    </div>
                </div>

                <div class="charts-grid">
                    <div class="chart-card">
                        <div class="chart-title">Episodes Performance</div>
                        <canvas id="episodeChart"></canvas>
                    </div>

                    <div class="chart-card">
                        <div class="chart-title">Metrics Overview</div>
                        <canvas id="metricsChart"></canvas>
                    </div>
                </div>

                <div class="results-container">
                    <div class="maze-visualization">
                        <div class="maze-title">First Episode Path Visualization</div>
                        <canvas id="mazeCanvas" width="400" height="400"></canvas>
                        <div class="maze-legend">
                            <div class="legend-item">
                                <div class="legend-color legend-start"></div>
                                <span>Start</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-color legend-goal"></div>
                                <span>Goal</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-color legend-path"></div>
                                <span>Agent Path</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-color legend-wall"></div>
                                <span>Wall (estimated)</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-color legend-tool" style="background: rgba(255, 152, 0, 0.3);"></div>
                                <span>🤖 LLM Used Tool</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="episode-list">
                    <div class="chart-title">Episode Details</div>
                    <div id="episodeDetails"></div>
                </div>

                <div class="all-episodes-section">
                    <div class="section-title">📊 All Episodes Path Visualization</div>
                    <div class="episodes-grid" id="episodesGrid"></div>
                </div>
            </div>

            <div id="loading" class="loading" style="display: none;">
                <div>Running Experiment...</div>
                <div class="spinner"></div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            let episodeChart = null;
            let metricsChart = null;

            // Update accuracy display
            document.getElementById('toolAccuracy').addEventListener('input', (e) => {
                document.getElementById('accuracyValue').textContent = e.target.value + '%';
            });

            async function runExperiment() {
                const llmModelSelect = document.getElementById('llmModel').value;
                let model = "gpt-3.5-turbo";
                let use_openai = true;

                if (llmModelSelect === "openai") {
                    model = "gpt-3.5-turbo";
                } else if (llmModelSelect === "openai-gpt4") {
                    model = "gpt-4";
                } else if (llmModelSelect === "openai-o1mini") {
                    model = "o1-mini";
                } else if (llmModelSelect === "openrouter") {
                    model = "openrouter";
                } else if (llmModelSelect === "ollama") {
                    model = "ollama";
                }

                const config = {
                    maze_size: parseInt(document.getElementById('mazeSize').value),
                    maze_difficulty: document.getElementById('difficulty').value,
                    num_episodes: parseInt(document.getElementById('episodes').value),
                    agent_strategy: document.getElementById('strategy').value,
                    noise_type: document.getElementById('noiseType').value,
                    noise_level: 1 - (parseInt(document.getElementById('toolAccuracy').value) / 100),
                    model: model,
                    use_openai: use_openai,
                    temperature: 0.7,
                    seed: 42
                };

                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';

                try {
                    const response = await fetch('/api/v1/experiments/start', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(config)
                    });

                    if (!response.ok) throw new Error('Failed to start experiment');

                    const result = await response.json();
                    const expId = result.experiment_id;

                    // Poll for results
                    let completed = false;
                    while (!completed) {
                        await new Promise(r => setTimeout(r, 1000));
                        const statusResponse = await fetch(`/api/v1/experiments/${expId}`);
                        const status = await statusResponse.json();

                        if (status.status === 'completed') {
                            const resultsResponse = await fetch(`/api/v1/experiments/${expId}/results`);
                            const data = await resultsResponse.json();
                            displayResults(data);
                            completed = true;
                        } else if (status.status === 'failed') {
                            alert('Experiment failed: ' + (status.error || 'Unknown error'));
                            completed = true;
                        }
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }

            function displayResults(data) {
                const metrics = data.metrics;

                // Store results data globally for decision details modal
                window.lastResultsData = data;

                // Update metrics
                document.getElementById('successRate').textContent =
                    (metrics.success_rate * 100).toFixed(1) + '%';
                document.getElementById('successEpisodes').textContent =
                    `${metrics.successful_episodes}/${metrics.total_episodes} episodes solved`;
                document.getElementById('avgSteps').textContent =
                    Math.round(metrics.avg_steps);
                document.getElementById('minSteps').textContent =
                    metrics.min_steps;
                document.getElementById('maxSteps').textContent =
                    metrics.max_steps;
                document.getElementById('pathOptimality').textContent =
                    (metrics.avg_path_optimality * 100).toFixed(1) + '%';
                document.getElementById('finalDistance').textContent =
                    Math.round(metrics.avg_final_distance);

                // Tool stats
                document.getElementById('toolUsageCount').textContent =
                    Math.round(metrics.avg_tool_queries);
                document.getElementById('toolUsageRate').textContent =
                    (metrics.avg_tool_usage_rate * 100).toFixed(1) + '%';
                document.getElementById('toolAccuracyRate').textContent =
                    (metrics.avg_tool_accuracy * 100).toFixed(1) + '%';
                document.getElementById('toolFollowRate').textContent =
                    (metrics.avg_tool_following_rate * 100).toFixed(1) + '%';

                // Draw maze visualization for first episode
                if (data.episodes && data.episodes.length > 0 && data.config) {
                    drawMazeVisualization(data.episodes[0], data.config.maze_size);
                    // Display all episodes in grid
                    displayAllEpisodes(data.episodes, data.config.maze_size);
                }

                // Charts
                updateCharts(data.episodes);

                // Episode details
                displayEpisodes(data.episodes);

                document.getElementById('results').style.display = 'block';
            }

            function updateCharts(episodes) {
                const steps = episodes.map(e => e.trajectory.length);
                const success = episodes.map(e => e.decisions.length > 0 ? 1 : 0);

                // Episode Chart
                const ctx1 = document.getElementById('episodeChart').getContext('2d');
                if (episodeChart) episodeChart.destroy();
                episodeChart = new Chart(ctx1, {
                    type: 'bar',
                    data: {
                        labels: Array.from({length: steps.length}, (_, i) => `Ep ${i}`),
                        datasets: [{
                            label: 'Steps',
                            data: steps,
                            backgroundColor: success.map(s => s ? '#4caf50' : '#f44336'),
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true } }
                    }
                });

                // Metrics Chart
                const ctx2 = document.getElementById('metricsChart').getContext('2d');
                if (metricsChart) metricsChart.destroy();
                metricsChart = new Chart(ctx2, {
                    type: 'doughnut',
                    data: {
                        labels: ['Success', 'Failed'],
                        datasets: [{
                            data: [
                                episodes.filter(e => e.decisions.length > 0).length,
                                episodes.length - episodes.filter(e => e.decisions.length > 0).length
                            ],
                            backgroundColor: ['#4caf50', '#f44336']
                        }]
                    },
                    options: { responsive: true }
                });
            }

            function drawMiniMazeVisualization(episode, mazeSize, canvasElement) {
                if (!canvasElement || !episode || !episode.trajectory || episode.trajectory.length === 0) {
                    return;
                }

                const ctx = canvasElement.getContext('2d');
                const trajectory = episode.trajectory;
                const maze = episode.maze;

                // Get start and goal positions
                const startPos = trajectory[0].agent_pos;
                const goalPos = trajectory[0].goal_pos;

                // Dimensions - smaller for grid
                const width = canvasElement.width;
                const height = canvasElement.height;
                const padding = 8;
                const availableWidth = width - (padding * 2);
                const availableHeight = height - (padding * 2);
                const cellSize = Math.min(availableWidth / mazeSize, availableHeight / mazeSize);

                // Clear canvas
                ctx.fillStyle = '#fff';
                ctx.fillRect(0, 0, width, height);

                // Draw walls if maze data exists
                if (maze) {
                    ctx.fillStyle = '#333';
                    for (let row = 0; row < maze.length; row++) {
                        for (let col = 0; col < maze[row].length; col++) {
                            if (maze[row][col] === 1) {  // Wall cell
                                const x = padding + col * cellSize;
                                const y = padding + row * cellSize;
                                ctx.fillRect(x, y, cellSize, cellSize);
                            }
                        }
                    }
                }

                // Draw grid (lighter)
                ctx.strokeStyle = '#f0f0f0';
                ctx.lineWidth = 0.3;
                for (let i = 0; i <= mazeSize; i++) {
                    const x = padding + (i * cellSize);
                    ctx.beginPath();
                    ctx.moveTo(x, padding);
                    ctx.lineTo(x, padding + (mazeSize * cellSize));
                    ctx.stroke();

                    const y = padding + (i * cellSize);
                    ctx.beginPath();
                    ctx.moveTo(padding, y);
                    ctx.lineTo(padding + (mazeSize * cellSize), y);
                    ctx.stroke();
                }

                // Build tool query positions set for quick lookup
                const toolQuerySteps = new Set();
                if (episode.tool_queries) {
                    for (let query of episode.tool_queries) {
                        if (query && query.step !== undefined) {
                            toolQuerySteps.add(query.step);
                        }
                    }
                }

                // Draw visited cells
                ctx.fillStyle = 'rgba(102, 126, 234, 0.08)';
                for (let i = 0; i < trajectory.length; i++) {
                    const pos = trajectory[i].agent_pos;
                    const x = padding + pos[1] * cellSize;
                    const y = padding + pos[0] * cellSize;
                    ctx.fillRect(x, y, cellSize, cellSize);

                    // Highlight cells where tool was queried
                    if (toolQuerySteps.has(i)) {
                        ctx.fillStyle = 'rgba(255, 152, 0, 0.3)';  // Orange highlight
                        ctx.fillRect(x, y, cellSize, cellSize);
                        ctx.fillStyle = 'rgba(102, 126, 234, 0.08)';
                    }
                }

                // Draw path
                ctx.strokeStyle = '#667eea';
                ctx.lineWidth = 1;
                ctx.setLineDash([1, 1]);
                ctx.beginPath();
                for (let i = 0; i < trajectory.length; i++) {
                    const pos = trajectory[i].agent_pos;
                    const x = padding + (pos[1] + 0.5) * cellSize;
                    const y = padding + (pos[0] + 0.5) * cellSize;
                    if (i === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                }
                ctx.stroke();
                ctx.setLineDash([]);

                // Draw start (green)
                ctx.fillStyle = '#4caf50';
                ctx.beginPath();
                ctx.arc(padding + (startPos[1] + 0.5) * cellSize, padding + (startPos[0] + 0.5) * cellSize, cellSize / 4, 0, Math.PI * 2);
                ctx.fill();

                // Draw goal (orange)
                ctx.fillStyle = '#ff9800';
                ctx.beginPath();
                ctx.arc(padding + (goalPos[1] + 0.5) * cellSize, padding + (goalPos[0] + 0.5) * cellSize, cellSize / 4, 0, Math.PI * 2);
                ctx.fill();

                // Draw final position if different from start
                if (trajectory.length > 1) {
                    const finalPos = trajectory[trajectory.length - 1].agent_pos;
                    if (finalPos[0] !== startPos[0] || finalPos[1] !== startPos[1]) {
                        ctx.fillStyle = '#2196f3';
                        ctx.beginPath();
                        ctx.arc(padding + (finalPos[1] + 0.5) * cellSize, padding + (finalPos[0] + 0.5) * cellSize, cellSize / 5, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
            }

            function displayAllEpisodes(episodes, mazeSize) {
                const grid = document.getElementById('episodesGrid');
                if (!grid) return;

                grid.innerHTML = episodes.map((episode, index) => {
                    const success = episode.decisions && episode.decisions.length > 0;
                    const steps = episode.trajectory.length;
                    const toolQueries = episode.tool_queries ? episode.tool_queries.length : 0;

                    return `
                        <div class="episode-canvas-container">
                            <div class="episode-canvas-header">
                                <span class="episode-number">Episode ${index}</span>
                                <span class="episode-status-mini ${success ? 'success' : 'failed'}">
                                    ${success ? '✓' : '✗'}
                                </span>
                            </div>
                            <canvas class="mini-canvas" id="episodeCanvas_${index}" width="200" height="200" data-episode-index="${index}"></canvas>
                            <div class="episode-canvas-stats">
                                <div class="canvas-stat">
                                    <div class="canvas-stat-value">${steps}</div>
                                    <div>Steps</div>
                                </div>
                                <div class="canvas-stat">
                                    <div class="canvas-stat-value">${toolQueries}</div>
                                    <div>Tools</div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');

                // Draw each episode after creating the HTML
                episodes.forEach((episode, index) => {
                    const canvas = document.getElementById(`episodeCanvas_${index}`);
                    if (canvas) {
                        drawMiniMazeVisualization(episode, mazeSize, canvas);
                    }
                });
            }

            function drawMazeVisualization(episode, mazeSize) {
                const canvas = document.getElementById('mazeCanvas');
                if (!canvas || !episode || !episode.trajectory || episode.trajectory.length === 0) {
                    return;
                }

                const ctx = canvas.getContext('2d');
                const trajectory = episode.trajectory;
                const maze = episode.maze;

                // Get start and goal positions
                const start = trajectory[0];
                const goal = trajectory[0];
                const startPos = start.agent_pos;
                const goalPos = goal.goal_pos;

                // Calculate grid size based on maze size
                const padding = 20;
                const availableWidth = canvas.width - (padding * 2);
                const availableHeight = canvas.height - (padding * 2);
                const cellSize = Math.min(availableWidth / mazeSize, availableHeight / mazeSize);

                // Clear canvas
                ctx.fillStyle = '#fff';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Draw walls if maze data exists
                if (maze) {
                    ctx.fillStyle = '#333';
                    for (let row = 0; row < maze.length; row++) {
                        for (let col = 0; col < maze[row].length; col++) {
                            if (maze[row][col] === 1) {  // Wall cell
                                const x = padding + col * cellSize;
                                const y = padding + row * cellSize;
                                ctx.fillRect(x, y, cellSize, cellSize);
                            }
                        }
                    }
                }

                // Draw grid background
                ctx.strokeStyle = '#e0e0e0';
                ctx.lineWidth = 0.5;
                for (let i = 0; i <= mazeSize; i++) {
                    const x = padding + (i * cellSize);
                    const y1 = padding;
                    const y2 = padding + (mazeSize * cellSize);
                    ctx.beginPath();
                    ctx.moveTo(x, y1);
                    ctx.lineTo(x, y2);
                    ctx.stroke();

                    const y = padding + (i * cellSize);
                    const x1 = padding;
                    const x2 = padding + (mazeSize * cellSize);
                    ctx.beginPath();
                    ctx.moveTo(x1, y);
                    ctx.lineTo(x2, y);
                    ctx.stroke();
                }

                // Draw agent path (light blue line)
                ctx.strokeStyle = '#667eea';
                ctx.lineWidth = 2;
                ctx.setLineDash([2, 2]);
                ctx.beginPath();
                for (let i = 0; i < trajectory.length; i++) {
                    const pos = trajectory[i].agent_pos;
                    const x = padding + (pos[1] + 0.5) * cellSize;
                    const y = padding + (pos[0] + 0.5) * cellSize;
                    if (i === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                }
                ctx.stroke();
                ctx.setLineDash([]);

                // Build tool query positions set for quick lookup
                const toolQuerySteps = new Set();
                if (episode.tool_queries) {
                    for (let query of episode.tool_queries) {
                        if (query && query.step !== undefined) {
                            toolQuerySteps.add(query.step);
                        }
                    }
                }

                // Draw visited cells (light blue)
                ctx.fillStyle = 'rgba(102, 126, 234, 0.1)';
                for (let i = 0; i < trajectory.length; i++) {
                    const pos = trajectory[i].agent_pos;
                    const x = padding + pos[1] * cellSize;
                    const y = padding + pos[0] * cellSize;
                    ctx.fillRect(x, y, cellSize, cellSize);

                    // Highlight cells where LLM decided to use tool (orange)
                    if (toolQuerySteps.has(i)) {
                        ctx.fillStyle = 'rgba(255, 152, 0, 0.3)';
                        ctx.fillRect(x, y, cellSize, cellSize);
                        ctx.fillStyle = 'rgba(102, 126, 234, 0.1)';
                    }
                }

                // Draw start position (green)
                ctx.fillStyle = '#4caf50';
                ctx.beginPath();
                ctx.arc(padding + (startPos[1] + 0.5) * cellSize, padding + (startPos[0] + 0.5) * cellSize, cellSize / 3, 0, Math.PI * 2);
                ctx.fill();

                // Draw goal position (orange star)
                ctx.fillStyle = '#ff9800';
                const goalX = padding + (goalPos[1] + 0.5) * cellSize;
                const goalY = padding + (goalPos[0] + 0.5) * cellSize;
                const starSize = cellSize / 3;

                // Draw 5-pointed star
                ctx.beginPath();
                for (let i = 0; i < 10; i++) {
                    const angle = (i * Math.PI) / 5 - Math.PI / 2;
                    const radius = i % 2 === 0 ? starSize : starSize / 2;
                    const x = goalX + Math.cos(angle) * radius;
                    const y = goalY + Math.sin(angle) * radius;
                    if (i === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                }
                ctx.closePath();
                ctx.fill();

                // Draw final position (current agent position)
                if (trajectory.length > 1) {
                    const finalPos = trajectory[trajectory.length - 1].agent_pos;
                    ctx.fillStyle = '#2196f3';
                    ctx.beginPath();
                    ctx.arc(
                        padding + (finalPos[1] + 0.5) * cellSize,
                        padding + (finalPos[0] + 0.5) * cellSize,
                        cellSize / 4,
                        0,
                        Math.PI * 2
                    );
                    ctx.fill();
                }
            }

            function displayEpisodes(episodes) {
                const html = episodes.map((ep, i) => {
                    const success = ep.decisions && ep.decisions.length > 0;
                    const steps = ep.trajectory.length;
                    const toolQueries = ep.tool_queries ? ep.tool_queries.length : 0;

                    return `
                        <div class="episode-item">
                            <div class="episode-info">
                                <div class="episode-badge ${success ? 'success' : 'failed'}">
                                    ${success ? '✓ OK' : '✗ FAIL'}
                                </div>
                                <div class="episode-details">
                                    <div class="episode-name">Episode ${i}</div>
                                    <div class="episode-meta">Status: ${success ? 'Success' : 'Timeout/Failed'}</div>
                                </div>
                            </div>
                            <div class="episode-stats">
                                <div class="stat">
                                    <div class="stat-label">Steps</div>
                                    <div class="stat-value">${steps}</div>
                                </div>
                                <div class="stat">
                                    <div class="stat-label">Tool Queries</div>
                                    <div class="stat-value">${toolQueries}</div>
                                </div>
                            </div>
                            <button onclick="showEpisodeDecisions(${i})" style="width: 100%; padding: 8px; margin-top: 10px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                View LLM Decisions →
                            </button>
                        </div>
                    `;
                }).join('');

                document.getElementById('episodeDetails').innerHTML = html;
            }

            function showEpisodeDecisions(episodeIndex) {
                const episode = window.lastResultsData.episodes[episodeIndex];
                if (!episode) return;

                const decisions = episode.decisions || [];
                const toolQueries = episode.tool_queries || [];
                const toolQuerySteps = new Set(toolQueries.map(q => q.step));

                let html = `
                    <div style="padding: 20px; background: white; border-radius: 8px; max-height: 600px; overflow-y: auto;">
                        <h3 style="margin-top: 0; color: #333;">Episode ${episodeIndex} - LLM Decision Breakdown</h3>
                        <div style="margin-bottom: 20px; padding: 10px; background: #f0f0f0; border-radius: 4px; font-size: 12px;">
                            <strong>How to read:</strong> Each step shows what the LLM decided to do at that position
                        </div>
                `;

                decisions.slice(0, 50).forEach((decision, stepIdx) => {
                    const isToolUsed = toolQuerySteps.has(stepIdx);
                    const actionNames = ['UP', 'DOWN', 'LEFT', 'RIGHT'];
                    const action = actionNames[decision.action] || 'UNKNOWN';
                    const strategy = decision.strategy || 'unknown';
                    const position = decision.position ? `(${decision.position[0]}, ${decision.position[1]})` : '?';

                    const toolBadge = isToolUsed ?
                        '<span style="display: inline-block; background: rgba(255, 152, 0, 0.3); color: #ff9800; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 8px;">🤖 USED TOOL</span>' :
                        '';

                    const reasoning = decision.reason || decision.action_reasoning?.reasoning || 'Navigation decision';

                    html += `
                        <div style="padding: 12px; margin: 8px 0; background: ${isToolUsed ? 'rgba(255, 152, 0, 0.1)' : '#fafafa'}; border-left: 4px solid ${isToolUsed ? '#ff9800' : '#667eea'}; border-radius: 4px;">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div>
                                    <strong>Step ${stepIdx}:</strong> Move <strong style="color: #667eea;">${action}</strong> from ${position}
                                    ${toolBadge}
                                    <div style="font-size: 12px; color: #666; margin-top: 4px;">
                                        Strategy: <code>${strategy}</code>
                                    </div>
                                    <div style="font-size: 12px; color: #555; margin-top: 4px; font-style: italic;">
                                        "${reasoning}"
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });

                if (decisions.length > 50) {
                    html += `<div style="padding: 10px; color: #999; font-size: 12px; text-align: center;">... and ${decisions.length - 50} more steps</div>`;
                }

                html += '</div>';

                // Show in modal or replace element
                const modal = document.createElement('div');
                modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;';
                modal.innerHTML = `
                    <div style="background: white; border-radius: 8px; max-width: 700px; max-height: 80vh; overflow-y: auto; position: relative; width: 90%;">
                        <button onclick="this.parentElement.parentElement.remove()" style="position: absolute; top: 10px; right: 10px; background: #ff6b6b; color: white; border: none; width: 30px; height: 30px; border-radius: 50%; cursor: pointer; font-size: 16px;">×</button>
                        ${html}
                    </div>
                `;
                document.body.appendChild(modal);
            }

            function loadSampleData() {
                // Load the previously run experiment
                const sampleData = {
                    metrics: {
                        total_episodes: 10,
                        success_rate: 0.4,
                        successful_episodes: 4,
                        failed_episodes: 6,
                        avg_steps: 187.8,
                        min_steps: 21,
                        max_steps: 299,
                        avg_path_optimality: 0.0558,
                        avg_final_distance: 7.5,
                        avg_tool_queries: 96.7,
                        avg_tool_usage_rate: 0.527,
                        avg_tool_accuracy: 0.0,
                        avg_tool_following_rate: 0.016
                    },
                    episodes: Array.from({length: 10}, (_, i) => ({
                        trajectory: Array(i % 2 === 0 ? 22 : 300).fill(null),
                        decisions: Array(i % 2 === 0 ? 20 : 250).fill(null),
                        tool_queries: Array(Math.floor(Math.random() * 150)).fill(null)
                    }))
                };

                displayResults(sampleData);
            }
        </script>
    </body>
    </html>
    """
