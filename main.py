import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="TRX Smart Tracker", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    .win { color: #28a745; font-weight: bold; font-size: 24px; }
    .lose { color: #dc3545; font-weight: bold; font-size: 24px; }
    .alert-box { background-color: #ff4b4b; color: white; padding: 20px; border-radius: 10px; text-align: center; animation: pulse 2s infinite; }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
    .prediction-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 2px solid #1f77b4; color: black; }
    </style>
    """, unsafe_allow_html=True)

# ၁။ Data Loading (History & Win Patterns)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv', usecols=['bs'])
        return df['bs'].astype(str).tolist()
    except: return []

# Win Patterns တွေကို ဖိုင်ထဲကနေ ဖတ်မယ်
def get_saved_wins():
    if os.path.exists('win_patterns.csv'):
        return pd.read_csv('win_patterns.csv')
    return pd.DataFrame(columns=['pattern', 'result'])

data_list = load_data()

# ၂။ Session State
if 'my_history' not in st.session_state: st.session_state.my_history = []
if 'last_prediction' not in st.session_state: st.session_state.last_prediction = None
if 'score_log' not in st.session_state: st.session_state.score_log = []

# ၃။ Win Pattern သိမ်းဆည်းတဲ့ Function
def save_win_pattern(pattern_list, result):
    pattern_str = ",".join(pattern_list)
    new_win = pd.DataFrame([[pattern_str, result]], columns=['pattern', 'result'])
    
    if os.path.exists('win_patterns.csv'):
        wins_df = pd.read_csv('win_patterns.csv')
        # ပုံစံတူ ရှိပြီးသားဆိုရင် ထပ်မသိမ်းတော့ဘူး
        if not ((wins_df['pattern'] == pattern_str) & (wins_df['result'] == result)).any():
            new_win.to_csv('win_patterns.csv', mode='a', header=False, index=False)
    else:
        new_win.to_csv('win_patterns.csv', index=False)

# ၄။ Input UI
st.title("🎯 TRX Permanent Win-Pattern Tracker")
new_val = st.radio("အခုထွက်တဲ့ ရလဒ်:", ["B", "S"], horizontal=True)

if st.button("ADD & ANALYZE"):
    # Win/Lose စစ်ဆေးပြီး Win ရင် Pattern ကို သိမ်းမယ်
    if st.session_state.last_prediction:
        if st.session_state.last_prediction == new_val:
            st.session_state.score_log.append("WIN ✅")
            # ရှေ့က Pattern ၁၀ ခုကို သိမ်းမယ်
            if len(st.session_state.my_history) == 10:
                save_win_pattern(st.session_state.my_history, new_val)
        else:
            st.session_state.score_log.append("LOSE ❌")
            
    st.session_state.my_history.append(new_val)
    if len(st.session_state.my_history) > 10: st.session_state.my_history.pop(0)

# ၅။ Pattern Alert Logic
st.write("---")
if len(st.session_state.my_history) == 10:
    current_p_str = ",".join(st.session_state.my_history)
    wins_df = get_saved_wins()
    
    # လက်ရှိ Pattern က Win ဖူးတဲ့ Pattern ထဲမှာ ပါလား စစ်မယ်
    match = wins_df[wins_df['pattern'] == current_p_str]
    if not match.empty:
        win_res = match.iloc[0]['result']
        st.markdown(f"""
            <div class="alert-box">
                <h2>🔥 WIN PATTERN ALERT!</h2>
                <p>ဒီ Pattern က အရင်က နိုင်ဖူးပါတယ်။ နောက်တစ်ခု <b>{win_res}</b> ထွက်ဖို့ များပါတယ်။</p>
            </div>
        """, unsafe_allow_html=True)

# ၆။ လက်ရှိ Sequence နှင့် Prediction
st.code(f"Current: {' - '.join(st.session_state.my_history)}")

if len(st.session_state.my_history) == 10:
    m_b, m_s = 0, 0
    for i in range(len(data_list) - 10):
        if data_list[i : i+10] == st.session_state.my_history:
            next_val = data_list[i+10]
            if next_val == 'B': m_b += 1
            elif next_val == 'S': m_s += 1
    
    total = m_b + m_s
    if total > 0:
        b_per = (m_b/total)*100
        pred = "B" if b_per > 50 else "S"
        st.session_state.last_prediction = pred
        
        st.markdown(f'<div class="prediction-box"><b>Next Prediction: {pred} ({round(max(b_per, 100-b_per), 1)}%)</b></div>', unsafe_allow_html=True)
else:
    st.info(f"Need {10 - len(st.session_state.my_history)} more data...")

# ၇။ Show All Win Patterns (Sidebar)
with st.sidebar:
    st.header("Saved Win Patterns")
    st.dataframe(get_saved_wins(), use_container_width=True)
    if st.button("Clear History"):
        st.session_state.my_history = []; st.session_state.score_log = []; st.rerun()
