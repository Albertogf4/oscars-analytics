#!/usr/bin/env python3
"""
Oscar Markets Dashboard for "One Battle After Another"

Interactive dashboard visualizing Kalshi prediction market data
for the movie's Oscar chances.
"""

import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np

# Load data
with open("oscars_obaa_markets.json", "r") as f:
    data = json.load(f)

markets = data["markets"]

# =============================================================================
# DATA PREPARATION
# =============================================================================

# Separate main category markets from "count" markets
main_markets = []
count_markets = []

for m in markets:
    if "KXOSCARCOUNT" in m["ticker"]:
        # Extract the number from ticker (e.g., KXOSCARCOUNT-26-ONE-6 -> 6)
        try:
            num = int(m["ticker"].split("-")[-1])
            m["award_count"] = num
            count_markets.append(m)
        except ValueError:
            pass
    else:
        main_markets.append(m)

# Create DataFrame for main markets
df_main = pd.DataFrame(main_markets)

# Extract category names from titles
def extract_category(title):
    if "Best Picture" in title:
        return "Best Picture"
    elif "Best Director" in title:
        return "Best Director"
    elif "Best Actor" in title and "Supporting" not in title:
        return "Best Actor"
    elif "Best Actress" in title and "Supporting" not in title:
        return "Best Actress"
    elif "Supporting Actor" in title:
        return "Best Supp. Actor"
    elif "Supporting Actress" in title:
        return "Best Supp. Actress"
    elif "Adapted Screenplay" in title:
        return "Adapted Screenplay"
    elif "Cinematography" in title:
        return "Cinematography"
    elif "Film Editing" in title:
        return "Film Editing"
    elif "Original Score" in title or "Music" in title:
        return "Original Score"
    elif "Production Design" in title:
        return "Production Design"
    elif "Sound" in title:
        return "Sound"
    else:
        return title.split("win")[1].split("at")[0].strip() if "win" in title else "Other"

def extract_person(subtitle):
    if "::" in subtitle:
        return subtitle.split("::")[0].strip()
    return ""

df_main["category"] = df_main["title"].apply(extract_category)
df_main["person"] = df_main["subtitle"].apply(extract_person)
df_main["probability"] = df_main["yes_price_cents"] / 100

# Sort by probability
df_main = df_main.sort_values("yes_price_cents", ascending=True)

# =============================================================================
# CREATE DASHBOARD
# =============================================================================

# Create figure with subplots
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "Win Probability by Category",
        "Trading Volume by Category",
        "Price vs Volume Analysis",
        "Expected Oscar Wins Distribution",
        "Market Activity (24h Volume)",
        "Open Interest Distribution"
    ),
    specs=[
        [{"type": "bar"}, {"type": "bar"}],
        [{"type": "scatter"}, {"type": "bar"}],
        [{"type": "bar"}, {"type": "pie"}]
    ],
    vertical_spacing=0.12,
    horizontal_spacing=0.1
)

# Color scale based on probability
colors = px.colors.sample_colorscale(
    "RdYlGn",
    [p/100 for p in df_main["yes_price_cents"]]
)

# -----------------------------------------------------------------------------
# Chart 1: Win Probability (Horizontal Bar)
# -----------------------------------------------------------------------------
labels = [f"{row['category']}" + (f" ({row['person']})" if row['person'] else "")
          for _, row in df_main.iterrows()]

fig.add_trace(
    go.Bar(
        y=labels,
        x=df_main["yes_price_cents"],
        orientation="h",
        marker=dict(color=colors),
        text=[f"{p}%" for p in df_main["yes_price_cents"]],
        textposition="outside",
        name="Win Probability",
        hovertemplate="<b>%{y}</b><br>Probability: %{x}%<extra></extra>"
    ),
    row=1, col=1
)

# -----------------------------------------------------------------------------
# Chart 2: Trading Volume (Horizontal Bar)
# -----------------------------------------------------------------------------
df_volume = df_main.sort_values("volume", ascending=True)
labels_vol = [f"{row['category']}" + (f" ({row['person']})" if row['person'] else "")
              for _, row in df_volume.iterrows()]

fig.add_trace(
    go.Bar(
        y=labels_vol,
        x=df_volume["volume"],
        orientation="h",
        marker=dict(color=px.colors.sample_colorscale("Blues", [v/df_volume["volume"].max() for v in df_volume["volume"]])),
        text=[f"{v:,.0f}" for v in df_volume["volume"]],
        textposition="outside",
        name="Volume",
        hovertemplate="<b>%{y}</b><br>Volume: %{x:,.0f}<extra></extra>"
    ),
    row=1, col=2
)

# -----------------------------------------------------------------------------
# Chart 3: Price vs Volume Scatter (KEY INSIGHT CHART)
# -----------------------------------------------------------------------------
# Add quadrant annotations
fig.add_trace(
    go.Scatter(
        x=df_main["yes_price_cents"],
        y=df_main["volume"],
        mode="markers+text",
        marker=dict(
            size=15,
            color=df_main["yes_price_cents"],
            colorscale="RdYlGn",
            showscale=True,
            colorbar=dict(title="Win %", x=0.45, len=0.3, y=0.5)
        ),
        text=df_main["category"],
        textposition="top center",
        textfont=dict(size=9),
        name="Markets",
        hovertemplate="<b>%{text}</b><br>Price: %{x}%<br>Volume: %{y:,.0f}<extra></extra>"
    ),
    row=2, col=1
)

# Add quadrant lines
median_price = df_main["yes_price_cents"].median()
median_volume = df_main["volume"].median()

fig.add_hline(y=median_volume, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)

# Add quadrant labels
fig.add_annotation(x=25, y=df_main["volume"].max()*0.9, text="LOW PRICE<br>HIGH VOLUME<br>(Confident Underdogs)",
                   showarrow=False, font=dict(size=8, color="red"), row=2, col=1)
fig.add_annotation(x=75, y=df_main["volume"].max()*0.9, text="HIGH PRICE<br>HIGH VOLUME<br>(Strong Favorites)",
                   showarrow=False, font=dict(size=8, color="green"), row=2, col=1)

# -----------------------------------------------------------------------------
# Chart 4: Award Count Distribution
# -----------------------------------------------------------------------------
df_count = pd.DataFrame(count_markets).sort_values("award_count")

fig.add_trace(
    go.Bar(
        x=df_count["award_count"],
        y=df_count["yes_price_cents"],
        marker=dict(
            color=df_count["yes_price_cents"],
            colorscale="Viridis"
        ),
        text=[f"{p}%" for p in df_count["yes_price_cents"]],
        textposition="outside",
        name="Award Count Prob",
        hovertemplate="<b>%{x} Awards</b><br>Probability: %{y}%<extra></extra>"
    ),
    row=2, col=2
)

# -----------------------------------------------------------------------------
# Chart 5: 24h Activity
# -----------------------------------------------------------------------------
df_active = df_main[df_main["volume_24h"] > 0].sort_values("volume_24h", ascending=True)
labels_24h = [f"{row['category']}" for _, row in df_active.iterrows()]

fig.add_trace(
    go.Bar(
        y=labels_24h,
        x=df_active["volume_24h"],
        orientation="h",
        marker=dict(color="orange"),
        text=[f"{v:,.0f}" for v in df_active["volume_24h"]],
        textposition="outside",
        name="24h Volume",
        hovertemplate="<b>%{y}</b><br>24h Volume: %{x:,.0f}<extra></extra>"
    ),
    row=3, col=1
)

# -----------------------------------------------------------------------------
# Chart 6: Open Interest Pie
# -----------------------------------------------------------------------------
top_oi = df_main.nlargest(6, "open_interest")
labels_oi = [f"{row['category']}" for _, row in top_oi.iterrows()]

fig.add_trace(
    go.Pie(
        labels=labels_oi,
        values=top_oi["open_interest"],
        hole=0.4,
        textinfo="label+percent",
        textposition="outside",
        name="Open Interest"
    ),
    row=3, col=2
)

# =============================================================================
# LAYOUT
# =============================================================================

fig.update_layout(
    title=dict(
        text="<b>One Battle After Another</b> - Oscar Prediction Markets Dashboard<br>" +
             f"<sup>Data from Kalshi | {data['timestamp'][:10]}</sup>",
        x=0.5,
        font=dict(size=20)
    ),
    showlegend=False,
    height=1200,
    width=1400,
    template="plotly_white"
)

# Update axes
fig.update_xaxes(title_text="Win Probability (%)", row=1, col=1, range=[0, 105])
fig.update_xaxes(title_text="Total Contracts Traded", row=1, col=2)
fig.update_xaxes(title_text="Win Probability (%)", row=2, col=1)
fig.update_yaxes(title_text="Trading Volume", row=2, col=1)
fig.update_xaxes(title_text="Number of Oscar Wins", row=2, col=2)
fig.update_yaxes(title_text="Probability (%)", row=2, col=2)
fig.update_xaxes(title_text="Contracts (Last 24h)", row=3, col=1)

# =============================================================================
# SAVE AND DISPLAY
# =============================================================================

# Save as HTML
fig.write_html("dashboard.html")
print("Dashboard saved to: dashboard.html")

# Also create a summary statistics table
print("\n" + "="*70)
print("SUMMARY STATISTICS")
print("="*70)

print(f"\nTotal Markets Analyzed: {len(main_markets)}")
print(f"Total Trading Volume: {df_main['volume'].sum():,.0f} contracts")
print(f"Total Open Interest: {df_main['open_interest'].sum():,.0f} contracts")

print("\n--- TOP OSCAR CONTENDERS (by probability) ---")
top_5 = df_main.nlargest(5, "yes_price_cents")[["category", "person", "yes_price_cents", "volume"]]
for _, row in top_5.iterrows():
    person = f" ({row['person']})" if row['person'] else ""
    print(f"  {row['category']}{person}: {row['yes_price_cents']}% ({row['volume']:,.0f} vol)")

print("\n--- EXPECTED OSCAR WINS ---")
# Calculate expected value from count markets
expected_wins = sum(m["award_count"] * m["yes_price_cents"] / 100 for m in count_markets)
print(f"  Expected wins: {expected_wins:.1f} Oscars")

# Most likely outcome
most_likely = max(count_markets, key=lambda x: x["yes_price_cents"])
print(f"  Most likely outcome: {most_likely['award_count']} wins ({most_likely['yes_price_cents']}%)")

print("\n--- PRICE vs VOLUME INSIGHT ---")
print("""
  The relationship between low prices and high volumes reveals market confidence:

  LOW PRICE + HIGH VOLUME = "Confident Underdogs"
  - Market has traded heavily and concluded this outcome is unlikely
  - Example: DiCaprio for Best Actor (11% price, 783K volume)
  - High volume means many traders agree on the low probability
  - The market has "priced in" the competition

  HIGH PRICE + HIGH VOLUME = "Strong Favorites"
  - Market consensus strongly supports this outcome
  - Example: Best Picture (74% price, 1M+ volume)
  - Both price and volume validate the favorite status

  LOW VOLUME = Less certainty, thinner market, prices may be less reliable
""")

# Show the dashboard
fig.show()
