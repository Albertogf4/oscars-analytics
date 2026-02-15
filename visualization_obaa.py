# visualization_obaa.py
"""
OBaA-focused HTML Dashboard (no Python plotly dependency)
- Reads campaign_validation_out/campaign_prioritization.csv
- Highlights "One Battle After Another" (substring match)
- Charts:
  1) Intent Rate ranking vs other movies (YouTube/Reddit)
  2) Intent vs Sentiment scatter (bubble size = n comments)
  3) KPI comparison: OBaA vs cohort average (per source)
  4) Drivers (perf/craft/family/music) + Friction (toxicity/confusion)
  5) Detailed table with ranks and deltas
"""

import json
from pathlib import Path
import pandas as pd


FOCUS_MOVIE_CONTAINS = "One Battle After Another"  # substring match
DATA_DIR = "campaign_validation_out"
OUTPUT_HTML = "campaign_dashboard_obaa.html"


def _pick_focus_movie(df: pd.DataFrame) -> str:
    # prefer exact contains match, otherwise fallback to first row
    matches = df[df["movie"].astype(str).str.contains(FOCUS_MOVIE_CONTAINS, case=False, na=False)]
    if not matches.empty:
        # choose the most-commented one (common if you have trailer + teaser variants)
        return matches.sort_values("n", ascending=False).iloc[0]["movie"]
    return df.iloc[0]["movie"]


def _add_ranks_and_deltas(df: pd.DataFrame, focus_movie: str) -> pd.DataFrame:
    out = df.copy()
    out["is_focus"] = out["movie"].astype(str).str.lower().eq(str(focus_movie).lower())

    # rank within each source by intent_rate descending (1 = best)
    out["intent_rank"] = (
        out.sort_values(["source", "intent_rate"], ascending=[True, False])
           .groupby("source")
           .cumcount() + 1
    )

    # deltas vs cohort (excluding focus)
    rows = []
    for src, g in out.groupby("source"):
        focus = g[g["is_focus"]]
        others = g[~g["is_focus"]]
        if focus.empty:
            continue
        f = focus.iloc[0].to_dict()

        def mean_or_nan(col):
            return float(others[col].mean()) if len(others) else float("nan")

        # compute deltas for key KPIs
        for col in [
            "avg_compound", "pos_rate", "neg_rate", "intent_rate",
            "perf_rate", "craft_rate", "family_rate", "music_rate",
            "confusion_rate", "toxicity_rate",
            "score_reduce_confusion", "score_performance_spotlight", "score_craft_event"
        ]:
            f[f"delta_{col}"] = float(f[col]) - mean_or_nan(col)

        f["cohort_intent_mean"] = mean_or_nan("intent_rate")
        f["cohort_intent_median"] = float(others["intent_rate"].median()) if len(others) else float("nan")
        f["cohort_n_movies"] = int(len(g))
        rows.append(f)

    focus_summary = pd.DataFrame(rows)
    return out, focus_summary


def generate_dashboard():
    p = Path(DATA_DIR)
    prio_path = p / "campaign_prioritization.csv"
    if not prio_path.exists():
        raise FileNotFoundError(f"Missing {prio_path}. Run compatible.py first.")

    prio = pd.read_csv(prio_path)

    # Basic cleaning (ensure numeric)
    numeric_cols = [
        "n","avg_compound","pos_rate","neg_rate","intent_rate",
        "family_rate","craft_rate","music_rate","perf_rate",
        "confusion_rate","toxicity_rate",
        "score_heart_family","score_craft_event","score_music_listening",
        "score_performance_spotlight","score_reduce_confusion"
    ]
    for c in numeric_cols:
        if c in prio.columns:
            prio[c] = pd.to_numeric(prio[c], errors="coerce")

    focus_movie = _pick_focus_movie(prio)
    prio2, focus_summary = _add_ranks_and_deltas(prio, focus_movie)

    # Split datasets for JS
    data_all = prio2.to_dict("records")
    data_y = prio2[prio2["source"] == "youtube"].sort_values("intent_rate", ascending=False).to_dict("records")
    data_r = prio2[prio2["source"] == "reddit"].sort_values("intent_rate", ascending=False).to_dict("records")
    focus_rows = focus_summary.to_dict("records")

    # KPI set for the "OBaA vs Cohort Avg" chart
    kpi_groups = [
        {"key": "intent_rate", "label": "Intent (%)"},
        {"key": "avg_compound", "label": "Avg Sentiment (compound)"},
        {"key": "pos_rate", "label": "Positive (%)"},
        {"key": "neg_rate", "label": "Negative (%)"},
        {"key": "perf_rate", "label": "Performance Buzz (%)"},
        {"key": "craft_rate", "label": "Craft Buzz (%)"},
        {"key": "family_rate", "label": "Family/Heart (%)"},
        {"key": "music_rate", "label": "Music/Score (%)"},
        {"key": "toxicity_rate", "label": "Toxicity (%)"},
        {"key": "confusion_rate", "label": "Confusion (%)"},
    ]

    campaign_labels = {
        "score_heart_family": "Heart & Family",
        "score_craft_event": "Craft as Event",
        "score_music_listening": "Music/Listening",
        "score_performance_spotlight": "Performance",
        "score_reduce_confusion": "Reduce Confusion"
    }
    campaigns = list(campaign_labels.keys())

    # Build HTML
    html = f"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>OBaA Campaign Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    body {{
      font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
      margin: 0;
      background: #f5f7fa;
      color: #2c3e50;
    }}
    .wrap {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px;
    }}
    .header {{
      background: linear-gradient(135deg, #d4af37 0%, #f4d03f 100%);
      border-radius: 18px;
      padding: 22px 22px;
      box-shadow: 0 4px 12px rgba(212,175,55,.25);
    }}
    .title {{
      font-size: 22px;
      font-weight: 800;
      margin: 0 0 8px 0;
      color: #1a1a1a;
    }}
    .subtitle {{
      margin: 0;
      line-height: 1.35;
      font-size: 14px;
      color: #2c3e50;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 16px;
      margin-top: 16px;
    }}
    .card {{
      background: #ffffff;
      border: 1px solid #e0e6ed;
      border-radius: 18px;
      padding: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,.08);
    }}
    .card h3 {{
      margin: 0 0 10px 0;
      font-size: 14px;
      letter-spacing: .2px;
      color: #d4af37;
      font-weight: 700;
    }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 12px;
    }}
    .kpi {{
      background: #f8f9fa;
      border: 1px solid #e0e6ed;
      border-radius: 14px;
      padding: 12px;
    }}
    .kpi .name {{
      font-size: 12px;
      color: #6c757d;
      margin-bottom: 6px;
    }}
    .kpi .val {{
      font-size: 22px;
      font-weight: 800;
      margin-bottom: 4px;
      color: #2c3e50;
    }}
    .kpi .delta {{
      font-size: 12px;
    }}
    .delta.pos {{ color: #28a745; }}
    .delta.neg {{ color: #dc3545; }}
    .delta.neu {{ color: #ffc107; }}
    .chart {{
      width: 100%;
      height: 440px;
    }}
    .span-12 {{ grid-column: span 12; }}
    .span-8  {{ grid-column: span 8; }}
    .span-6  {{ grid-column: span 6; }}
    .span-4  {{ grid-column: span 4; }}
    .span-3  {{ grid-column: span 3; }}
    .note {{
      font-size: 13px;
      line-height: 1.35;
      color: #6c757d;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      overflow: hidden;
      border-radius: 14px;
    }}
    th, td {{
      padding: 10px 10px;
      border-bottom: 1px solid #e0e6ed;
      text-align: left;
      font-size: 12.5px;
    }}
    th {{
      background: #f8f9fa;
      font-weight: 700;
      color: #d4af37;
    }}
    tr:hover td {{
      background: #f8f9fa;
    }}
    .pill {{
      display:inline-block;
      padding:2px 8px;
      border-radius:999px;
      font-size:12px;
      background: #e0e6ed;
      border: 1px solid #d0d7de;
      color: #2c3e50;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <p class="title">🎬 OBaA Dashboard — "Intent is low" + KPI snapshot</p>
      <p class="subtitle">
        Película foco: <b>{focus_movie}</b> — acción/thriller con comedia negra y "hook" padre-hija; craft fuerte (VistaVision / movimiento) y conversación intensa sobre cast/craft.
        <br/>Objetivo del dashboard: evidenciar que <b>Intent (%)</b> es bajo vs cohort y ver qué drivers (Performance/Craft) no se están convirtiendo en intención.
      </p>
    </div>

    <div class="grid">
      <div class="card span-12">
        <h3>📌 KPI Cards (OBaA vs media del resto de películas en la misma fuente)</h3>
        <div id="kpiCards" class="kpis"></div>
      </div>

      <div class="card span-6">
        <h3>Intent ranking — YouTube (OBaA resaltada)</h3>
        <div id="intentBarYT" class="chart"></div>
      </div>

      <div class="card span-6">
        <h3>Intent ranking — Reddit (OBaA resaltada)</h3>
        <div id="intentBarRD" class="chart"></div>
      </div>

      <div class="card span-12">
        <h3>🧭 Intent vs Sentiment (bubble size = n comentarios)</h3>
        <div id="intentVsSent" class="chart"></div>
      </div>

      <div class="card span-6">
        <h3>OBaA vs Cohort Avg — KPI comparison (por fuente)</h3>
        <div id="kpiCompare" class="chart"></div>
      </div>

      <div class="card span-6">
        <h3>Drivers & Friction</h3>
        <div id="driversFriction" class="chart"></div>
      </div>

      <div class="card span-12">
        <h3>🏁 Campaign scores (OBaA) — radar por fuente</h3>
        <div id="campaignRadar" class="chart"></div>
      </div>

      <div class="card span-12">
        <h3>📋 Tabla detallada</h3>
        <div id="dataTable"></div>
      </div>
    </div>
  </div>

<script>
  const ALL = {json.dumps(data_all, ensure_ascii=False)};
  const YT  = {json.dumps(data_y, ensure_ascii=False)};
  const RD  = {json.dumps(data_r, ensure_ascii=False)};
  const FOCUS_ROWS = {json.dumps(focus_rows, ensure_ascii=False)};
  const KPI_GROUPS = {json.dumps(kpi_groups, ensure_ascii=False)};
  const CAMPAIGNS = {json.dumps(campaigns, ensure_ascii=False)};
  const CAMPAIGN_LABELS = {json.dumps(campaign_labels, ensure_ascii=False)};

  const plotlyLayout = {{
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: '#ffffff',
    font: {{ color: '#2c3e50' }}
  }};

  function fmt(x, d=2) {{
    if (x === null || x === undefined || Number.isNaN(x)) return '—';
    return Number(x).toFixed(d);
  }}

  function deltaClass(v) {{
    if (v === null || v === undefined || Number.isNaN(v)) return 'neu';
    if (v > 0) return 'pos';
    if (v < 0) return 'neg';
    return 'neu';
  }}

  // ---------- KPI Cards (one block per source) ----------
  const kpiRoot = document.getElementById('kpiCards');

  if (!FOCUS_ROWS.length) {{
    kpiRoot.innerHTML = '<div class="note">⚠️ No se encontró la peli foco en los datos.</div>';
  }} else {{
    FOCUS_ROWS.forEach(r => {{
      const wrap = document.createElement('div');
      wrap.className = 'kpi';
      wrap.innerHTML = `
        <div class="name"><span class="pill">${{r.source.toUpperCase()}}</span> · n=${{Number(r.n).toLocaleString()}} · intent rank #${{r.intent_rank}}/${{r.cohort_n_movies}}</div>
        <div class="val">Intent ${{fmt(r.intent_rate,2)}}%</div>
        <div class="delta ${{deltaClass(r.delta_intent_rate)}}">Δ intent vs cohort avg: ${{fmt(r.delta_intent_rate,2)}} pts (cohort mean: ${{fmt(r.cohort_intent_mean,2)}}%)</div>
        <div class="delta ${{deltaClass(r.delta_avg_compound)}}">Δ sentiment(compound): ${{fmt(r.delta_avg_compound,3)}}</div>
        <div class="delta ${{deltaClass(-r.delta_toxicity_rate)}}">Toxicity: ${{fmt(r.toxicity_rate,2)}}% (Δ: ${{fmt(r.delta_toxicity_rate,2)}} pts)</div>
      `;
      kpiRoot.appendChild(wrap);
    }});
  }}

  // ---------- Intent Bar Charts ----------
  function intentBar(divId, data) {{
    if (!data || !data.length) {{
      document.getElementById(divId).innerHTML = '<div class="note">No data.</div>';
      return;
    }}
    const x = data.map(d => d.movie);
    const y = data.map(d => d.intent_rate);
    const colors = data.map(d => d.is_focus ? '#d4af37' : 'rgba(108,117,125,.65)');

    const trace = {{
      type: 'bar',
      x, y,
      marker: {{ color: colors }},
      hovertemplate: '<b>%{{x}}</b><br>Intent: %{{y:.2f}}%<extra></extra>'
    }};

    Plotly.newPlot(divId, [trace], {{
      ...plotlyLayout,
      margin: {{l: 50, r: 10, t: 10, b: 140}},
      xaxis: {{ tickangle: -35 }},
      yaxis: {{ title: 'Intent Rate (%)' }},
      height: 440
    }}, {{displayModeBar: false}});
  }}

  intentBar('intentBarYT', YT);
  intentBar('intentBarRD', RD);

  // ---------- Intent vs Sentiment scatter ----------
  const scatter = {{
    type: 'scatter',
    mode: 'markers',
    x: ALL.map(d => d.avg_compound),
    y: ALL.map(d => d.intent_rate),
    text: ALL.map(d => `${{d.movie}} · ${{d.source}} · n=${{d.n}}`),
    marker: {{
      size: ALL.map(d => Math.max(8, Math.min(60, d.n / 60))),
      opacity: 0.85,
      color: ALL.map(d => d.is_focus ? '#d4af37' : 'rgba(108,117,125,.70)'),
      line: {{ width: 1, color: 'rgba(0,0,0,.25)' }}
    }},
    hovertemplate: '<b>%{{text}}</b><br>Sentiment(compound): %{{x:.3f}}<br>Intent: %{{y:.2f}}%<extra></extra>'
  }};

  Plotly.newPlot('intentVsSent', [scatter], {{
    ...plotlyLayout,
    margin: {{l: 60, r: 20, t: 10, b: 60}},
    xaxis: {{ title: 'Avg compound (VADER)' }},
    yaxis: {{ title: 'Intent Rate (%)' }},
    height: 440
  }}, {{displayModeBar: false}});

  // ---------- KPI Compare: OBaA vs cohort avg (per source) ----------
  function buildKpiCompare() {{
    if (!FOCUS_ROWS.length) return;

    const traces = [];
    FOCUS_ROWS.forEach((r, idx) => {{
      const src = r.source.toUpperCase();
      const x = KPI_GROUPS.map(k => k.label);
      const y_focus = KPI_GROUPS.map(k => r[k.key]);
      const y_cohort = KPI_GROUPS.map(k => (r[k.key] - r['delta_' + k.key])); // mean others = focus - delta

      traces.push({{
        type: 'bar',
        name: src + ' · OBaA',
        x, y: y_focus,
        marker: {{ color: idx === 0 ? '#d4af37' : 'rgba(212,175,55,.65)' }}
      }});
      traces.push({{
        type: 'bar',
        name: src + ' · Cohort Avg',
        x, y: y_cohort,
        marker: {{ color: idx === 0 ? 'rgba(108,117,125,.50)' : 'rgba(108,117,125,.30)' }}
      }});
    }});

    Plotly.newPlot('kpiCompare', traces, {{
      ...plotlyLayout,
      barmode: 'group',
      margin: {{l: 55, r: 10, t: 10, b: 110}},
      xaxis: {{ tickangle: -30 }},
      yaxis: {{ title: 'Value' }},
      height: 440,
      legend: {{ orientation: 'h', y: 1.15 }}
    }}, {{displayModeBar: false}});
  }}
  buildKpiCompare();

  // ---------- Drivers & Friction ----------
  function buildDriversFriction() {{
    if (!FOCUS_ROWS.length) return;

    // One grouped chart per source: Drivers (perf/craft/family/music) + Friction (toxicity/confusion)
    const x = FOCUS_ROWS.map(r => r.source.toUpperCase());

    const drivers = [
      {{key:'perf_rate', label:'Performance'}},
      {{key:'craft_rate', label:'Craft'}},
      {{key:'family_rate', label:'Family/Heart'}},
      {{key:'music_rate', label:'Music'}}
    ];
    const fric = [
      {{key:'toxicity_rate', label:'Toxicity'}},
      {{key:'confusion_rate', label:'Confusion'}}
    ];

    const traces = [];

    drivers.forEach((d, i) => {{
      traces.push({{
        type: 'bar',
        name: d.label,
        x,
        y: FOCUS_ROWS.map(r => r[d.key]),
      }});
    }});

    fric.forEach((d, i) => {{
      traces.push({{
        type: 'bar',
        name: d.label,
        x,
        y: FOCUS_ROWS.map(r => r[d.key]),
      }});
    }});

    Plotly.newPlot('driversFriction', traces, {{
      ...plotlyLayout,
      barmode: 'stack',
      margin: {{l: 55, r: 10, t: 10, b: 60}},
      yaxis: {{ title: '% de comentarios' }},
      height: 440,
      legend: {{ orientation: 'h', y: 1.15 }}
    }}, {{displayModeBar: false}});
  }}
  buildDriversFriction();

  // ---------- Campaign radar (OBaA) ----------
  function buildRadar() {{
    if (!FOCUS_ROWS.length) return;
    const traces = FOCUS_ROWS.map((r, idx) => {{
      return {{
        type: 'scatterpolar',
        r: CAMPAIGNS.map(c => r[c]),
        theta: CAMPAIGNS.map(c => CAMPAIGN_LABELS[c]),
        fill: 'toself',
        name: r.source.toUpperCase()
      }};
    }});

    Plotly.newPlot('campaignRadar', traces, {{
      ...plotlyLayout,
      polar: {{
        radialaxis: {{ visible: true }}
      }},
      margin: {{l: 30, r: 30, t: 10, b: 30}},
      height: 440,
      legend: {{ orientation: 'h', y: 1.1 }}
    }}, {{displayModeBar: false}});
  }}
  buildRadar();

  // ---------- Data table ----------
  function buildTable() {{
    const cols = [
      'movie','source','n','avg_compound','pos_rate','neg_rate','intent_rate',
      'perf_rate','craft_rate','family_rate','music_rate','confusion_rate','toxicity_rate',
      'intent_rank','score_reduce_confusion'
    ];

    let html = '<table><thead><tr>';
    cols.forEach(c => html += `<th>${{c}}</th>`);
    html += '</tr></thead><tbody>';

    ALL
      .sort((a,b) => (a.source === b.source ? (b.intent_rate - a.intent_rate) : (a.source > b.source ? 1 : -1)))
      .forEach(r => {{
        html += '<tr>';
        cols.forEach(c => {{
          let v = r[c];
          if (c === 'n') v = Number(v).toLocaleString();
          if (typeof v === 'number') {{
            if (c === 'avg_compound') v = v.toFixed(3);
            else v = v.toFixed(2);
          }}
          const strong = r.is_focus && c === 'movie' ? 'style="font-weight:800;color:#d4af37"' : '';
          html += `<td ${{strong}}>${{v}}</td>`;
        }});
        html += '</tr>';
      }});

    html += '</tbody></table>';
    document.getElementById('dataTable').innerHTML = html;
  }}
  buildTable();
</script>
</body>
</html>
"""

    Path(OUTPUT_HTML).write_text(html, encoding="utf-8")
    print(f"✅ Dashboard created: {OUTPUT_HTML}")
    print("   Open it in your browser.")


if __name__ == "__main__":
    generate_dashboard()