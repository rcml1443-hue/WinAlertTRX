import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="TRX Ultimate Predictor", layout="wide")

# Styling
st.markdown("""
    <style>
    .win { color: #28a745; font-weight: bold; font-size: 25px; }
    .lose { color: #dc3545; font-weight: bold; font-size: 25px; }
    .alert-box { background-color: #ff4b4b; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 3px solid white; }
    .prediction-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 2px solid #1f77b4; color: black; }
    .martingale { background-color: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107; color: #856404; }
    </style>
    """, unsafe_allow_html=True)

# ၁။ Data Loading
def load_saved_wins():
    if os.path.exists('win_patterns.csv'):
        try: return pd.read_csv('win_patterns.csv').to_dict('records')
        except: return []
    return []

def save_win_to_file(pattern_list, result):
    p_str = ",".join(pattern_list)
    new_data = pd.DataFrame([[p_str, result]], columns=['pattern', 'result'])
    if not os.path.exists('win_patterns.csv'):
        new_data.to_csv('win_patterns.csv', index=False)
    else:
        existing = pd.read_csv('win_patterns.csv')
        if not ((existing['pattern'] == p_str) & (existing['result'] == result)).any():
            new_data.to_csv('win_patterns.csv', mode='a', header=False, index=False)

@st.cache_data
def load_main_data():
    try:
        df = pd.read_csv('data.csv', usecols=['bs'])
        return df['bs'].astype(str).tolist()
    except: return []

main_data = load_main_data()

# ၂။ Session States
if 'my_history' not in st.session_state: st.session_state.my_history = []
if 'last_prediction' not in st.session_state: st.session_state.last_prediction = None
if 'score_log' not in st.session_state: st.session_state.score_log = []
if 'm_step' not in st.session_state: st.session_state.m_step = 1 # Martingale Step

st.title("🛡️ TRX Ultimate Predictor Pro")

# ၃။ Input Section
new_val = st.radio("Next Result:", ["B", "S"], horizontal=True)

if st.button("ADD & DEEP ANALYZE"):
    if st.session_state.last_prediction:
        if st.session_state.last_prediction == new_val:
            st.session_state.score_log.append("WIN ✅")
            if len(st.session_state.my_history) == 10:
                save_win_to_file(st.session_state.my_history, new_val)
            st.session_state.m_step = 1 # နိုင်ရင် အစပြန်စ
        else:
            st.session_state.score_log.append("LOSE ❌")
            st.session_state.m_step += 1 # ရှုံးရင် အဆတိုး

    st.session_state.my_history.append(new_val)
    if len(st.session_state.my_history) > 10: st.session_state.my_history.pop(0)

# ၄။ Multi-Length Analysis Logic
def get_prediction(history, data, length):
    if len(history) < length: return None, 0
    pattern = history[-length:]
    m_b, m_s = 0, 0
    for i in range(len(data) - length):
        if data[i : i+length] == pattern:
            if data[i+length] == 'B': m_b += 1
            else: m_s += 1
    total = m_b + m_s
    if total == 0: return None, 0
    prob = (m_b/total)*100
    return ('B', prob) if prob >= 50 else ('S', 100-prob)

# ၅။ UI Display
if len(st.session_state.my_history) >= 10:
    # Permanent Win Alert
    saved_wins = load_saved_wins()
    current_p_str = ",".join(st.session_state.my_history)
    for sw in saved_wins:
        if sw['pattern'] == current_p_str:
            st.markdown(f'<div class="alert-box"><h2>🔥 WIN PATTERN ALERT!</h2><p>Past Result: {sw["result"]}</p></div>', unsafe_allow_html=True)

    # Deep Analysis Results
    st.subheader("📊 Multi-Length Analysis")
    c1, c2, c3 = st.columns(3)
    p3, pr3 = get_prediction(st.session_state.my_history, main_data, 3)
    p5, pr5 = get_prediction(st.session_state.my_history, main_data, 5)
    p10, pr10 = get_prediction(st.session_state.my_history, main_data, 10)

    c1.metric("3-Step Pattern", f"{p3} ({round(pr3,1)}%)")
    c2.metric("5-Step Pattern", f"{p5} ({round(pr5,1)}%)")
    c3.metric("10-Step Pattern", f"{p10} ({round(pr10,1)}%)")

    # Final Recommendation
    st.divider()
    final_pred = p10 # Default to 10-step
    st.session_state.last_prediction = final_pred
    
    st.markdown(f'<div class="prediction-box"><h3>🔮 Final Recommendation: {final_pred}</h3></div>', unsafe_allow_html=True)

    # Martingale Advisor
    steps = [1, 3, 8, 24, 70, 200] # 3x Strategy
    current_amt = steps[st.session_state.m_step-1] if st.session_state.m_step <= 6 else "MAX"
    st.markdown(f'<div class="martingale">💰 <b>Martingale Advice:</b> Step {st.session_state.m_step} -> ထိုးရမည့်အဆ: <b>{current_amt}x</b></div>', unsafe_allow_html=True)

st.write(f"**Current:** {' - '.join(st.session_state.my_history)}")

# ၆။ History Log
if st.session_state.score_log:
    st.subheader("Recent Results")
    for res in reversed(st.session_state.score_log[-5:]):
        st.markdown(f'<span class="{"win" if "WIN" in res else "lose"}">{res}</span>', unsafe_allow_html=True)

with st.sidebar:
    if st.button("Reset Everything"):
        st.session_state.my_history = []; st.session_state.score_log = []; st.session_state.m_step = 1; st.rerun()
