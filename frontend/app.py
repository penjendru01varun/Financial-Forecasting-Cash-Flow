import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BACKEND_URL = "http://localhost:8000"

# === CUSTOM CSS FOR THEMES AND BETTER UI ===
def apply_custom_css():
    st.markdown("""
    <style>
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #1e3a8a, #1e40af, #3b82f6, #60a5fa);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Card-style containers */
    .card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Chatbot container */
    .chat-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        max-height: 500px;
        overflow-y: auto;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }
    
    /* Chat messages */
    .user-message {
        background: #3b82f6;
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 5px 18px;
        margin: 10px 0;
        display: inline-block;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .bot-message {
        background: #e5e7eb;
        color: #1f2937;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 5px;
        margin: 10px 0;
        display: inline-block;
        max-width: 80%;
        float: left;
        clear: both;
    }
    
    /* Improved metrics */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #1e40af;
    }
    
    /* Better headers */
    h1, h2, h3 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(30, 58, 138, 0.95);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid;
    }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="MSME Cashflow Agent", layout="wide", initial_sidebar_state="expanded")
apply_custom_css()

st.title("💰 MSME Cashflow AI Cockpit")
st.markdown(
    """<div style='background: rgba(255, 255, 255, 0.9); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
    <p style='color: #1e40af; margin: 0; font-size: 16px;'>

    Upload your cashflow CSV (columns: <code>date</code>, <code>description</code>, <code>category</code>, 
    <code>type</code>, <code>amount</code>) and let our AI agents forecast your next 4–12 weeks and highlight risks.
    </p></div>""",
    unsafe_allow_html=True
)

with st.sidebar:
    st.header("⚙️ Forecast Settings")
    initial_balance = st.number_input("💵 Current cash balance (optional)", value=0.0, step=1000.0)
    initial_provided = st.checkbox("Use this as initial balance", value=False)
    horizon_weeks = st.slider("📅 Forecast horizon (weeks)", min_value=4, max_value=12, value=8)
    st.markdown("---")
    st.markdown("### 🎨 Theme")
    st.info("Animated gradient background active")

uploaded_file = st.file_uploader("📂 Upload CSV file", type=["csv"])

if uploaded_file is not None:    if st.button("🚀 Run AI Agents"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            data = {"horizon_weeks": str(horizon_weeks)}
            if initial_provided:
                data["initial_balance"] = str(initial_balance)

            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/forecast",
                    files=files,
                    data=data,
                    timeout=120,
                )
            except Exception as e:
                st.error(f"❌ Error contacting backend: {e}")
            else:
                if resp.status_code != 200:
                    st.error(f"❌ Backend error: {resp.status_code} – {resp.text}")
                else:
                    result = resp.json()
                    
                    # Store result in session state for chatbot
                    st.session_state["forecast_result"] = result
                    
                    # === SUMMARY SECTION ===
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader("📊 Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("💰 Initial Balance", f"₹{result['initial_balance']:.2f}")
                    with col2:
                        st.metric("🛡️ Recommended Buffer", f"₹{result['buffer_amount']:.2f}")
                    with col3:
                        risky_weeks = [p for p in result["points"] if p["risk_level"] == "risky"]
                        st.metric("⚠️ High-Risk Weeks", len(risky_weeks))
                    st.markdown("</div>", unsafe_allow_html=True)

                    # === WEEKLY FORECAST ===
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader("📈 Weekly Forecast")
                    df_points = pd.DataFrame(result["points"])
                    
                    # Add color coding for risk levels
                    def highlight_risk(row):
                        if row['risk_level'] == 'risky':
                            return ['background-color: #fee2e2'] * len(row)
                        elif row['risk_level'] == 'tight':
                            return ['background-color: #fef3c7'] * len(row)
                        else:
                            return ['background-color: #d1fae5'] * len(row)
                    
                    st.dataframe(df_points.style.apply(highlight_risk, axis=1), use_container_width=True)
                    st.line_chart(
                        df_points.set_index("week_start")[["projected_balance"]],
                        use_container_width=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                                # === COMPREHENSIVE VISUALIZATIONS ===
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📊 Comprehensive Charts & Analysis")
            
            # Create tabs for different chart types
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Line & Area", "📊 Bar Charts", "🥧 Pie Charts", "📉 Heatmap"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Cash Flow Trend (Line Chart)**")
                    fig_line = px.line(df_points, x='week_start', y='projected_balance', 
                                      title='Projected Cash Balance Over Time',
                                      markers=True)
                    fig_line.update_traces(line_color='#3b82f6', line_width=3)
                    st.plotly_chart(fig_line, use_container_width=True)
                
                with col2:
                    st.markdown("**Cash Flow Area Chart**")
                    fig_area = px.area(df_points, x='week_start', y='projected_balance',
                                      title='Cash Balance Accumulation')
                    fig_area.update_traces(fillcolor='rgba(59, 130, 246, 0.3)', line_color='#3b82f6')
                    st.plotly_chart(fig_area, use_container_width=True)
            
            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Weekly Balance (Bar Chart)**")
                    fig_bar = px.bar(df_points, x='week_start', y='projected_balance',
                                    title='Weekly Projected Balance',
                                    color='risk_level',
                                    color_discrete_map={'safe': '#10b981', 'tight': '#f59e0b', 'risky': '#ef4444'})
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    st.markdown("**Risk Level Distribution**")
                    risk_summary = df_points['risk_level'].value_counts().reset_index()
                    risk_summary.columns = ['Risk Level', 'Weeks']
                    fig_risk_bar = px.bar(risk_summary, x='Risk Level', y='Weeks',
                                         title='Number of Weeks by Risk',
                                         color='Risk Level',
                                         color_discrete_map={'safe': '#10b981', 'tight': '#f59e0b', 'risky': '#ef4444'})
                    st.plotly_chart(fig_risk_bar, use_container_width=True)
            
            with tab3:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Risk Level Pie Chart**")
                    risk_counts = df_points['risk_level'].value_counts().reset_index()
                    risk_counts.columns = ['Risk Level', 'Count']
                    fig_pie = px.pie(risk_counts, values='Count', names='Risk Level',
                                    title='Weeks by Risk Level',
                                    color='Risk Level',
                                    color_discrete_map={'safe': '#10b981', 'tight': '#f59e0b', 'risky': '#ef4444'})
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    st.markdown("**Balance Range (Donut Chart)**")
                    df_points['Balance Range'] = pd.cut(df_points['projected_balance'], 
                                                       bins=[-float('inf'), 0, 50000, 100000, float('inf')],
                                                       labels=['Negative', 'Low (<50K)', 'Medium (50-100K)', 'High (>100K)'])
                    balance_dist = df_points['Balance Range'].value_counts().reset_index()
                    balance_dist.columns = ['Range', 'Count']
                    fig_donut = px.pie(balance_dist, values='Count', names='Range',
                                      title='Balance Distribution', hole=0.4)
                    st.plotly_chart(fig_donut, use_container_width=True)
            
            with tab4:
                st.markdown("**Risk Intensity Heatmap**")
                risk_score_map = {'safe': 1, 'tight': 2, 'risky': 3}
                df_points['Risk Score'] = df_points['risk_level'].map(risk_score_map)
                fig_heat = px.imshow([df_points['Risk Score'].values],
                                    labels=dict(x="Week", y="Risk", color="Risk Level"),
                                    x=df_points['week_start'],
                                    y=['Cash Flow Risk'],
                                    color_continuous_scale=[[0, '#10b981'], [0.5, '#f59e0b'], [1, '#ef4444']],
                                    title='Cash Flow Risk Heatmap Over Time')
                st.plotly_chart(fig_heat, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

                    # === ALERTS ===
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader("🚨 Alerts")
                    if result["alerts"]:
                        for a in result["alerts"]:
                            st.warning(f"⚠️ {a}")
                    else:
                        st.success("✅ No major cashflow risks detected in the forecast horizon.")
                    st.markdown("</div>", unsafe_allow_html=True)

                    # === ADVISOR RECOMMENDATIONS ===
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader("💡 Advisor Recommendations")
                    for idx, r in enumerate(result["recommendations"], 1):
                        st.info(f"{idx}. {r}")
                    st.markdown("</div>", unsafe_allow_html=True)

                    # === AI CHATBOT ===
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader("🤖 AI Cashflow Assistant")
                    st.markdown("<p style='color: #6b7280;'>Ask me anything about your cashflow forecast!</p>", unsafe_allow_html=True)
                    
                    if "chat_history" not in st.session_state:
                        st.session_state["chat_history"] = []

                    # Chat history display
                    if st.session_state["chat_history"]:
                        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
                        for speaker, text in st.session_state["chat_history"]:
                            if speaker == "You":
                                st.markdown(f"<div class='user-message'><strong>You:</strong> {text}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div class='bot-message'><strong>🤖 AI:</strong> {text}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Chat input
                    col_input, col_btn = st.columns([4, 1])
                    with col_input:
                        user_q = st.text_input(
                            "Your question",
                            placeholder="e.g., Why is week 3 risky? What should I do?",
                            label_visibility="collapsed"
                        )
                    with col_btn:
                        ask_button = st.button("💬 Ask")
                    
                    if ask_button:
                        if not user_q.strip():
                            st.warning("⚠️ Please type a question.")
                        else:
                            chat_payload = {
                                "question": user_q,
                                "initial_balance": result["initial_balance"],
                                "buffer_amount": result["buffer_amount"],
                                "points": result["points"],
                                "alerts": result["alerts"],
                                "recommendations": result["recommendations"],
                            }
                            try:
                                with st.spinner("🤔 AI is thinking..."):
                                    chat_resp = requests.post(f"{BACKEND_URL}/api/chat", json=chat_payload, timeout=60)
                                if chat_resp.status_code != 200:
                                    st.error(f"❌ Chat backend error: {chat_resp.status_code} – {chat_resp.text}")
                                else:
                                    answer = chat_resp.json()["answer"]
                                    st.session_state["chat_history"].append(("You", user_q))
                                    st.session_state["chat_history"].append(("AI", answer))
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error contacting chat agent: {e}")
                    
                    if st.button("🗑️ Clear Chat History"):
                        st.session_state["chat_history"] = []
                        st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("👆 Upload a cashflow CSV file to get started!")
    st.markdown("""
    <div style='background: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 10px; margin-top: 20px;'>
        <h3 style='color: #1e40af;'>📋 CSV Format Example</h3>
        <p style='color: #374151;'>Your CSV should contain these columns:</p>
        <ul style='color: #374151;'>
            <li><code>date</code> - Transaction date (YYYY-MM-DD)</li>
            <li><code>description</code> - Transaction description</li>
            <li><code>category</code> - Category name</li>
            <li><code>type</code> - Either "inflow" or "outflow"</li>
            <li><code>amount</code> - Transaction amount</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
