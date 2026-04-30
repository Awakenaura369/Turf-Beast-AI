🔥 TURF BEAST AI - PRO VERSION (UPGRADED)

Added:

- Hybrid scoring engine

- Risk-based selection

- Backtesting

- Improved stats

import streamlit as st import pandas as pd import numpy as np from collections import Counter from datetime import datetime import re

st.set_page_config(page_title="Turf Beast AI PRO", layout="wide")

-----------------------------

INPUT

-----------------------------

st.title("🐎 Turf Beast AI PRO") raw_data = st.text_area("Enter race results (comma separated)") max_horse = st.slider("Max horse number", 5, 20, 15) risk = st.selectbox("Risk", ["Conservative", "Balanced", "Aggressive"]) top_n = st.slider("Top picks", 3, 10, 5)

-----------------------------

HELPERS

-----------------------------

def parse_data(raw): tokens = re.split(r'[ ,]+', raw.strip()) return [int(t) for t in tokens if t.isdigit()]

def compute_stats(data): counts = Counter(data) total = len(data) recent = data[-10:] recent_counts = Counter(recent)

gap = {}
for n in range(1, max_horse+1):
    indices = [i for i,x in enumerate(data) if x == n]
    gap[n] = (len(data)-1 - indices[-1]) if indices else len(data)

return counts, recent_counts, gap

def compute_scores(counts, recent_counts, gap, total): scores = {} for n in range(1, max_horse+1): freq = counts.get(n, 0) / total rec = recent_counts.get(n, 0) g = gap[n]

score = (
        freq * 0.4 +
        (rec / 10) * 0.3 +
        (1 / (g + 1)) * 0.3
    )
    scores[n] = score
return scores

def select_picks(scores, gap, counts): sorted_nums = sorted(scores, key=scores.get, reverse=True)

if risk == "Conservative":
    return sorted_nums[:top_n]

elif risk == "Balanced":
    mix = sorted_nums[:top_n//2] + sorted(gap, key=gap.get, reverse=True)[:top_n//2]
    return list(dict.fromkeys(mix))[:top_n]

else:  # Aggressive
    return sorted(gap, key=gap.get, reverse=True)[:top_n]

-----------------------------

BACKTEST

-----------------------------

def backtest(data): if len(data) < 20: return None

hits = 0
tests = 0

for i in range(10, len(data)-1):
    sub = data[:i]
    actual = data[i]

    counts, recent_counts, gap = compute_stats(sub)
    scores = compute_scores(counts, recent_counts, gap, len(sub))
    picks = sorted(scores, key=scores.get, reverse=True)[:3]

    if actual in picks:
        hits += 1
    tests += 1

return round(hits/tests * 100, 1) if tests else 0

-----------------------------

RUN

-----------------------------

if st.button("Analyze"): data = parse_data(raw_data)

if len(data) < 10:
    st.error("Enter at least 10 values")
else:
    counts, recent_counts, gap = compute_stats(data)
    scores = compute_scores(counts, recent_counts, gap, len(data))
    picks = select_picks(scores, gap, counts)

    st.subheader("🎯 Picks")
    for i, p in enumerate(picks):
        conf = int(scores[p] * 100)
        st.write(f"#{p} — Confidence: {conf}%")

    st.subheader("📊 Scores")
    df = pd.DataFrame({
        "Horse": list(scores.keys()),
        "Score": list(scores.values())
    }).set_index("Horse")
    st.bar_chart(df)

    st.subheader("📈 Backtest")
    acc = backtest(data)
    if acc:
        st.success(f"Accuracy: {acc}%")
    else:
        st.info("Not enough data for backtest")

    st.subheader("📋 Stats")
    st.write("Most frequent:", counts.most_common(3))
    st.write("Top gaps:", sorted(gap.items(), key=lambda x: x[1], reverse=True)[:5])

    st.caption("⚠️ Statistical tool only")
