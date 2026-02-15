"""
Award Correlation Analysis: Do BAFTA and Golden Globe wins predict Oscar Best Picture?
=======================================================================================
Analyzes the historical correlation between winning Best Picture/Film at the
BAFTA Awards and Golden Globe Awards and subsequently winning Best Picture at the Oscars.
"""

import pandas as pd
import numpy as np
import re
import json
from collections import defaultdict

# ─────────────────────────────────────────────────────
# 1. LOAD & CLEAN DATA
# ─────────────────────────────────────────────────────

# --- Oscars ---
oscars_raw = pd.read_csv("archive (2)/the_oscar_award.csv")
# Keep only Best Picture categories
bp_keywords = ["OUTSTANDING PICTURE", "OUTSTANDING MOTION PICTURE",
               "BEST MOTION PICTURE", "BEST PICTURE"]
oscars_bp = oscars_raw[oscars_raw["category"].isin(bp_keywords)].copy()
oscars_bp = oscars_bp[["year_film", "film", "winner"]].copy()
oscars_bp.rename(columns={"year_film": "year"}, inplace=True)
oscars_bp["film_clean"] = oscars_bp["film"].str.strip().str.upper()
oscars_bp["winner"] = oscars_bp["winner"].astype(str).str.strip().str.lower() == "true"
print(f"Oscar Best Picture entries: {len(oscars_bp)} ({oscars_bp['year'].min()}-{oscars_bp['year'].max()})")

# Oscar winners per year
oscar_winners = oscars_bp[oscars_bp["winner"]].drop_duplicates(subset=["year"])
print(f"  Unique Oscar BP winners: {len(oscar_winners)}")

# --- Golden Globes ---
gg_raw = pd.read_csv("Golden_Globes_Awards_Dataset.csv")
# Best Picture Drama & Comedy/Musical
gg_bp_mask = gg_raw["award"].str.contains(
    "Best Motion Picture - Drama|Best Motion Picture - Musical or Comedy",
    na=False, regex=True
)
gg_bp = gg_raw[gg_bp_mask].copy()
gg_bp = gg_bp[["year", "award", "title", "winner"]].copy()
gg_bp.rename(columns={"title": "film"}, inplace=True)
gg_bp["film_clean"] = gg_bp["film"].str.strip().str.upper()
gg_bp["winner"] = gg_bp["winner"].astype(str).str.strip().str.lower() == "true"

# GG ceremonies happen in January for films of the previous year.
# The 'year' in the GG dataset is the ceremony year.
# Oscar year_film is the film release year.
# GG year 2024 → films of 2023 → Oscar year_film 2023
gg_bp["oscar_year"] = gg_bp["year"] - 1
print(f"Golden Globe BP entries: {len(gg_bp)} ({gg_bp['year'].min()}-{gg_bp['year'].max()})")

gg_winners = gg_bp[gg_bp["winner"]].copy()
print(f"  GG BP winners: {len(gg_winners)}")

# --- BAFTA ---
bafta_raw = pd.read_csv("bafta_films.csv")
# Best Film categories (the main "Film" award, NOT British Film, Animated, etc.)
bafta_bp_mask = bafta_raw["category"].str.contains(
    r"Film \| Film |Film \| Film$|Film \| Best Film", regex=True, na=False
)
bafta_bp_mask = bafta_bp_mask & ~bafta_raw["category"].str.contains(
    "British|Animated|Newcomer|United|Editing|Foreign|Not in|Language",
    case=False, na=False
)
bafta_bp = bafta_raw[bafta_bp_mask].copy()
bafta_bp = bafta_bp[["year", "category", "nominee", "winner"]].copy()
bafta_bp.rename(columns={"nominee": "film"}, inplace=True)
bafta_bp["film_clean"] = bafta_bp["film"].str.strip().str.upper()
bafta_bp["winner"] = bafta_bp["winner"].astype(str).str.strip().str.lower() == "true"

# BAFTA year in data = the ceremony year; but BAFTA ceremonies happen in Feb
# for films of the previous year. Match to Oscar year (film release year).
# BAFTA year 1949 → films of 1948 → Oscar year 1948
# But let's verify: BAFTA 1949 winner = "The Best Years of Our Lives" (1946 film, Oscar 1947)
# Actually BAFTA historically had its own cycle. Let's try year-1 and year mapping and pick best.
# We'll try both offsets and see which gives more matches.
bafta_bp["oscar_year_minus1"] = bafta_bp["year"] - 1
bafta_bp["oscar_year_same"] = bafta_bp["year"]
print(f"BAFTA Best Film entries: {len(bafta_bp)} ({bafta_bp['year'].min()}-{bafta_bp['year'].max()})")

bafta_winners = bafta_bp[bafta_bp["winner"]].copy()
print(f"  BAFTA Best Film winners: {len(bafta_winners)}")


# ─────────────────────────────────────────────────────
# 2. FUZZY FILM NAME MATCHING
# ─────────────────────────────────────────────────────
def normalize_title(title):
    """Normalize film title for matching."""
    if pd.isna(title):
        return ""
    t = str(title).upper().strip()
    # Remove articles, punctuation, extra spaces
    t = re.sub(r"[^A-Z0-9\s]", "", t)
    t = re.sub(r"\b(THE|A|AN)\b", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

# Apply normalization
oscars_bp["film_norm"] = oscars_bp["film"].apply(normalize_title)
gg_bp["film_norm"] = gg_bp["film"].apply(normalize_title)
bafta_bp["film_norm"] = bafta_bp["film"].apply(normalize_title)


# ─────────────────────────────────────────────────────
# 3. MERGE & ANALYZE
# ─────────────────────────────────────────────────────

# Build Oscar nominees lookup: year → set of normalized film names
# and Oscar winners lookup: year → set of normalized film names
oscar_nominees_by_year = oscars_bp.groupby("year")["film_norm"].apply(set).to_dict()
oscar_winners_by_year = oscars_bp[oscars_bp["winner"]].groupby("year")["film_norm"].apply(set).to_dict()
oscar_winner_names_by_year = oscars_bp[oscars_bp["winner"]].groupby("year")["film"].first().to_dict()

def find_match(film_norm, year, lookup):
    """Check if a film matches any entry in the lookup for the given year."""
    if year not in lookup:
        return False
    candidates = lookup[year]
    if film_norm in candidates:
        return True
    # Partial match: check if one is a substring of the other
    for c in candidates:
        if len(film_norm) > 3 and len(c) > 3:
            if film_norm in c or c in film_norm:
                return True
    return False

# --- Golden Globes → Oscars ---
print("\n" + "="*70)
print("GOLDEN GLOBES → OSCARS CORRELATION ANALYSIS")
print("="*70)

gg_winners_analysis = []
for _, row in gg_winners.iterrows():
    oscar_year = row["oscar_year"]
    film_norm = normalize_title(row["film"])
    won_oscar = find_match(film_norm, oscar_year, oscar_winners_by_year)
    nominated_oscar = find_match(film_norm, oscar_year, oscar_nominees_by_year)
    gg_winners_analysis.append({
        "year": row["year"],
        "oscar_year": oscar_year,
        "gg_award": row["award"],
        "film": row["film"],
        "won_oscar": won_oscar,
        "nominated_oscar": nominated_oscar
    })

gg_df = pd.DataFrame(gg_winners_analysis)

# Filter to years where both awards exist in the data
common_years_gg = set(gg_df["oscar_year"]) & set(oscar_winners_by_year.keys())
gg_df_filtered = gg_df[gg_df["oscar_year"].isin(common_years_gg)]

gg_total = len(gg_df_filtered)
gg_won = gg_df_filtered["won_oscar"].sum()
gg_nominated = gg_df_filtered["nominated_oscar"].sum()

print(f"\nGG Best Picture winners (in overlapping years): {gg_total}")
print(f"  Also won Oscar BP: {gg_won} ({gg_won/gg_total*100:.1f}%)")
print(f"  Also nominated for Oscar BP: {gg_nominated} ({gg_nominated/gg_total*100:.1f}%)")

# Breakdown by Drama vs Comedy/Musical
for award_type in ["Drama", "Musical or Comedy"]:
    subset = gg_df_filtered[gg_df_filtered["gg_award"].str.contains(award_type)]
    if len(subset) > 0:
        won = subset["won_oscar"].sum()
        print(f"\n  GG Best Picture - {award_type}: {len(subset)} winners")
        print(f"    Won Oscar: {won} ({won/len(subset)*100:.1f}%)")

# --- BAFTA → Oscars ---
print("\n" + "="*70)
print("BAFTA → OSCARS CORRELATION ANALYSIS")
print("="*70)

# Try both year offsets and pick the one with more matches
for offset_name, offset_col in [("year-1", "oscar_year_minus1"), ("same year", "oscar_year_same")]:
    matches = 0
    for _, row in bafta_winners.iterrows():
        film_norm = normalize_title(row["film"])
        if find_match(film_norm, row[offset_col], oscar_winners_by_year):
            matches += 1
    print(f"  BAFTA offset '{offset_name}': {matches} Oscar matches")

# Use year-1 (BAFTA ceremony year - 1 = film release year for pre-2000 data)
# But actually test both and use best
best_offset = "oscar_year_minus1"  # default
match_m1 = sum(find_match(normalize_title(r["film"]), r["oscar_year_minus1"], oscar_winners_by_year) for _, r in bafta_winners.iterrows())
match_same = sum(find_match(normalize_title(r["film"]), r["oscar_year_same"], oscar_winners_by_year) for _, r in bafta_winners.iterrows())
if match_same > match_m1:
    best_offset = "oscar_year_same"
print(f"  → Using offset: {best_offset}")

bafta_winners_analysis = []
for _, row in bafta_winners.iterrows():
    oscar_year = row[best_offset]
    film_norm = normalize_title(row["film"])
    won_oscar = find_match(film_norm, oscar_year, oscar_winners_by_year)
    nominated_oscar = find_match(film_norm, oscar_year, oscar_nominees_by_year)
    bafta_winners_analysis.append({
        "bafta_year": row["year"],
        "oscar_year": oscar_year,
        "film": row["film"],
        "won_oscar": won_oscar,
        "nominated_oscar": nominated_oscar
    })

bafta_df = pd.DataFrame(bafta_winners_analysis)
common_years_bafta = set(bafta_df["oscar_year"]) & set(oscar_winners_by_year.keys())
bafta_df_filtered = bafta_df[bafta_df["oscar_year"].isin(common_years_bafta)]

bafta_total = len(bafta_df_filtered)
bafta_won = bafta_df_filtered["won_oscar"].sum()
bafta_nominated = bafta_df_filtered["nominated_oscar"].sum()

print(f"\nBAFTA Best Film winners (in overlapping years): {bafta_total}")
print(f"  Also won Oscar BP: {bafta_won} ({bafta_won/bafta_total*100:.1f}%)")
print(f"  Also nominated for Oscar BP: {bafta_nominated} ({bafta_nominated/bafta_total*100:.1f}%)")


# ─────────────────────────────────────────────────────
# 4. COMBINED ANALYSIS: Both BAFTA + GG → Oscar
# ─────────────────────────────────────────────────────
print("\n" + "="*70)
print("COMBINED ANALYSIS: BAFTA + GOLDEN GLOBE → OSCAR")
print("="*70)

# Build year-based lookup of GG & BAFTA winners
gg_winner_films = {}
for _, row in gg_winners.iterrows():
    yr = row["oscar_year"]
    if yr not in gg_winner_films:
        gg_winner_films[yr] = set()
    gg_winner_films[yr].add(normalize_title(row["film"]))

bafta_winner_films = {}
for _, row in bafta_winners.iterrows():
    yr = row[best_offset]
    if yr not in bafta_winner_films:
        bafta_winner_films[yr] = set()
    bafta_winner_films[yr].add(normalize_title(row["film"]))

# For each Oscar nominee, check if it won BAFTA and/or GG
combined_data = []
for _, row in oscars_bp.iterrows():
    year = row["year"]
    film_norm = row["film_norm"]
    won_oscar = row["winner"]

    won_gg = False
    if year in gg_winner_films:
        for f in gg_winner_films[year]:
            if f == film_norm or (len(f) > 3 and len(film_norm) > 3 and (f in film_norm or film_norm in f)):
                won_gg = True
                break

    won_bafta = False
    if year in bafta_winner_films:
        for f in bafta_winner_films[year]:
            if f == film_norm or (len(f) > 3 and len(film_norm) > 3 and (f in film_norm or film_norm in f)):
                won_bafta = True
                break

    combined_data.append({
        "year": year,
        "film": row["film"],
        "won_oscar": won_oscar,
        "won_gg": won_gg,
        "won_bafta": won_bafta
    })

combined_df = pd.DataFrame(combined_data)

# Filter to years where all three awards have data
all_years = set(gg_winner_films.keys()) & set(bafta_winner_films.keys()) & set(oscar_winners_by_year.keys())
combined_filtered = combined_df[combined_df["year"].isin(all_years)]

print(f"\nOverlapping years (all 3 awards): {len(all_years)} ({min(all_years)}-{max(all_years)})")
print(f"Oscar nominees in those years: {len(combined_filtered)}")

# Compute conditional probabilities
scenarios = {
    "Won neither BAFTA nor GG": combined_filtered[(~combined_filtered["won_gg"]) & (~combined_filtered["won_bafta"])],
    "Won GG only": combined_filtered[(combined_filtered["won_gg"]) & (~combined_filtered["won_bafta"])],
    "Won BAFTA only": combined_filtered[(~combined_filtered["won_gg"]) & (combined_filtered["won_bafta"])],
    "Won both BAFTA and GG": combined_filtered[(combined_filtered["won_gg"]) & (combined_filtered["won_bafta"])],
}

print(f"\n{'Scenario':<30} {'N':>5} {'Oscar wins':>11} {'Win Rate':>10}")
print("-"*60)
scenario_results = {}
for name, subset in scenarios.items():
    n = len(subset)
    wins = subset["won_oscar"].sum()
    rate = wins / n * 100 if n > 0 else 0
    print(f"{name:<30} {n:>5} {wins:>11} {rate:>9.1f}%")
    scenario_results[name] = {"n": n, "wins": int(wins), "rate": round(rate, 1)}

# ─────────────────────────────────────────────────────
# 5. STATISTICAL TESTS
# ─────────────────────────────────────────────────────
print("\n" + "="*70)
print("STATISTICAL ANALYSIS")
print("="*70)

from scipy import stats

# Chi-squared test: GG win vs Oscar win
ct_gg = pd.crosstab(combined_filtered["won_gg"], combined_filtered["won_oscar"])
chi2_gg, p_gg, _, _ = stats.chi2_contingency(ct_gg)
print(f"\nChi-squared test (GG → Oscar):")
print(f"  χ² = {chi2_gg:.2f}, p-value = {p_gg:.6f}")
print(f"  {'Significant' if p_gg < 0.05 else 'Not significant'} at α=0.05")

# Chi-squared test: BAFTA win vs Oscar win
ct_bafta = pd.crosstab(combined_filtered["won_bafta"], combined_filtered["won_oscar"])
chi2_bafta, p_bafta, _, _ = stats.chi2_contingency(ct_bafta)
print(f"\nChi-squared test (BAFTA → Oscar):")
print(f"  χ² = {chi2_bafta:.2f}, p-value = {p_bafta:.6f}")
print(f"  {'Significant' if p_bafta < 0.05 else 'Not significant'} at α=0.05")

# Phi coefficient (correlation for 2x2 tables)
phi_gg = np.sqrt(chi2_gg / len(combined_filtered))
phi_bafta = np.sqrt(chi2_bafta / len(combined_filtered))
print(f"\nPhi coefficients (correlation strength):")
print(f"  GG → Oscar:    φ = {phi_gg:.3f}")
print(f"  BAFTA → Oscar: φ = {phi_bafta:.3f}")

# Odds ratios
def odds_ratio(ct):
    a, b = ct.iloc[0, 0], ct.iloc[0, 1]
    c, d = ct.iloc[1, 0], ct.iloc[1, 1]
    return (d * a) / (b * c) if b * c > 0 else float("inf")

or_gg = odds_ratio(ct_gg)
or_bafta = odds_ratio(ct_bafta)
print(f"\nOdds Ratios:")
print(f"  GG winner → Oscar win:    OR = {or_gg:.1f}")
print(f"  BAFTA winner → Oscar win: OR = {or_bafta:.1f}")


# ─────────────────────────────────────────────────────
# 6. DECADE-BY-DECADE ANALYSIS
# ─────────────────────────────────────────────────────
print("\n" + "="*70)
print("DECADE-BY-DECADE ANALYSIS")
print("="*70)

combined_filtered_copy = combined_filtered.copy()
combined_filtered_copy["decade"] = (combined_filtered_copy["year"] // 10) * 10

decade_data = []
for decade, group in combined_filtered_copy.groupby("decade"):
    gg_subset = group[group["won_gg"]]
    bafta_subset = group[group["won_bafta"]]
    both_subset = group[group["won_gg"] & group["won_bafta"]]

    gg_rate = gg_subset["won_oscar"].mean() * 100 if len(gg_subset) > 0 else 0
    bafta_rate = bafta_subset["won_oscar"].mean() * 100 if len(bafta_subset) > 0 else 0
    both_rate = both_subset["won_oscar"].mean() * 100 if len(both_subset) > 0 else 0

    decade_data.append({
        "decade": f"{int(decade)}s",
        "gg_winners": len(gg_subset),
        "gg_to_oscar_rate": round(gg_rate, 1),
        "bafta_winners": len(bafta_subset),
        "bafta_to_oscar_rate": round(bafta_rate, 1),
        "both_winners": len(both_subset),
        "both_to_oscar_rate": round(both_rate, 1),
    })
    print(f"  {int(decade)}s: GG→Oscar {gg_rate:.0f}% | BAFTA→Oscar {bafta_rate:.0f}% | Both→Oscar {both_rate:.0f}%")

decade_df = pd.DataFrame(decade_data)


# ─────────────────────────────────────────────────────
# 7. TIMELINE: LIST MATCHES AND MISMATCHES
# ─────────────────────────────────────────────────────
print("\n" + "="*70)
print("RECENT YEARS: GG/BAFTA/OSCAR ALIGNMENT")
print("="*70)

recent = combined_filtered[combined_filtered["year"] >= 2000].sort_values("year")
recent_winners = recent[recent["won_oscar"]].copy()
print(f"\n{'Year':<6} {'Oscar Winner':<40} {'GG?':<6} {'BAFTA?':<6}")
print("-"*60)
for _, row in recent_winners.iterrows():
    gg_mark = "✓" if row["won_gg"] else "✗"
    bafta_mark = "✓" if row["won_bafta"] else "✗"
    print(f"{int(row['year']):<6} {row['film'][:38]:<40} {gg_mark:<6} {bafta_mark:<6}")


# ─────────────────────────────────────────────────────
# 8. EXPORT DATA FOR VISUALIZATION
# ─────────────────────────────────────────────────────

export = {
    "summary": {
        "gg_to_oscar": {
            "total_winners": int(gg_total),
            "also_won_oscar": int(gg_won),
            "rate": round(gg_won/gg_total*100, 1),
            "chi2": round(chi2_gg, 2),
            "p_value": round(p_gg, 6),
            "phi": round(phi_gg, 3),
            "odds_ratio": round(or_gg, 1)
        },
        "bafta_to_oscar": {
            "total_winners": int(bafta_total),
            "also_won_oscar": int(bafta_won),
            "rate": round(bafta_won/bafta_total*100, 1),
            "chi2": round(chi2_bafta, 2),
            "p_value": round(p_bafta, 6),
            "phi": round(phi_bafta, 3),
            "odds_ratio": round(or_bafta, 1)
        }
    },
    "scenarios": scenario_results,
    "decades": decade_data,
    "recent_winners": recent_winners[["year","film","won_gg","won_bafta"]].to_dict(orient="records"),
    "gg_drama_rate": None,
    "gg_comedy_rate": None,
}

# Add GG drama/comedy breakdown
for award_type, key in [("Drama", "gg_drama_rate"), ("Musical or Comedy", "gg_comedy_rate")]:
    subset = gg_df_filtered[gg_df_filtered["gg_award"].str.contains(award_type)]
    if len(subset) > 0:
        won = subset["won_oscar"].sum()
        export[key] = {"total": int(len(subset)), "won_oscar": int(won), "rate": round(won/len(subset)*100, 1)}

with open("award_correlation_data.json", "w") as f:
    json.dump(export, f, indent=2, default=str)

print("\n✓ Analysis data exported to award_correlation_data.json")

# Also export the combined dataframe
combined_filtered.to_csv("award_correlation_combined.csv", index=False)
print("✓ Combined dataset exported to award_correlation_combined.csv")
