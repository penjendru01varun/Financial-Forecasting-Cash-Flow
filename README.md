# MSME Cashflow Agentic Cockpit

An agentic AI system that helps Indian MSMEs forecast short-term cash flow, detect upcoming cash crunches, and get actionable recommendations.

## 🎯 Problem Statement

Indian MSMEs often look profitable on paper but struggle to pay rent, salaries, and suppliers on time because cash inflows and outflows are fragmented across spreadsheets, bank exports, and invoices. They lack tools to forecast short-term cash needs and prevent avoidable cash crunches.

## 💡 Solution

This project is an **agentic cashflow cockpit** that:
- ✅ Ingests recent cashflow data from CSV files
- ✅ Forecasts 4-8 weeks of cashflow based on historical patterns
- ✅ Flags "tight" and "risky" weeks where cash may drop below safe levels
- ✅ Provides MSME-friendly recommendations
- ✅ Includes a chat-based explanation agent powered by LLM

## 🏗️ Architecture

```
                             +-------------------+
   CSV Upload                |  Streamlit UI     |
   (cashflow_sample.csv) --> |  (frontend/app.py)| 
                             +---------+---------+
                                       |
                                       v  HTTP
                             +---------+---------+
                             |   FastAPI Backend |
                             |   (backend/)      |
                             +---------+---------+
                                       |
        +------------------------------+------------------------------+
        |                              |                              |
        v                              v                              v
+---------------+            +-------------------+          +-------------------+
| Ingestion     |            | Forecasting Agent |          |  Explanation/Chat |
| Agent         |            | - Weekly inflow   |          | Agent (LLM)       |
| - Parse CSV   |            | - Weekly outflow  |          | - Takes forecast, |
| - Normalize   |            | - Balance & risk  |          |   alerts, advice  |
+---------------+            +-------------------+          +-------------------+
        |                              |
        v                              v
+---------------+                +---------------+
| Risk & Alert  |                | Advisor Agent |
| Agent         |                | - Actionable  |
| - Tight/risky |                |   suggestions |
|   weeks       |                +---------------+
+---------------+
```

## 🚀 Features

### Multi-Agent System
1. **Data Ingestion Agent** - Parses and normalizes CSV data
2. **Forecasting Agent** - Projects weekly cash flow using historical averages
3. **Risk & Alert Agent** - Identifies high-risk weeks
4. **Advisor Agent** - Generates practical recommendations
5. **Explanation Agent** - Answers natural language questions about forecasts using LLM

### Key Capabilities
- 📊 Visual cash flow forecast dashboard
- ⚠️ Automated risk detection and alerts
- 💡 Actionable business recommendations
- 💬 Interactive chat with AI explanation agent
- 📈 Week-by-week breakdown of inflows/outflows

## 💾 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Step 1: Clone the repository
```bash
git clone https://github.com/penjendru01varun/Financial-Forecasting-Cash-Flow.git
cd Financial-Forecasting-Cash-Flow
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: AI Chatbot Configuration (Pre-configured with 10 API Keys)

The chatbot is pre-configured with 10 API keys for maximum reliability:

**Configured APIs:**
- Jules API
- Gemini API  
- Grok API
- HuggingFace API
- CloudSambanova API
- Massive AI API
- EODHD API
- BrightData API
- OpenRouter API
- AI Studio API

**Intelligent Fallback System:**
The chatbot tries each API in sequence. If one fails (rate limit/credits exhausted), it automatically moves to the next. Only after ALL 10 APIs are exhausted does it fall back to a rule-based system, ensuring **zero downtime**.
### Step 4: Run the backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Step 4b: Run the AI chatbot backend (optional, in a new terminal)

```bash
cd chatbot_backend
uvicorn main:app --reload --port 8001
```

### Step 4c: Run the AI chatbot frontend (optional, in a new terminal)

```bash
cd chatbot_frontend
streamlit run app.py
```

The chatbot will be available on a separate port from the main dashboard.

### Step 5: Run the frontend (in a new terminal)
```bash
cd frontend
streamlit run app.py
```

### Step 6: Open your browser
Go to `http://localhost:8501` and upload the sample CSV from `sample_data/cashflow_sample.csv`

## 📁 Project Structure

```
Financial-Forecasting-Cash-Flow/
├── backend/
│   ├── __init__.py          # Package initializer
│   ├── main.py              # FastAPI server & orchestration
│   ├── models.py            # Pydantic data models
│   ├── agents.py            # Core agent logic
│   └── llm_agent.py         # LLM-powered explanation agent
├── frontend/
│   └── app.py               # Streamlit dashboard UI
├── sample_data/
│   └── cashflow_sample.csv  # Sample MSME cashflow data
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 📊 CSV Format

Your cashflow CSV should have these columns:

```csv
date,description,category,type,amount
2025-10-01,Opening balance,opening,inflow,200000
2025-10-02,Customer invoice #101,sales,inflow,50000
2025-10-03,Office rent,rent,outflow,30000
```

- **date**: Transaction date (YYYY-MM-DD)
- **description**: Transaction description
- **category**: Category (sales, rent, salary, etc.)
- **type**: Either "inflow" or "outflow"
- **amount**: Amount in INR

## 🎬 Demo Usage

1. Upload your cashflow CSV
2. Set initial balance (optional)
3. Choose forecast horizon (4-12 weeks)
4. Click "Run agents"
5. View forecast, alerts, and recommendations
6. Ask questions in the chat agent

## 🏆 Why This Saves MSMEs

- **Early Warning**: Forecasting and risk agents highlight upcoming weeks where cash is likely to fall below a safe buffer, giving owners time to react
- **Concrete Actions**: Advisor agent translates patterns into practical steps like following up on invoices, delaying expenses, or planning short-term finance
- **Clarity Through Conversation**: Explanation agent answers "Why is week 3 risky?" in simple language, helping non-finance founders understand the numbers

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **LLM**: OpenAI GPT-4o-mini
- **Agent Framework**: Custom multi-agent orchestration

## 📝 License

MIT License - Feel free to use this for your hackathon or business!

## 👥 Contributors

- Varun Penjendru (@penjendru01varun)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or collaboration:
- GitHub: [@penjendru01varun](https://github.com/penjendru01varun)
- Project: [Financial-Forecasting-Cash-Flow](https://github.com/penjendru01varun/Financial-Forecasting-Cash-Flow)

---

**Built for Agentathon 2025 Hyderabad** 🚀

*Helping MSMEs survive and thrive through AI-powered cashflow management*
