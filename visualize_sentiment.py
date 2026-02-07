"""
Movie Sentiment Visualization
Creates charts and an interactive HTML dashboard for sentiment analysis comparison.
"""

import pandas as pd
import json
from pathlib import Path


def load_comparison_data(script_dir: Path) -> tuple[pd.DataFrame, dict]:
    """Load comparison CSV and JSON data."""
    csv_path = script_dir / "movie_comparison.csv"
    json_path = script_dir / "movie_comparison.json"
    
    df = pd.read_csv(csv_path)
    with open(json_path, 'r', encoding='utf-8') as f:
        viz_data = json.load(f)
    
    return df, viz_data


def generate_html_dashboard(df: pd.DataFrame, viz_data: dict, output_path: Path):
    """Generate an interactive HTML dashboard with Chart.js."""
    
    movies = viz_data['movies']
    positive = viz_data['metrics']['positive_pct']
    negative = viz_data['metrics']['negative_pct']
    neutral = viz_data['metrics']['neutral_pct']
    avg_compound = viz_data['metrics']['avg_compound']
    total_comments = viz_data['metrics']['total_comments']
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Trailer Sentiment Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e8e8e8;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: #a0a0a0;
            font-size: 1.1rem;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        .card h2 {{
            font-size: 1.2rem;
            margin-bottom: 1rem;
            color: #00d4ff;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
        }}
        
        .stat-card h3 {{
            font-size: 1rem;
            color: #888;
            margin-bottom: 0.5rem;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-movie {{
            font-size: 0.9rem;
            color: #a0a0a0;
            margin-top: 0.3rem;
        }}
        
        .ranking-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        
        .ranking-table th,
        .ranking-table td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .ranking-table th {{
            color: #00d4ff;
            font-weight: 600;
        }}
        
        .ranking-table tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .medal {{
            font-size: 1.5rem;
        }}
        
        .bar {{
            height: 8px;
            border-radius: 4px;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        }}
        
        .sentiment-bars {{
            display: flex;
            gap: 4px;
            height: 24px;
            border-radius: 12px;
            overflow: hidden;
        }}
        
        .sentiment-bars .positive {{ background: #22c55e; }}
        .sentiment-bars .neutral {{ background: #94a3b8; }}
        .sentiment-bars .negative {{ background: #ef4444; }}
        
        footer {{
            text-align: center;
            margin-top: 3rem;
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎬 Movie Trailer Sentiment Analysis</h1>
            <p class="subtitle">Comparing audience reactions from YouTube comments</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>🌟 Most Positive</h3>
                <div class="stat-value">{df.loc[df['positive_pct'].idxmax(), 'positive_pct']}%</div>
                <div class="stat-movie">{df.loc[df['positive_pct'].idxmax(), 'movie']}</div>
            </div>
            <div class="stat-card">
                <h3>📊 Highest Score</h3>
                <div class="stat-value">{df.loc[df['avg_compound'].idxmax(), 'avg_compound']}</div>
                <div class="stat-movie">{df.loc[df['avg_compound'].idxmax(), 'movie']}</div>
            </div>
            <div class="stat-card">
                <h3>🔥 Most Engagement</h3>
                <div class="stat-value">{df['total_comments'].sum():,}</div>
                <div class="stat-movie">Total comments analyzed</div>
            </div>
            <div class="stat-card">
                <h3>💔 Most Controversial</h3>
                <div class="stat-value">{df.loc[df['negative_pct'].idxmax(), 'negative_pct']}%</div>
                <div class="stat-movie">{df.loc[df['negative_pct'].idxmax(), 'movie']}</div>
            </div>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h2>📊 Sentiment Distribution</h2>
                <div class="chart-container">
                    <canvas id="stackedBarChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>📈 Average Compound Score</h2>
                <div class="chart-container">
                    <canvas id="compoundChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Positive vs Negative</h2>
                <div class="chart-container">
                    <canvas id="polarChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>💬 Comment Volume</h2>
                <div class="chart-container">
                    <canvas id="doughnutChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🏆 Complete Rankings</h2>
            <table class="ranking-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Movie</th>
                        <th>Score</th>
                        <th>Sentiment Distribution</th>
                        <th>Comments</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td><span class="medal">{["🥇", "🥈", "🥉", "4️⃣"][i]}</span></td>
                        <td>{row['movie']}</td>
                        <td>{row['avg_compound']}</td>
                        <td>
                            <div class="sentiment-bars">
                                <div class="positive" style="width: {row['positive_pct']}%"></div>
                                <div class="neutral" style="width: {row['neutral_pct']}%"></div>
                                <div class="negative" style="width: {row['negative_pct']}%"></div>
                            </div>
                        </td>
                        <td>{row['total_comments']}</td>
                    </tr>
                    ''' for i, (_, row) in enumerate(df.iterrows())])}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Generated with VADER Sentiment Analysis | Data from YouTube Comments</p>
        </footer>
    </div>
    
    <script>
        const movies = {json.dumps(movies)};
        const positive = {json.dumps(positive)};
        const negative = {json.dumps(negative)};
        const neutral = {json.dumps(neutral)};
        const avgCompound = {json.dumps(avg_compound)};
        const totalComments = {json.dumps(total_comments)};
        
        // Stacked Bar Chart - Sentiment Distribution
        new Chart(document.getElementById('stackedBarChart'), {{
            type: 'bar',
            data: {{
                labels: movies,
                datasets: [
                    {{
                        label: 'Positive',
                        data: positive,
                        backgroundColor: 'rgba(34, 197, 94, 0.8)',
                        borderRadius: 4
                    }},
                    {{
                        label: 'Neutral',
                        data: neutral,
                        backgroundColor: 'rgba(148, 163, 184, 0.8)',
                        borderRadius: 4
                    }},
                    {{
                        label: 'Negative',
                        data: negative,
                        backgroundColor: 'rgba(239, 68, 68, 0.8)',
                        borderRadius: 4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        labels: {{ color: '#e8e8e8' }}
                    }}
                }},
                scales: {{
                    x: {{
                        stacked: true,
                        ticks: {{ color: '#a0a0a0' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    y: {{
                        stacked: true,
                        ticks: {{ color: '#a0a0a0' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }}
                }}
            }}
        }});
        
        // Compound Score Chart
        new Chart(document.getElementById('compoundChart'), {{
            type: 'bar',
            data: {{
                labels: movies,
                datasets: [{{
                    label: 'Avg Compound Score',
                    data: avgCompound,
                    backgroundColor: avgCompound.map(v => 
                        v > 0.2 ? 'rgba(34, 197, 94, 0.8)' : 
                        v > 0.1 ? 'rgba(250, 204, 21, 0.8)' : 
                        'rgba(239, 68, 68, 0.8)'
                    ),
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{
                        ticks: {{ color: '#a0a0a0' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    y: {{
                        ticks: {{ color: '#e8e8e8' }},
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
        
        // Polar Chart
        new Chart(document.getElementById('polarChart'), {{
            type: 'radar',
            data: {{
                labels: movies,
                datasets: [
                    {{
                        label: 'Positive %',
                        data: positive,
                        backgroundColor: 'rgba(34, 197, 94, 0.2)',
                        borderColor: 'rgba(34, 197, 94, 1)',
                        pointBackgroundColor: 'rgba(34, 197, 94, 1)'
                    }},
                    {{
                        label: 'Negative %',
                        data: negative,
                        backgroundColor: 'rgba(239, 68, 68, 0.2)',
                        borderColor: 'rgba(239, 68, 68, 1)',
                        pointBackgroundColor: 'rgba(239, 68, 68, 1)'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        labels: {{ color: '#e8e8e8' }}
                    }}
                }},
                scales: {{
                    r: {{
                        ticks: {{ color: '#a0a0a0', backdropColor: 'transparent' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }},
                        pointLabels: {{ color: '#e8e8e8' }}
                    }}
                }}
            }}
        }});
        
        // Doughnut Chart - Comment Volume
        new Chart(document.getElementById('doughnutChart'), {{
            type: 'doughnut',
            data: {{
                labels: movies,
                datasets: [{{
                    data: totalComments,
                    backgroundColor: [
                        'rgba(0, 212, 255, 0.8)',
                        'rgba(123, 44, 191, 0.8)',
                        'rgba(255, 107, 107, 0.8)',
                        'rgba(34, 197, 94, 0.8)'
                    ],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{ color: '#e8e8e8' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def main():
    script_dir = Path(__file__).parent
    
    print("📂 Loading comparison data...")
    
    try:
        df, viz_data = load_comparison_data(script_dir)
    except FileNotFoundError:
        print("❌ Comparison files not found! Run compare_sentiment.py first.")
        return
    
    print(f"✅ Loaded data for {len(df)} movies")
    
    # Generate HTML Dashboard
    html_path = script_dir / "sentiment_dashboard.html"
    generate_html_dashboard(df, viz_data, html_path)
    print(f"\n🎨 HTML Dashboard created: {html_path}")
    print(f"\n🌐 Open in browser: file://{html_path}")


if __name__ == "__main__":
    main()
