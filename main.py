import streamlit as st
import pandas as pd

st.set_page_config(page_title="TRX Pro Tracker", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    .win { color: #28a745; font-weight: bold; font-size: 25px; }
    .lose { color: #dc3545; font-weight: bold; font-size: 25px; }
    .alert-box { background-color: #ff4b4b; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .prediction-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 2px solid #1f77b4; color: black; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 TRX Live Tracker with Win Alert")

# ၁။ Data Loading
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv', usecols=['bs'])
        return df['bs'].astype(str).tolist()
    except: return []

data_list = load_data()

# ၂။ Session State (Data သိမ်းဆည်းရန်)
if 'my_history' not in st.session_state: st.session_state.my_history = []
if 'last_prediction' not in st.session_state: st.session_state.last_prediction = None
if 'score_log' not in st.session_state: st.session_state.score_log = []
if 'saved_wins' not in st.session_state: st.session_state.saved_wins = [] # Win pattern များမှတ်ရန်

# ၃။ Input Section
st.subheader("ရလဒ်အသစ်ကို ရွေးပြီး Add လုပ်ပါ")
new_val = st.radio("Choose Result:", ["B", "S"], horizontal=True)

if st.button("ADD RESULT & PREDICT"):
    # Win/Lose စစ်ဆေးခြင်း
    if st.session_state.last_prediction:
        if st.session_state.last_prediction == new_val:
            st.session_state.score_log.append("WIN ✅")
            # နိုင်သွားတဲ့ pattern ကို memory ထဲမှာ win pattern အဖြစ်မှတ်မယ်
            current_p = st.session_state.my_history.copy()
            if len(current_p) == 10:
                win_entry = {"pattern": current_p, "result": new_val}
                if win_entry not in st.session_state.saved_wins:
                    st.session_state.saved_wins.append(win_entry)
        else:
            st.session_state.score_log.append("LOSE ❌")
            
    # ရလဒ်အသစ်ကို List ထဲထည့်
    st.session_state.my_history.append(new_val)
    if len(st.session_state.my_history) > 10:
        st.session_state.my_history.pop(0)

# ၄။ Win Alert Logic (လက်ရှိ ၁၀ ခုက Win ဖူးတဲ့ pattern ဖြစ်နေရင်ပြမယ်)
if len(st.session_state.my_history) == 10:
    for saved in st.session_state.saved_wins:
        if saved["pattern"] == st.session_state.my_history:
            st.markdown(f"""
                <div class="alert-box">
                    <h2>🔥 WIN PATTERN ALERT!</h2>
                    <p>ဒီ Pattern နဲ့ အရင်က <b>{saved['result']}</b> ထွက်ပြီး နိုင်ဖူးပါတယ်။</p>
                </div>
            """, unsafe_allow_html=True)

# ၅။ လက်ရှိ Sequence
st.write("---")
st.write(f"**Current Sequence (နောက်ဆုံး {len(st.session_state.my_history)} ခု):**")
st.code(" - ".join(st.session_state.my_history))

# ၆။ Prediction Logic
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
        
        st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
        st.subheader(f"🔮 Next Prediction: {'BIG (B)' if pred == 'B' else 'SMALL (S)'} ({round(max(b_per, 100-b_per), 1)}%)")
        st.write(f"သမိုင်းကြောင်းအရ ဤ Pattern ကို {total} ကြိမ် တွေ့ရှိခဲ့သည်။")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info(f"ခန့်မှန်းချက်ထွက်ရန် နောက်ထပ် {10 - len(st.session_state.my_history)} ခု ထည့်ပေးပါ။")

# ၇။ Win/Lose History Log (အောက်မှာပြန်ပြထားပါတယ်)
if st.session_state.score_log:
    st.write("---")
    st.subheader("Win/Lose Results:")
    for res in reversed(st.session_state.score_log[-10:]):
        if "WIN" in res:
            st.markdown(f'<span class="win">{res}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="lose">{res}</span>', unsafe_allow_html=True)

# Reset & Sidebar
with st.sidebar:
    st.header("Memory")
    st.write(f"Saved Win Patterns: {len(st.session_state.saved_wins)}")
    if st.button("Reset Everything"):
        st.session_state.my_history = []
        st.session_state.last_prediction = None
        st.session_state.score_log = []
        st.session_state.saved_wins = []
        st.rerun()
