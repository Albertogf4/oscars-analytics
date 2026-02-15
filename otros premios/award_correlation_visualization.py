"""
Visualization Dashboard: BAFTA / Golden Globe → Oscar Correlation
=================================================================
Generates an interactive HTML dashboard with charts showing the predictive
power of BAFTA and Golden Globe wins for the Oscar Best Picture award.
"""

import json
import pandas as pd

# Load analysis results
with open("award_correlation_data.json") as f:
    data = json.load(f)

summary = data["summary"]
scenarios = data["scenarios"]
decades = data["decades"]
recent = data["recent_winners"]
gg_drama = data.get("gg_drama_rate", {})
gg_comedy = data.get("gg_comedy_rate", {})

# ─────────────────────────────────────────────────────
# Build HTML Dashboard
# ─────────────────────────────────────────────────────

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Award Correlation Dashboard – BAFTA & Golden Globes → Oscars</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {
    --gold: #D4AF37;
    --oscar-gold: #C5A028;
    --bafta-bronze: #CD7F32;
    --gg-blue: #1B3A5C;
    --bg: #0F0F0F;
    --card-bg: #1A1A2E;
    --text: #E8E8E8;
    --muted: #999;
    --accent-green: #4CAF50;
    --accent-red: #E74C3C;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }
  .header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 40px 20px 30px;
    text-align: center;
    border-bottom: 3px solid var(--gold);
  }
  .header h1 {
    font-size: 2.2rem;
    color: var(--gold);
    letter-spacing: 1px;
    margin-bottom: 8px;
  }
  .header p { color: var(--muted); font-size: 1rem; }
  .container { max-width: 1300px; margin: 0 auto; padding: 30px 20px; }

  /* KPI cards */
  .kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
    margin-bottom: 35px;
  }
  .kpi-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    border: 1px solid #2a2a4a;
    transition: transform .2s;
  }
  .kpi-card:hover { transform: translateY(-3px); }
  .kpi-label { font-size: .85rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
  .kpi-value { font-size: 2.4rem; font-weight: 700; }
  .kpi-sub { font-size: .8rem; color: var(--muted); margin-top: 6px; }
  .gold { color: var(--gold); }
  .bronze { color: var(--bafta-bronze); }
  .blue { color: #5B9BD5; }
  .green { color: var(--accent-green); }

  /* Chart containers */
  .chart-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 25px;
    margin-bottom: 35px;
  }
  .chart-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #2a2a4a;
  }
  .chart-card h3 { color: var(--gold); font-size: 1.1rem; margin-bottom: 15px; }
  .chart-card canvas { width: 100% !important; }

  /* Full-width chart */
  .full-width { grid-column: 1 / -1; }

  /* Table */
  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: .9rem; }
  th { text-align: left; padding: 10px 12px; color: var(--gold); border-bottom: 2px solid #333; }
  td { padding: 8px 12px; border-bottom: 1px solid #222; }
  tr:hover td { background: rgba(212, 175, 55, .05); }
  .badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: .8rem; font-weight: 600;
  }
  .badge-yes { background: rgba(76, 175, 80, .2); color: #4CAF50; }
  .badge-no  { background: rgba(231, 76, 60, .15); color: #E74C3C; }

  /* Statistical section */
  .stat-box {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #2a2a4a;
    margin-bottom: 25px;
  }
  .stat-box h3 { color: var(--gold); margin-bottom: 15px; }
  .stat-row { display: flex; gap: 30px; flex-wrap: wrap; }
  .stat-item {
    flex: 1; min-width: 200px;
    background: rgba(255,255,255,.03);
    border-radius: 8px;
    padding: 16px;
  }
  .stat-item .label { font-size: .8rem; color: var(--muted); margin-bottom: 4px; }
  .stat-item .value { font-size: 1.3rem; font-weight: 700; }

  .insight-box {
    background: linear-gradient(135deg, rgba(212,175,55,.08), rgba(212,175,55,.02));
    border-left: 4px solid var(--gold);
    border-radius: 0 12px 12px 0;
    padding: 20px 24px;
    margin: 25px 0;
    font-size: .95rem;
    line-height: 1.6;
  }
  .insight-box strong { color: var(--gold); }

  @media (max-width: 600px) {
    .chart-grid { grid-template-columns: 1fr; }
    .header h1 { font-size: 1.5rem; }
    .kpi-value { font-size: 1.8rem; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>🏆 Award Correlation Analysis</h1>
  <p>Do BAFTA and Golden Globe wins predict the Oscar for Best Picture?</p>
</div>

<div class="container">
"""

# KPI Cards
gg = summary["gg_to_oscar"]
ba = summary["bafta_to_oscar"]

html += f"""
  <div class="kpi-row">
    <div class="kpi-card">
      <div class="kpi-label">GG → Oscar Win Rate</div>
      <div class="kpi-value gold">{gg['rate']}%</div>
      <div class="kpi-sub">{gg['also_won_oscar']} of {gg['total_winners']} GG winners also won Oscar</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">BAFTA → Oscar Win Rate</div>
      <div class="kpi-value bronze">{ba['rate']}%</div>
      <div class="kpi-sub">{ba['also_won_oscar']} of {ba['total_winners']} BAFTA winners also won Oscar</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">GG Odds Ratio</div>
      <div class="kpi-value blue">{gg['odds_ratio']}x</div>
      <div class="kpi-sub">Times more likely to win Oscar after GG win</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">BAFTA Odds Ratio</div>
      <div class="kpi-value blue">{ba['odds_ratio']}x</div>
      <div class="kpi-sub">Times more likely to win Oscar after BAFTA win</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Both Awards → Oscar</div>
      <div class="kpi-value green">{scenarios['Won both BAFTA and GG']['rate']}%</div>
      <div class="kpi-sub">{scenarios['Won both BAFTA and GG']['wins']} of {scenarios['Won both BAFTA and GG']['n']} that won both</div>
    </div>
  </div>
"""

# Insight box
html += f"""
  <div class="insight-box">
    <strong>Key Finding:</strong> Films that win <strong>both</strong> the BAFTA Best Film and a Golden Globe Best Picture 
    have a <strong>{scenarios['Won both BAFTA and GG']['rate']}%</strong> chance of winning the Oscar for Best Picture, 
    compared to only <strong>{scenarios['Won neither BAFTA nor GG']['rate']}%</strong> for films that win neither.
    The Golden Globe (φ&nbsp;=&nbsp;{gg['phi']}) and BAFTA (φ&nbsp;=&nbsp;{ba['phi']}) both show 
    {'strong' if max(gg['phi'], ba['phi']) > 0.3 else 'moderate'} statistical correlation with Oscar outcomes
    (p&nbsp;&lt;&nbsp;0.001 for both).
  </div>
"""

# Charts section
html += """
  <div class="chart-grid">
    <!-- Scenario comparison bar chart -->
    <div class="chart-card">
      <h3>Oscar Win Rate by Prior Award Status</h3>
      <canvas id="scenarioChart"></canvas>
    </div>

    <!-- GG Drama vs Comedy -->
    <div class="chart-card">
      <h3>Golden Globe Breakdown: Drama vs. Musical/Comedy</h3>
      <canvas id="ggBreakdownChart"></canvas>
    </div>

    <!-- Decade-by-decade trends -->
    <div class="chart-card full-width">
      <h3>Predictive Power Over the Decades</h3>
      <canvas id="decadeChart"></canvas>
    </div>
  </div>
"""

# Statistical details
html += f"""
  <div class="stat-box">
    <h3>Statistical Tests</h3>
    <div class="stat-row">
      <div class="stat-item">
        <div class="label">Chi-squared (GG → Oscar)</div>
        <div class="value gold">χ² = {gg['chi2']}</div>
        <div class="label">p = {gg['p_value']}</div>
      </div>
      <div class="stat-item">
        <div class="label">Chi-squared (BAFTA → Oscar)</div>
        <div class="value bronze">χ² = {ba['chi2']}</div>
        <div class="label">p = {ba['p_value']}</div>
      </div>
      <div class="stat-item">
        <div class="label">Phi Coefficient (GG)</div>
        <div class="value gold">φ = {gg['phi']}</div>
        <div class="label">{'Strong' if gg['phi'] > 0.3 else 'Moderate'} correlation</div>
      </div>
      <div class="stat-item">
        <div class="label">Phi Coefficient (BAFTA)</div>
        <div class="value bronze">φ = {ba['phi']}</div>
        <div class="label">{'Strong' if ba['phi'] > 0.3 else 'Moderate'} correlation</div>
      </div>
    </div>
  </div>
"""

# Recent winners table
html += """
  <div class="chart-card" style="margin-bottom: 30px;">
    <h3>Recent Oscar Best Picture Winners – Award Alignment</h3>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Year</th><th>Oscar Best Picture</th><th>Won GG?</th><th>Won BAFTA?</th></tr></thead>
        <tbody>
"""
for r in sorted(recent, key=lambda x: x["year"], reverse=True):
    gg_badge = '<span class="badge badge-yes">✓ Yes</span>' if r["won_gg"] else '<span class="badge badge-no">✗ No</span>'
    ba_badge = '<span class="badge badge-yes">✓ Yes</span>' if r["won_bafta"] else '<span class="badge badge-no">✗ No</span>'
    html += f"<tr><td>{int(float(r['year']))}</td><td>{r['film']}</td><td>{gg_badge}</td><td>{ba_badge}</td></tr>\n"

html += """
        </tbody>
      </table>
    </div>
  </div>
"""

# JavaScript for charts
scenario_labels = list(scenarios.keys())
scenario_rates = [scenarios[k]["rate"] for k in scenario_labels]
scenario_counts = [f"{scenarios[k]['wins']}/{scenarios[k]['n']}" for k in scenario_labels]
scenario_colors = ["#555", "#D4AF37", "#CD7F32", "#4CAF50"]

decade_labels = [d["decade"] for d in decades]
decade_gg = [d["gg_to_oscar_rate"] for d in decades]
decade_bafta = [d["bafta_to_oscar_rate"] for d in decades]
decade_both = [d["both_to_oscar_rate"] for d in decades]

gg_drama_data = gg_drama if gg_drama else {"total": 0, "won_oscar": 0, "rate": 0}
gg_comedy_data = gg_comedy if gg_comedy else {"total": 0, "won_oscar": 0, "rate": 0}

html += f"""
<script>
Chart.defaults.color = '#999';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';

// 1. Scenario comparison
new Chart(document.getElementById('scenarioChart'), {{
  type: 'bar',
  data: {{
    labels: {json.dumps(scenario_labels)},
    datasets: [{{
      label: 'Oscar Win Rate (%)',
      data: {json.dumps(scenario_rates)},
      backgroundColor: {json.dumps(scenario_colors)},
      borderRadius: 6,
      barPercentage: 0.65
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          afterLabel: function(ctx) {{
            var counts = {json.dumps(scenario_counts)};
            return counts[ctx.dataIndex] + ' films';
          }}
        }}
      }}
    }},
    scales: {{
      y: {{
        beginAtZero: true,
        max: 100,
        ticks: {{ callback: v => v + '%' }}
      }},
      x: {{
        ticks: {{ maxRotation: 25, font: {{ size: 11 }} }}
      }}
    }}
  }}
}});

// 2. GG Drama vs Comedy
new Chart(document.getElementById('ggBreakdownChart'), {{
  type: 'bar',
  data: {{
    labels: ['Drama', 'Musical / Comedy'],
    datasets: [{{
      label: 'Oscar Win Rate (%)',
      data: [{gg_drama_data['rate'] if gg_drama_data else 0}, {gg_comedy_data['rate'] if gg_comedy_data else 0}],
      backgroundColor: ['#D4AF37', '#5B9BD5'],
      borderRadius: 6,
      barPercentage: 0.5
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          afterLabel: function(ctx) {{
            var info = [
              '{gg_drama_data["won_oscar"] if gg_drama_data else 0}/{gg_drama_data["total"] if gg_drama_data else 0} films',
              '{gg_comedy_data["won_oscar"] if gg_comedy_data else 0}/{gg_comedy_data["total"] if gg_comedy_data else 0} films'
            ];
            return info[ctx.dataIndex];
          }}
        }}
      }}
    }},
    scales: {{
      y: {{ beginAtZero: true, max: 100, ticks: {{ callback: v => v + '%' }} }}
    }}
  }}
}});

// 3. Decade trends
new Chart(document.getElementById('decadeChart'), {{
  type: 'line',
  data: {{
    labels: {json.dumps(decade_labels)},
    datasets: [
      {{
        label: 'GG Winner → Oscar Win %',
        data: {json.dumps(decade_gg)},
        borderColor: '#D4AF37',
        backgroundColor: 'rgba(212,175,55,0.1)',
        fill: false,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 8
      }},
      {{
        label: 'BAFTA Winner → Oscar Win %',
        data: {json.dumps(decade_bafta)},
        borderColor: '#CD7F32',
        backgroundColor: 'rgba(205,127,50,0.1)',
        fill: false,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 8
      }},
      {{
        label: 'Both Winners → Oscar Win %',
        data: {json.dumps(decade_both)},
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76,175,80,0.1)',
        fill: false,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 8,
        borderDash: [5,5]
      }}
    ]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'top' }}
    }},
    scales: {{
      y: {{ beginAtZero: true, max: 100, ticks: {{ callback: v => v + '%' }} }}
    }}
  }}
}});
</script>

<div style="text-align:center; padding:30px 0 20px; color:var(--muted); font-size:.8rem;">
  Award Correlation Analysis Dashboard · Data from BAFTA, Golden Globe & Oscar historical records
</div>

</div>
</body>
</html>
"""

with open("award_correlation_dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✓ Dashboard generated: award_correlation_dashboard.html")
