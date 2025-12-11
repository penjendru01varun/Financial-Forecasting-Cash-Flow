# chatbot_frontend/app.py
import streamlit as st
import requests

# IMPORTANT: Update port to 8001 to match backend
BACKEND_URL = "http://localhost:8001/chat"

st.set_page_config(
    page_title="Cashflow & Forecasting Chatbot",
    page_icon="💸",
    layout="centered"
)

# Custom CSS for improved UI
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        max-width: 900px;
        padding: 2rem 1rem;
    }
    
    /* Title styling */
    h1 {
        color: #1e3a8a;
        text-align: center;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Info text styling */
    .stMarkdown p {
        color: #64748b;
        text-align: center;
    }
    
    /* Chat container card */
    .chat-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* User message */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Assistant message */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: #f8fafc;
        border-left: 4px solid #667eea;
    }
    
    /* Input box styling */
    .stChatInputContainer {
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 5px solid #3b82f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("💸 Cashflow & Financial Forecasting Chatbot")

st.markdown("""
<div class="info-box">
    <strong>🎯 What I can help with:</strong>
    <ul>
        <li>Cash flow analysis and forecasting</li>
        <li>Working capital management</li>
        <li>Budgeting for cash flow</li>
        <li>Liquidity planning strategies</li>
        <li>Financial forecasting for MSMEs</li>
    </ul>
    <em>Note: I only answer questions about cash flow and financial forecasting.</em>
</div>
""", unsafe_allow_html=True)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (sender, text)

# Display chat history
for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.chat_message("user").markdown(msg)
    else:
        st.chat_message("assistant").markdown(msg)

# Chat input
user_input = st.chat_input("💬 Type your cash-flow question...")

if user_input:
    # Add user message to history
    st.session_state.chat_history.append(("You", user_input))
    st.chat_message("user").markdown(user_input)
    
    try:
        # Prepare payload
        payload = {
            "message": user_input,
            "history": [],  # you can enhance this to pass full history
        }
        
        # Show spinner while waiting for response
        with st.spinner("🤔 Analyzing your question..."):
            resp = requests.post(BACKEND_URL, json=payload, timeout=60)
        
        if resp.status_code == 200:
            bot_reply = resp.json().get("reply", "")
        else:
            bot_reply = f"❌ Error from backend: {resp.status_code} - {resp.text}"
            
    except requests.exceptions.ConnectionError:
        bot_reply = "❌ **Connection Error**: Could not connect to the chatbot backend. Please ensure:\n\n1. The backend server is running on port 8001\n2. Run: `cd chatbot_backend && uvicorn main:app --reload --port 8001`"
    except requests.exceptions.Timeout:
        bot_reply = "⏱️ **Timeout Error**: The request took too long. Please try again."
    except Exception as e:
        bot_reply = f"❌ **Request failed**: {str(e)}"
    
    # Add bot reply to history
    st.session_state.chat_history.append(("Bot", bot_reply))
    st.chat_message("assistant").markdown(bot_reply)
    st.rerun()

# Add footer
st.markdown("---")
st.markdown("""
<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>
    💡 Tip: Be specific with your questions for better answers<br/>
    🔒 This chatbot is specialized for financial forecasting only
</p>
""", unsafe_allow_html=True)
