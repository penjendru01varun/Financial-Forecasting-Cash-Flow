# chatbot_frontend/app.py

import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="Cashflow & Forecasting Chatbot")

st.title("💸 Cashflow & Financial Forecasting Chatbot")
st.write(
    "Ask questions only about cash flow, cash‑flow forecasting, budgeting for cash, "
    "working capital, and liquidity planning."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (sender, text)

user_input = st.chat_input("Type your cash-flow question...")

if user_input:
    st.session_state.chat_history.append(("You", user_input))

    try:
        payload = {
            "message": user_input,
            "history": [],  # you can later pass real history if you want multi-turn
        }
        resp = requests.post(BACKEND_URL, json=payload, timeout=60)
        if resp.status_code == 200:
            bot_reply = resp.json().get("reply", "")
        else:
            bot_reply = f"Error from backend: {resp.status_code} - {resp.text}"
    except Exception as e:
        bot_reply = f"Request failed: {e}"

    st.session_state.chat_history.append(("Bot", bot_reply))

for sender, msg in st.session_state.chat_history:
    if sender == "You":
        st.chat_message("user").markdown(msg)
    else:
        st.chat_message("assistant").markdown(msg)
