import streamlit as st
import pandas as pd
import numpy as np
from groq import Groq

# إعداد الصفحة
st.set_page_config(page_title="Turf Beast AI Explorer", page_icon="🐎", layout="centered")

# ستايل احترافي متناسق
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        background-color: #1b5e20; 
        color: white; 
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #2e7d32;
        border: none;
    }
    .prediction-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #1b5e20;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐎 Turf Beast AI Explorer")
st.markdown("**نظام تحليل مراهنات الخيول المبني على الإحصاء والذكاء الاصطناعي**")

# إعدادات الشريط الجانبي
st.sidebar.header("⚙️ الإعدادات")
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# اختيار الموديل (تم تحديث الموديلات هنا)
model_choice = st.sidebar.selectbox("اختر موديل الذكاء الاصطناعي", 
                                    ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

# واجهة إدخال البيانات
with st.container():
    st.subheader("📊 إدخال البيانات التاريخية")
    raw_data = st.text_area("أدخل الأرقام الرابحة (افصل بينها بفاصلة)", 
                          placeholder="مثال: 5, 12, 1, 8, 3, 5, 9, 12...",
                          help="دخل أرقام الخيول اللي ربحوا ف الكورسات اللي فاتو")
    
    col1, col2 = st.columns(2)
    with col1:
        top_n = st.slider("عدد الأرقام المقترحة", 3, 10, 5)
    with col2:
        risk_level = st.select_slider("مستوى المخاطرة (Risk)", 
                                    options=["Low", "Medium", "High"])

if st.button("🚀 ابدأ التحليل الذكي"):
    if not api_key:
        st.error("المرجو إدخال مفتاح API Key الخاص بـ Groq في الجانب.")
    elif not raw_data:
        st.warning("المرجو إدخال البيانات التاريخية للتحليل.")
    else:
        try:
            # 1. المعالجة الإحصائية (Clean Data)
            clean_list = [int(n.strip()) for n in raw_data.split(",") if n.strip().isdigit()]
            
            if len(clean_list) < 5:
                st.error("دخل على الأقل 5 أرقام باش يكون التحليل منطقي.")
            else:
                # حساب الترددات باستعمال Pandas
                df_counts = pd.Series(clean_list).value_counts().reset_index()
                df_counts.columns = ['Number', 'Frequency']
                
                # 2. استشارة Groq AI
                client = Groq(api_key=api_key)
                
                analysis_prompt = f"""
                Role: Professional Paris Turf Analyst.
                Data:
                - Historical Winners: {clean_list}
                - Frequency Map: {df_counts.to_dict(orient='records')}
                - Risk Preference: {risk_level}
                - Target: Predict top {top_n} likely numbers for the next race.

                Instruction:
                Analyze trends (hot numbers, cold numbers, patterns). 
                Provide the top {top_n} numbers as a clear list.
                Give a professional logic reasoning in English (max 3 sentences).
                Finish with: 'Disclaimer: Horse racing involves probability and luck.'
                """

                with st.spinner('جاري معالجة البيانات واستنتاج التوقعات...'):
                    completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": analysis_prompt}],
                        model=model_choice,
                        temperature=0.5
                    )
                    
                    response_text = completion.choices[0].message.content

                    # 3. عرض النتائج
                    st.success("✅ تم التحليل بنجاح")
                    
                    st.markdown("### 🎯 التوقعات والتحليل")
                    st.markdown(f'<div class="prediction-box">{response_text}</div>', unsafe_allow_html=True)
                    
                    # مبيان إحصائي للتردد
                    st.markdown("### 📈 مبيان تكرار الأرقام")
                    st.bar_chart(df_counts.set_index('Number'))

        except Exception as e:
            st.error(f"وقع خطأ غير متوقع: {e}")

st.divider()
st.caption("© 2026 Mouhcine Digital Systems | AI Logic for Strategic Analysis")
