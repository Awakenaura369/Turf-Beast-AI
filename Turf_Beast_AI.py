import streamlit as st
import pandas as pd
import numpy as np
import json
import re
from groq import Groq
from collections import Counter
from datetime import datetime

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Turf Beast AI Explorer",
    page_icon="🐎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;700&display=swap');

/* ── BASE ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0f0d;
    color: #e8f0eb;
}
.main { background-color: #0a0f0d; padding-top: 0 !important; }
section.main > div { padding-top: 1rem; }

/* ── HEADER ── */
.tb-header {
    background: linear-gradient(135deg, #0d2818 0%, #0a1a0f 60%, #091209 100%);
    border-bottom: 2px solid #1e6b35;
    padding: 2rem 2.5rem 1.5rem;
    margin-bottom: 2rem;
    border-radius: 0 0 20px 20px;
    position: relative;
    overflow: hidden;
}
.tb-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(46,160,67,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.tb-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    letter-spacing: 4px;
    color: #ffffff;
    line-height: 1;
    text-shadow: 0 0 30px rgba(46,160,67,0.4);
    margin: 0;
}
.tb-title span { color: #2ea843; }
.tb-subtitle {
    font-size: 0.85rem;
    color: #7aab88;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 6px;
}

/* ── STAT CARDS ── */
.stat-row { display: flex; gap: 12px; margin-bottom: 1.5rem; flex-wrap: wrap; }
.stat-card {
    background: #101f14;
    border: 1px solid #1c3d24;
    border-radius: 12px;
    padding: 14px 20px;
    flex: 1;
    min-width: 120px;
    text-align: center;
}
.stat-card .val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: #2ea843;
    line-height: 1;
}
.stat-card .lbl {
    font-size: 0.7rem;
    color: #7aab88;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* ── SECTION HEADERS ── */
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.3rem;
    letter-spacing: 3px;
    color: #2ea843;
    text-transform: uppercase;
    border-bottom: 1px solid #1c3d24;
    padding-bottom: 6px;
    margin-bottom: 1rem;
}

/* ── PICK CARDS ── */
.picks-grid { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 1.5rem; }
.pick-card {
    background: linear-gradient(135deg, #0d2818, #0a1a0f);
    border: 1px solid #1e6b35;
    border-radius: 14px;
    padding: 16px 20px;
    min-width: 90px;
    text-align: center;
    position: relative;
    transition: transform 0.2s;
}
.pick-card:hover { transform: translateY(-3px); border-color: #2ea843; }
.pick-card .pick-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem;
    color: #ffffff;
    line-height: 1;
}
.pick-card .pick-label {
    font-size: 0.65rem;
    color: #7aab88;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.pick-card .pick-conf {
    font-size: 0.75rem;
    color: #2ea843;
    font-weight: 700;
    margin-top: 4px;
}
.pick-card.top { border-color: #f5c518; }
.pick-card.top .pick-num { color: #f5c518; }
.pick-card.top::before {
    content: '★';
    position: absolute;
    top: -8px; right: 8px;
    font-size: 0.8rem;
    color: #f5c518;
}

/* ── REASONING BOX ── */
.reasoning-box {
    background: #0d1f12;
    border: 1px solid #1c3d24;
    border-left: 4px solid #2ea843;
    border-radius: 12px;
    padding: 18px 22px;
    font-size: 0.9rem;
    line-height: 1.7;
    color: #c8dccb;
    margin-bottom: 1.5rem;
}

/* ── HOT / COLD CHIPS ── */
.chip-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1rem; }
.chip {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.chip.hot { background: rgba(255,80,50,0.15); color: #ff6b4a; border: 1px solid rgba(255,80,50,0.3); }
.chip.cold { background: rgba(80,140,255,0.15); color: #6fa3ff; border: 1px solid rgba(80,140,255,0.3); }
.chip.warm { background: rgba(255,180,50,0.15); color: #ffc94a; border: 1px solid rgba(255,180,50,0.3); }

/* ── HISTORY ENTRY ── */
.hist-entry {
    background: #0d1f12;
    border: 1px solid #1c3d24;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.82rem;
    color: #9abda0;
}
.hist-entry strong { color: #2ea843; }

/* ── DISCLAIMER ── */
.disclaimer {
    background: rgba(255,180,50,0.07);
    border: 1px solid rgba(255,180,50,0.2);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 0.78rem;
    color: #c8a84a;
    margin-top: 1.5rem;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: #080e0a !important;
    border-right: 1px solid #1c3d24;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] p { color: #9abda0 !important; }

/* ── INPUT ── */
textarea, input[type="text"], input[type="password"] {
    background-color: #101f14 !important;
    border: 1px solid #1c3d24 !important;
    color: #e8f0eb !important;
    border-radius: 10px !important;
}

/* ── BUTTON ── */
.stButton>button {
    width: 100%;
    background: linear-gradient(135deg, #1e6b35, #145228) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 3px !important;
    transition: all 0.2s !important;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #2ea843, #1e6b35) !important;
    box-shadow: 0 4px 20px rgba(46,168,67,0.3) !important;
    transform: translateY(-1px);
}

/* ── DIVIDER ── */
hr { border-color: #1c3d24 !important; }

/* ── SUCCESS / ERROR ── */
.stAlert { border-radius: 10px !important; }

/* ── CONF BAR ── */
.conf-bar-wrap { margin: 6px 0 12px; }
.conf-bar-bg {
    background: #1c3d24;
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, #1e6b35, #2ea843);
    transition: width 0.6s ease;
}
.conf-label { font-size: 0.72rem; color: #7aab88; margin-bottom: 3px; display: flex; justify-content: space-between; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown("""
<div class="tb-header">
    <div class="tb-title">TURF <span>BEAST</span> AI</div>
    <div class="tb-subtitle">Statistical Intelligence for Horse Racing Analysis</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ الإعدادات")
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    model_choice = st.selectbox("موديل AI", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    st.markdown("---")
    top_n = st.slider("عدد الأرقام المقترحة", 3, 10, 5)
    risk_level = st.select_slider("مستوى المخاطرة", options=["Conservative", "Balanced", "Aggressive"])
    st.markdown("---")
    max_horse = st.number_input("أكبر رقم خيل ممكن", min_value=5, max_value=20, value=15)
    st.markdown("---")
    if st.button("🗑️ مسح السجل"):
        st.session_state.history = []
        st.success("تم مسح السجل")

# ──────────────────────────────────────────────
# INPUT
# ──────────────────────────────────────────────
st.markdown('<div class="section-title">📊 البيانات التاريخية</div>', unsafe_allow_html=True)

col_in, col_tip = st.columns([3, 1])
with col_in:
    raw_data = st.text_area(
        "أدخل أرقام الخيول الرابحة (مفصولة بفاصلة)",
        placeholder="مثال: 3, 7, 1, 12, 5, 3, 9, 7, 2, 14, 5, 1, 7...",
        height=100,
        label_visibility="collapsed"
    )
with col_tip:
    st.info("💡 كل رقم = الخيل الرابح في كورس.\nدخل على الأقل **10 نتائج** لتحليل جيد.")

run_btn = st.button("🚀  ابدأ التحليل الذكي")

# ──────────────────────────────────────────────
# STATS HELPERS
# ──────────────────────────────────────────────
def compute_stats(data: list, max_h: int):
    counts = Counter(data)
    total = len(data)
    
    # Frequency %
    freq = {n: round(counts[n] / total * 100, 1) for n in counts}
    
    # Hot / Cold / Warm (last 10 vs overall)
    recent = data[-10:] if len(data) >= 10 else data
    recent_counts = Counter(recent)
    
    hot, cold, warm = [], [], []
    for n in range(1, max_h + 1):
        r = recent_counts.get(n, 0)
        g = counts.get(n, 0)
        if r >= 2 or (r == 1 and g >= 3):
            hot.append(n)
        elif r == 0 and g == 0:
            cold.append(n)
        elif g >= 2:
            warm.append(n)
    
    # Gap analysis: races since last appearance
    gap = {}
    for n in range(1, max_h + 1):
        indices = [i for i, x in enumerate(data) if x == n]
        gap[n] = (total - 1 - indices[-1]) if indices else total

    return counts, freq, hot, cold, warm, gap

def conf_bar_html(label, value, color="#2ea843"):
    return f"""
<div class="conf-bar-wrap">
  <div class="conf-label"><span>{label}</span><span>{value}%</span></div>
  <div class="conf-bar-bg">
    <div class="conf-bar-fill" style="width:{value}%; background: linear-gradient(90deg, #1e6b35, {color});"></div>
  </div>
</div>"""

# ──────────────────────────────────────────────
# GROQ PROMPT
# ──────────────────────────────────────────────
def build_prompt(data, freq, hot, cold, warm, gap, top_n, risk, max_h):
    return f"""
You are a professional Paris Turf statistical analyst. Your job is purely statistical pattern recognition — NOT gambling advice.

INPUT DATA:
- Full sequence ({len(data)} races): {data}
- Frequency map (number: % of appearances): {freq}
- Hot numbers (recent surge): {hot}
- Cold numbers (long absence, due for return statistically): {cold}
- Warm numbers (consistent performers): {warm}
- Gap since last appearance (races): {gap}
- Risk preference: {risk}
- Max horse number on track: {max_h}
- Request: Top {top_n} picks for next race

TASK:
Return ONLY a valid JSON object (no markdown, no explanation outside JSON) with this exact structure:
{{
  "picks": [
    {{"number": <int>, "confidence": <int 1-99>, "reason": "<short reason max 10 words>"}},
    ...
  ],
  "reasoning": "<2-3 sentences overall pattern analysis>",
  "strategy": "<one sentence on risk approach applied>"
}}

Rules:
- All numbers must be between 1 and {max_h}
- Confidence values must vary meaningfully (not all the same)
- Order picks from highest to lowest confidence
- Be statistically logical, not random
"""

# ──────────────────────────────────────────────
# MAIN LOGIC
# ──────────────────────────────────────────────
if run_btn:
    if not api_key:
        st.error("⚠️ أدخل Groq API Key في الشريط الجانبي.")
    elif not raw_data.strip():
        st.warning("⚠️ أدخل البيانات التاريخية أولاً.")
    else:
        # --- PARSE & VALIDATE ---
        tokens = re.split(r'[,\s]+', raw_data.strip())
        clean_list = []
        invalid = []
        for t in tokens:
            if t.isdigit():
                n = int(t)
                if 1 <= n <= max_horse:
                    clean_list.append(n)
                else:
                    invalid.append(t)
        
        if invalid:
            st.warning(f"⚠️ تم تجاهل هاد الأرقام (خارج النطاق 1-{max_horse}): {', '.join(invalid)}")
        
        if len(clean_list) < 5:
            st.error(f"❌ دخل على الأقل 5 أرقام صحيحة بين 1 و {max_horse}.")
        else:
            # --- STATS ---
            counts, freq, hot, cold, warm, gap = compute_stats(clean_list, max_horse)
            total = len(clean_list)

            # --- STAT CARDS ---
            unique_nums = len(counts)
            most_common_num, most_common_cnt = counts.most_common(1)[0]
            avg_gap = round(np.mean(list(gap.values())), 1)

            st.markdown(f"""
            <div class="stat-row">
                <div class="stat-card"><div class="val">{total}</div><div class="lbl">كورسات محللة</div></div>
                <div class="stat-card"><div class="val">{unique_nums}</div><div class="lbl">أرقام مختلفة</div></div>
                <div class="stat-card"><div class="val">{most_common_num}</div><div class="lbl">الأكثر تكراراً</div></div>
                <div class="stat-card"><div class="val">{len(hot)}</div><div class="lbl">أرقام ساخنة</div></div>
                <div class="stat-card"><div class="val">{avg_gap}</div><div class="lbl">متوسط الغياب</div></div>
            </div>
            """, unsafe_allow_html=True)

            # --- HOT / COLD / WARM ---
            st.markdown('<div class="section-title">🌡️ تصنيف الأرقام</div>', unsafe_allow_html=True)
            chips_html = '<div class="chip-row">'
            for n in hot[:8]:
                chips_html += f'<span class="chip hot">🔥 {n}</span>'
            for n in warm[:8]:
                chips_html += f'<span class="chip warm">⚡ {n}</span>'
            for n in cold[:8]:
                chips_html += f'<span class="chip cold">❄️ {n}</span>'
            chips_html += '</div>'
            st.markdown(chips_html, unsafe_allow_html=True)

            # --- AI CALL ---
            st.markdown('<div class="section-title">🤖 تحليل الذكاء الاصطناعي</div>', unsafe_allow_html=True)
            
            with st.spinner("جاري تحليل الأنماط الإحصائية..."):
                try:
                    client = Groq(api_key=api_key)
                    prompt = build_prompt(clean_list, freq, hot, cold, warm, gap, top_n, risk_level, max_horse)
                    
                    completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=model_choice,
                        temperature=0.3,
                        max_tokens=800
                    )
                    
                    raw_response = completion.choices[0].message.content.strip()
                    
                    # Clean JSON
                    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        result = json.loads(raw_response)

                    picks = result.get("picks", [])[:top_n]
                    reasoning = result.get("reasoning", "")
                    strategy = result.get("strategy", "")

                    # --- PICKS ---
                    picks_html = '<div class="picks-grid">'
                    for i, p in enumerate(picks):
                        cls = "top" if i == 0 else "pick-card"
                        card_cls = f"pick-card {cls}" if i == 0 else "pick-card"
                        picks_html += f"""
                        <div class="{card_cls}">
                            <div class="pick-num">{p['number']}</div>
                            <div class="pick-label">{p.get('reason','')}</div>
                            <div class="pick-conf">{p['confidence']}%</div>
                        </div>"""
                    picks_html += '</div>'
                    st.markdown(picks_html, unsafe_allow_html=True)

                    # --- CONFIDENCE BARS ---
                    st.markdown('<div class="section-title">📊 مستوى الثقة</div>', unsafe_allow_html=True)
                    bars_html = ""
                    for p in picks:
                        color = "#f5c518" if p['confidence'] >= 75 else "#2ea843" if p['confidence'] >= 50 else "#6fa3ff"
                        bars_html += conf_bar_html(f"الخيل {p['number']}", p['confidence'], color)
                    st.markdown(bars_html, unsafe_allow_html=True)

                    # --- REASONING ---
                    st.markdown('<div class="section-title">🧠 التحليل</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="reasoning-box">{reasoning}<br><br><em style="color:#7aab88">{strategy}</em></div>', unsafe_allow_html=True)

                    # --- FREQUENCY CHART ---
                    st.markdown('<div class="section-title">📈 تكرار الأرقام</div>', unsafe_allow_html=True)
                    df_chart = pd.DataFrame([
                        {"Cheval": str(n), "Fréquence %": round(counts.get(n, 0) / total * 100, 1)}
                        for n in range(1, max_horse + 1)
                    ]).set_index("Cheval")
                    st.bar_chart(df_chart, color="#2ea843")

                    # --- SAVE HISTORY ---
                    st.session_state.history.insert(0, {
                        "time": datetime.now().strftime("%H:%M"),
                        "races": total,
                        "picks": [p["number"] for p in picks],
                        "risk": risk_level
                    })

                    # --- DISCLAIMER ---
                    st.markdown("""
                    <div class="disclaimer">
                    ⚠️ <strong>Disclaimer:</strong> هاد التول كايقدم تحليل إحصائي فقط. المراهنات على الخيل فيها مخاطر حقيقية.
                    هاد التطبيق مو ضمان للربح ومو نصيحة مالية. ارهن بمسؤولية.
                    </div>
                    """, unsafe_allow_html=True)

                except json.JSONDecodeError:
                    st.error("⚠️ الموديل رجع جواب غير منظم. جرب مرة أخرى أو غير الموديل.")
                    with st.expander("Raw response"):
                        st.code(raw_response)
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")

# ──────────────────────────────────────────────
# HISTORY
# ──────────────────────────────────────────────
if st.session_state.history:
    st.markdown("---")
    st.markdown('<div class="section-title">🕓 سجل التحليلات</div>', unsafe_allow_html=True)
    for entry in st.session_state.history[:5]:
        picks_str = " · ".join([str(p) for p in entry["picks"]])
        st.markdown(f"""
        <div class="hist-entry">
            <strong>{entry['time']}</strong> &nbsp;|&nbsp;
            {entry['races']} كورس &nbsp;|&nbsp;
            Risk: {entry['risk']} &nbsp;|&nbsp;
            Picks: <strong>{picks_str}</strong>
        </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.caption("© 2026 Mouhcine Digital Systems | Turf Beast AI Explorer v2.0")
