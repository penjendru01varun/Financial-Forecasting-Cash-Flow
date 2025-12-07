import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="MSME Cashflow Agent", layout="wide")
st.title("MSME Cashflow Agentic Cockpit")

st.markdown(
    "Upload your recent cashflow CSV (columns: `date`, `description`, `category`, `type`, `amount`) "
    "and the agents will forecast your next 4–8 weeks and highlight risks."
)

with st.sidebar:
    st.header("Forecast settings")
    initial_balance = st.number_input("Current cash balance (optional)", value=0.0, step=1000.0)
    initial_provided = st.checkbox("Use this as initial balance", value=False)
    horizon_weeks = st.slider("Forecast horizon (weeks)", min_value=4, max_value=12, value=8)

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    if st.button("Run agents"):
        with st.spinner("Running agents and generating forecast..."):
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
                st.error(f"Error contacting backend: {e}")
            else:
                if resp.status_code != 200:
                    st.error(f"Backend error: {resp.status_code} – {resp.text}")
                else:
                    result = resp.json()

                    st.subheader("Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Initial balance", f"₹{result['initial_balance']:.2f}")
                    with col2:
                        st.metric("Recommended buffer", f"₹{result['buffer_amount']:.2f}")
                    with col3:
                        risky_weeks = [
                            p for p in result["points"] if p["risk_level"] == "risky"
                        ]
                        st.metric("High-risk weeks", len(risky_weeks))

                    st.subheader("Weekly forecast")
                    df_points = pd.DataFrame(result["points"])
                    st.dataframe(df_points)

                    st.line_chart(
                        df_points.set_index("week_start")[["projected_balance"]],
                        use_container_width=True,
                    )

                    st.subheader("Alerts")
                    if result["alerts"]:
                        for a in result["alerts"]:
                            st.warning(a)
                    else:
                        st.success("No major cashflow risks detected in the forecast horizon.")

                    st.subheader("Advisor recommendations")
                    for r in result["recommendations"]:
                        st.info("• " + r)

                    st.subheader("Chat with the explanation agent")
                    if "chat_history" not in st.session_state:
                        st.session_state["chat_history"] = []

                    user_q = st.text_input("Ask a question about your cash flow (e.g., 'Why is week 3 risky?')")

                    if st.button("Ask"):
                        if not user_q.strip():
                            st.warning("Please type a question.")
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
                                chat_resp = requests.post(f"{BACKEND_URL}/api/chat", json=chat_payload, timeout=60)
                                if chat_resp.status_code != 200:
                                    st.error(f"Chat backend error: {chat_resp.status_code} – {chat_resp.text}")
                                else:
                                    answer = chat_resp.json()["answer"]
                                    st.session_state["chat_history"].append(("You", user_q))
                                    st.session_state["chat_history"].append(("Agent", answer))
                            except Exception as e:
                                st.error(f"Error contacting chat agent: {e}")

                    if st.session_state["chat_history"]:
                        for speaker, text in st.session_state["chat_history"]:
                            if speaker == "You":
                                st.markdown(f"**You:** {text}")
                            else:
                                st.markdown(f"**Agent:** {text}")
else:
    st.info("Upload a cashflow CSV to get started.")
