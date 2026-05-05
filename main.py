import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="TRX Permanent Tracker", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    .win { color: #28a745; font-weight: bold; font-size: 25px; }
    .lose { color: #dc3545; font-weight: bold; font-size: 25px; }
    .alert-box { background-color: #ff4b4b; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .prediction-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 2px solid #1f77b4; color: black; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 TRX Permanent Memory Tracker")

# ၁။ CSV ဖိုင်မှ Win Patterns များကို အမြဲတမ်းဖတ်ယူခြင်း
def load_saved_wins():
    if os.path.exists('win_patterns.csv'):
        return pd.read_csv('win_patterns.csv').to_dict('records')
    return []

# Win Pattern ကို ဖိုင်ထဲ အသေသွားမှတ်ခြင်း
def save_win_to_file(pattern_list, result):
    p_str = ",".join(pattern_list)
    new_data = pd.DataFrame([[p_str, result]], columns=['pattern', 'result'])
    if not os.path.exists('win_patterns.csv'):
        new_data.to_csv('win_patterns.csv', index=False)
    else:
        # ရှိပြီးသား pattern ဆို ထပ်မသိမ်းအောင် စစ်မယ်
        existing = pd.read_csv('win_patterns.csv')
        if not ((existing['pattern'] == p_str) & (existing['result'] == result)).any():
            new_data.to_csv('win_patterns.csv', mode='a', header=False, index=False)

# ၂။ Data Loading
@st.cache_data
def load_main_data():
    try:
        df = pd.read_csv('data.csv', usecols=['bs'])
        return df['bs'].astype(str).tolist()
    except: return []

main_data = load_main_data()

# ၃။ Session State (ယာယီမှတ်ဉာဏ်များ)
if 'my_history' not in st.session_state: st.session_state.my_history = []
if 'last_prediction' not in st.session_state: st.session_state.last_prediction = None
if 'score_log' not in st.session_state: st.session_state.score_log = []

# ၄။ Input Section
new_val = st.radio("Choose Result:", ["B", "S"], horizontal=True)

if st.button("ADD RESULT & PREDICT"):
    if st.session_state.last_prediction:
        if st.session_state.last_prediction == new_val:
            st.session_state.score_log.append("WIN ✅")
            # WIN ရင် ဖိုင်ထဲမှာ အသေသွားမှတ်မယ်
            if len(st.session_state.my_history) == 10:
                save_win_to_file(st.session_state.my_history, new_val)
        else:
            st.session_state.score_log.append("LOSE ❌")
            
    st.session_state.my_history.append(new_val)
    if len(st.session_state.my_history) > 10: st.session_state.my_history.pop(0)

# ၅။ Permanent Alert (ဖိုင်ထဲကနေ အမြဲတမ်း စစ်ဆေးခြင်း)
if len(st.session_state.my_history) == 10:
    saved_wins = load_saved_wins()
    current_p_str = ",".join(st.session_state.my_history)
    for sw in saved_wins:
        if sw['pattern'] == current_p_str:
            st.markdown(f"""
                <div class="alert-box">
                    <h2>🔥 WIN PATTERN ALERT!</h2>
                    <p>ဒီ Pattern နဲ့ အရင်က <b>{sw['result']}</b> ထွက်ပြီး နိုင်ဖူးပါတယ်။</p>
                </div>
            """, unsafe_allow_html=True)

# ၆။ UI & Prediction (လက်ရှိအတိုင်း)
st.code(f"Current: {' - '.join(st.session_state.my_history)}")
if len(st.session_state.my_history) == 10:
    m_b, m_s = 0, 0
    for i in range(len(main_data) - 10):
        if main_data[i : i+10] == st.session_state.my_history:
            next_val = main_data[i+10]; 
            if next_val == 'B': m_b += 1 
            else: m_s += 1
    total = m_b + m_s
    if total > 0:
        pred = "B" if m_b > m_s else "S"
        st.session_state.last_prediction = pred
        st.markdown(f'<div class="prediction-box"><b>Next: {pred} ({round(max(m_b,m_s)/total*100, 1)}%)</b></div>', unsafe_allow_html=True)

# ၇။ Results Log
if st.session_state.score_log:
    st.write("---")
    for res in reversed(st.session_state.score_log[-5:]):
        st.markdown(f'<span class="{"win" if "WIN" in res else "lose"}">{res}</span>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Memory Tools")
    saved_count = len(load_saved_wins())
    st.write(f"Permanent Saved Patterns: {saved_count}")
    if st.button("Reset Current Tracker"):
        st.session_state.my_history = []; st.session_state.score_log = []; st.rerun()
