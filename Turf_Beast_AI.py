# -*- coding: utf-8 -*-
# TURF BEAST AI - CLEAN VERSION

import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
import re

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Turf Beast AI", layout="wide")

st.title("Turf Beast AI")
st.caption("Statistical Horse Racing Analyzer")

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.header("Settings")
    risk = st.selectbox("Risk", ["Conservative", "Balanced", "Aggressive"])
    top_n = st.slider("Top Picks", 3, 10, 5)
    max_horse = st.slider("Max Horse", 5, 20, 15)

# -----------------------------
# INPUT
# -----------------------------
raw_data = st.text_area("Enter race results (comma separated)")

# -----------------------------
# FUNCTIONS
# -----------------------------
def parse_data(raw):
    tokens = re.split(r'[ ,]+', raw.strip())
    return [int(t) for t in tokens if t.isdigit()]

def compute_stats(data):
    counts = Counter(data)
    total = len(data)
    recent = data[-10:]
    recent_counts = Counter(recent)

    gap = {}
    for n in range(1, max_horse + 1):
        indices = [i for i, x in enumerate(data) if x == n]
        gap[n] = (len(data) - 1 - indices[-1]) if indices else len(data)

    return counts, recent_counts, gap, total

def compute_scores(counts, recent_counts, gap, total):
    scores = {}
    for n in range(1, max_horse + 1):
        freq = counts.get(n, 0) / total
        rec = recent_counts.get(n, 0)
        g = gap[n]

        score = (
            freq * 0.4 +
            (rec / 10) * 0.3 +
            (1 / (g + 1)) * 0.3
        )
        scores[n] = score
    return scores

def select_picks(scores, gap):
    sorted_nums = sorted(scores, key=scores.get, reverse=True)

    if risk == "Conservative":
        return sorted_nums[:top_n]

    elif risk == "Balanced":
        half = top_n // 2
        mix = sorted_nums[:half] + sorted(gap, key=gap.get, reverse=True)[:half]
        return list(dict.fromkeys(mix))[:top_n]

    else:
        return sorted(gap, key=gap.get, reverse=True)[:top_n]

def backtest(data):
    if len(data) < 20:
        return None

    hits = 0
    tests = 0

    for i in range(10, len(data) - 1):
        sub = data[:i]
        actual = data[i]

        counts, recent_counts, gap, total = compute_stats(sub)
        scores = compute_scores(counts, recent_counts, gap, total)
        picks = sorted(scores, key=scores.get, reverse=True)[:3]

        if actual in picks:
            hits += 1
        tests += 1

    return round(hits / tests * 100, 1) if tests else 0

# -----------------------------
# RUN
# -----------------------------
if st.button("Analyze"):
    data = parse_data(raw_data)

    if len(data) < 10:
        st.error("Enter at least 10 numbers")
    else:
        counts, recent_counts, gap, total = compute_stats(data)
        scores = compute_scores(counts, recent_counts, gap, total)
        picks = select_picks(scores, gap)

        st.subheader("Top Picks")
        for p in picks:
            conf = int(scores[p] * 100)
            st.write(f"Horse {p} - Confidence: {conf}%")

        st.subheader("Score Distribution")
        df = pd.DataFrame({
            "Horse": list(scores.keys()),
            "Score": list(scores.values())
        }).set_index("Horse")
        st.bar_chart(df)

        st.subheader("Backtest")
        acc = backtest(data)
        if acc:
            st.success(f"Accuracy: {acc}%")
        else:
            st.info("Not enough data")

        st.subheader("Stats")
        st.write("Most frequent:", counts.most_common(5))
        st.write("Top gaps:", sorted(gap.items(), key=lambda x: x[1], reverse=True)[:5])

        if "history" not in st.session_state:
            st.session_state.history = []

        st.session_state.history.insert(0, {
            "time": datetime.now().strftime("%H:%M"),
            "picks": picks
        })

# -----------------------------
# HISTORY
# -----------------------------
if "history" in st.session_state and st.session_state.history:
    st.subheader("History")
    for h in st.session_state.history[:5]:
        st.write(f"{h['time']} -> {h['picks']}")

st.caption("This is a statistical tool only")
