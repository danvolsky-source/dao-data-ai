'use client';

export default function Home() {
  return (
    <div dangerouslySetInnerHTML={{ __html: `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arbitrum DAO Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
        .header p { color: #666; font-size: 1.1em; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
        }
        .chart-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .chart-title {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 20px;
            font-weight: 600;
        }
        .table-container {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-top: 20px;
            overflow-x: auto;
        }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #667eea; color: white; font-weight: 600; }
        tr:hover { background: #f5f5f5; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ Arbitrum DAO Analytics</h1>
            <p>Real-time governance data visualization and analysis</p>
        </div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Proposals</div>
                <div class="stat-value" id="totalProposals">Loading...</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Proposals</div>
                <div class="stat-value" id="activeProposals">Loading...</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Votes</div>
                <div class="stat-value" id="totalVotes">Loading...</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Delegates</div>
                <div class="stat-value" id="totalDelegates">Loading...</div>
            </div>
        </div>
        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-title">📊 Proposal Status Distribution</div>
                <canvas id="proposalStatusChart"></canvas>
            </div>
            <div class="chart-card">
                <div class="chart-title">📈 Voting Activity Timeline</div>
                <canvas id="votingTimelineChart"></canvas>
            </div>
        </div>
        <div class="table-container">
            <div class="chart-title">🎯 Top 10 Recent Proposals</div>
            <table id="proposalsTable">
                <thead><tr><th>Title</th><th>Status</th><th>Votes</th><th>Created</th></tr></thead>
                <tbody id="proposalsTableBody">
                    <tr><td colspan="4" style="text-align: center;">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    <script>
        const SUPABASE_URL = 'https://fsvlkshplbfivwmdljqh.supabase.co';
        const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZzdmxrc2hwbGJmaXZ3bWRsanFoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc5NDM5OTgsImV4cCI6MjA3MzUxOTk5OH0.jgjEW3h1qh1kI1oYyRNoCNcGm7SsD8vtsmoFIVqgGyA';
        const { createClient } = supabase;
        const supabaseClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        async function loadDashboardData() {
            try {
                const { data: proposals } = await supabaseClient.from('proposals').select('*').order('created_at', { ascending: false });
                const { data: votes } = await supabaseClient.from('votes').select('*');
                const { data: delegates } = await supabaseClient.from('delegates').select('*');
                document.getElementById('totalProposals').textContent = proposals?.length || 0;
                document.getElementById('activeProposals').textContent = proposals?.filter(p => p.status === 'active').length || 0;
                document.getElementById('totalVotes').textContent = votes?.length || 0;
                document.getElementById('totalDelegates').textContent = delegates?.length || 0;
                createProposalStatusChart(proposals);
                createVotingTimelineChart(proposals);
                populateProposalsTable(proposals?.slice(0, 10) || []);
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }
        function createProposalStatusChart(proposals) {
            const statusCounts = {};
            proposals?.forEach(p => { statusCounts[p.status] = (statusCounts[p.status] || 0) + 1; });
            const ctx = document.getElementById('proposalStatusChart');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(statusCounts),
                    datasets: [{ data: Object.values(statusCounts), backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0'] }]
                },
                options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
            });
        }
        function createVotingTimelineChart(proposals) {
            const monthCounts = {};
            proposals?.forEach(p => {
                const month = new Date(p.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
                monthCounts[month] = (monthCounts[month] || 0) + 1;
            });
            const ctx = document.getElementById('votingTimelineChart');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Object.keys(monthCounts),
                    datasets: [{ label: 'Proposals per Month', data: Object.values(monthCounts), borderColor: '#667eea', backgroundColor: 'rgba(102, 126, 234, 0.1)', tension: 0.4, fill: true }]
                },
                options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
            });
        }
        function populateProposalsTable(proposals) {
            const tbody = document.getElementById('proposalsTableBody');
            tbody.innerHTML = proposals.map(p => \`
                <tr>
                    <td>\${p.title.substring(0, 50)}\${p.title.length > 50 ? '...' : ''}</td>
                    <td><span style="background: #667eea; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.85em;">\${p.status}</span></td>
                    <td>\${p.votes || 0}</td>
                    <td>\${new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
            \`).join('');
        }
        loadDashboardData();
        setInterval(loadDashboardData, 30000);
    </script>
</body>
</html>
    `}} />
  );
}
