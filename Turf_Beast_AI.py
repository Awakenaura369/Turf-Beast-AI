import streamlit as st
import pandas as pd
import numpy as np
from groq import Groq

# إعداد الصفحة
st.set_page_config(page_title="Turf Beast AI", page_icon="🐎", layout="centered")

# ستايل مغربي خفيف
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #2e7d32; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐎 Turf Beast AI Explorer")
st.write("تحليل احترافي مبني على الإحصاء وذكاء Groq")

# إدخال المفتاح (تقدر تخليه ثابت إلا بغيتي)
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# فورم إدخال البيانات
with st.expander("📊 مدخلات البيانات التاريخية", expanded=True):
    raw_data = st.text_area("دخل نتائج الكورسات اللخرة (فرق بيناتهم بـ فاصلة)", 
                          placeholder="مثال: 4, 12, 1, 8, 5, 4, 9, 12, 3")
    
    col1, col2 = st.columns(2)
    with col1:
        top_n = st.slider("عدد الأرقام اللي بغيتي تخمن", 3, 8, 5)
    with col2:
        risk_level = st.select_slider("مستوى المخاطرة", options=["Safe", "Balanced", "Aggressive"])

if st.button("🚀 تحليل وتوليد التوقعات"):
    if not api_key:
        st.error("خاصك تدخّل API Key ديال Groq")
    elif not raw_data:
        st.warning("دخل الأرقام أولا أ خاي")
    else:
        try:
            # 1. المرحلة الإحصائية (Pure Python)
            numbers_list = [int(n.strip()) for n in raw_data.split(",") if n.strip().isdigit()]
            df = pd.Series(numbers_list).value_counts().reset_index()
            df.columns = ['Number', 'Frequency']
            
            # حساب الاحتمالات المبسطة
            total = len(numbers_list)
            df['Probability'] = (df['Frequency'] / total) * 100
            
            # 2. تحضير التحليل للـ AI
            stats_summary = df.to_string(index=False)
            last_5 = numbers_list[-5:] # آخر 5 أرقام دخلو
            
            # 3. استشارة Groq (The Brain)
            client = Groq(api_key=api_key)
            
            prompt = f"""
            System: You are an expert Horse Racing Analyst (Turf specialist).
            Data Analysis:
            - Historical Frequency of numbers: {stats_summary}
            - Last 5 winners trend: {last_5}
            - User Risk Level: {risk_level}
            - Target: Suggest the best {top_n} numbers for the next Paris Turf race.
            
            Task:
            1. Use the 'Law of Small Numbers' and 'Hot/Cold numbers' theory to analyze.
            2. Provide the top {top_n} suggested numbers.
            3. Give a professional 'Expert Insight' (max 2 lines) in English about why these numbers.
            4. Add a disclaimer: 'Racing involves luck'.
            """
            
            with st.spinner('جاري تحليل الأرقام بدقة...'):
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192", # استعملنا الموديل الكبير للدقة
                    temperature=0.6 # توازن بين الإبداع والمنطق
                )
                
                response = chat_completion.choices[0].message.content
                
                # عرض النتائج
                st.subheader("🎯 التوقعات المقترحة")
                st.markdown(f"```\n{response}\n```")
                
                # رسم مبياني بسيط للتردد
                st.subheader("📈 تكرار الأرقام في البيانات اللي دخلتي")
                st.bar_chart(df.set_index('Number')['Frequency'])
                
        except Exception as e:
            st.error(f"وقع خطأ في معالجة البيانات: {e}")

st.divider()
st.caption("Developed by Mouhcine Digital Systems - AI Marketing Logic applied to Turf")
