# chatbot_backend/main.py
import os
from typing import List
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# ---------- Load env & configure Multiple API Keys ----------
load_dotenv()

# Load all 10 API keys
JULES_API_KEY = "AQ.Ab8RN6J6o9KezfmPy4wIXqBkx7nbWu7D7W6jINL225QkHSfe2Q"
GEMINI_API_KEY = "AIzaSyDBHuMSNGNZsjtoSCcRoH_eHze6BLYzIMU"
GROK_API_KEY = "xai-KZqZ1JdB2I0NbGwiSGa6xYCnEFrcZu6jpmigNpwCeMOWz6oz3iuEgX7sZQ6xdYieVt36QZpEJZwPFF5Y"
HUGGINGFACE_API_KEY = "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"
CLOUDSAMBANOVA_API_KEY = "cbb82fb7-0558-40af-997f-9e71cdf28a4f"
MASSIVEAI_API_KEY = "xnZCyPNL51vXAs7JjjyIIJDnYxnOCdNA"
EODHD_API_KEY = "693a6ad70abd12.88277264"
BRIGHTDATA_API_KEY = "929ae03c6501f4d0d86caeb542ea61480ccd2d98553a569091ffa7ecd82e4c53"
OPENROUTER_API_KEY = "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"
AISTUDIO_API_KEY = "AIzaSyAoes5DTIp-FKE7VbOcoEBW9fktmRGbfks"

# API endpoints
JULES_API_URL = "https://jules.googleapis.com/v1alpha/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
AISTUDIO_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

SYSTEM_PROMPT = """
You are a specialized AI Assistant designed ONLY for answering questions related to:
- Cash flow
- Cash-flow management
- Cash-flow forecasting
- Financial forecasting
- Budgeting related to cash flow
- Working capital
- Liquidity planning

Your strict rules:
1. Only respond to cash-flow or financial-forecasting related questions.
2. If a question is NOT about these topics, politely decline and remind the user of your purpose.
3. Be helpful, concise, and professional.
4. Provide actionable insights when possible.
"""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: List = []

class ChatResponse(BaseModel):
    reply: str


# ---------- 20 SAMPLE Q&A PAIRS FOR CASH FLOW ----------
SAMPLE_QA = {
    "what is cash flow": "Cash flow is the movement of money into and out of your business. Positive cash flow means more money coming in than going out, while negative cash flow indicates more outflows than inflows. It's crucial for business survival.",
    
    "how to forecast cash flow": "To forecast cash flow: 1) Track all income sources, 2) List all expenses (fixed and variable), 3) Project future sales, 4) Estimate payment timelines, 5) Calculate net cash flow = inflows - outflows for each period (weekly/monthly), 6) Monitor and adjust regularly.",
    
    "what is working capital": "Working capital = Current Assets - Current Liabilities. It represents the funds available for day-to-day operations. Positive working capital means you can cover short-term obligations. For MSMEs, maintaining 2-3 months of operating expenses as working capital is recommended.",
    
    "cash flow vs profit": "Profit is revenue minus expenses on paper. Cash flow is actual money movement. You can be profitable but cash-poor if customers haven't paid yet. Cash flow focuses on timing of receipts and payments, while profit ignores timing.",
    
    "how to improve cash flow": "5 ways to improve cash flow: 1) Invoice promptly and follow up on payments, 2) Negotiate better payment terms with suppliers, 3) Reduce unnecessary expenses, 4) Offer discounts for early payments, 5) Maintain a cash reserve for emergencies.",
    
    "what is liquidity": "Liquidity is your ability to convert assets to cash quickly. High liquidity means you can easily access cash for immediate needs. The current ratio (current assets / current liabilities) and quick ratio measure liquidity. MSMEs should aim for a current ratio of 1.5-2.0.",
    
    "what causes cash flow problems": "Common causes: 1) Late customer payments, 2) Overstocking inventory, 3) Unexpected expenses, 4) Seasonal sales fluctuations, 5) Too much debt, 6) Rapid growth without planning, 7) Poor financial tracking.",
    
    "cash inflow sources": "Main cash inflows: 1) Sales revenue, 2) Customer payments, 3) Loans/financing, 4) Investment from owners, 5) Asset sales, 6) Interest income, 7) Government grants or subsidies. Track each source separately for better forecasting.",
    
    "cash outflow types": "Main cash outflows: 1) Supplier payments, 2) Salaries and wages, 3) Rent and utilities, 4) Loan repayments, 5) Tax payments, 6) Equipment purchases, 7) Marketing expenses. Categorize as fixed or variable for budgeting.",
    
    "what is break even point": "Break-even point is when total revenue equals total costs (no profit, no loss). Formula: Fixed Costs / (Price per Unit - Variable Cost per Unit). Knowing this helps plan minimum sales needed to cover costs.",
    
    "weekly vs monthly forecasting": "Weekly forecasting is better for: tight cash positions, seasonal businesses, rapid growth. Monthly is sufficient for: stable operations, predictable cash flows. MSMEs with cash concerns should forecast weekly for next 8-12 weeks.",
    
    "cash flow statement sections": "3 sections: 1) Operating Activities (day-to-day business), 2) Investing Activities (buying/selling assets), 3) Financing Activities (loans, equity). Net change = sum of all three. This shows where cash comes from and goes.",
    
    "how much cash reserve needed": "MSMEs should maintain 2-3 months of operating expenses as cash reserve. This covers: unexpected costs, slow sales periods, late payments. Calculate monthly burn rate (expenses) and multiply by 2-3.",
    
    "payment terms impact": "Payment terms directly affect cash flow timing. If you give 30-day terms but suppliers demand 15 days, you face a gap. Align receivables (shorter) and payables (longer) to maintain positive flow. Offer 2/10 net 30 (2% discount if paid in 10 days).",
    
    "seasonal cash flow": "Many businesses face seasonal peaks and valleys. Solution: 1) Forecast based on last year's pattern, 2) Build cash reserve during peak season, 3) Arrange credit line for slow months, 4) Diversify revenue streams, 5) Plan expenses around cash availability.",
    
    "cash deficit meaning": "Cash deficit = when cash outflows exceed inflows in a period. You don't have enough money to pay bills. Solutions: 1) Delay non-essential expenses, 2) Speed up collections, 3) Use credit line, 4) Negotiate payment extensions, 5) Inject owner funds.",
    
    "cash surplus management": "Cash surplus = excess cash after meeting obligations. Smart uses: 1) Pay down high-interest debt, 2) Invest in growth opportunities, 3) Build emergency fund, 4) Short-term investments, 5) Negotiate early payment discounts with suppliers.",
    
    "accounts receivable management": "Receivables = money customers owe you. Tips: 1) Invoice immediately, 2) Set clear payment terms, 3) Follow up on overdue accounts, 4) Offer early payment incentives, 5) Consider factoring for urgent needs. Aim for Days Sales Outstanding (DSO) < 45 days.",
    
    "funding options for cash shortage": "Short-term options: 1) Business line of credit, 2) Invoice factoring, 3) Short-term loans, 4) Merchant cash advance, 5) Trade credit. Long-term: equity investment, term loans. Choose based on urgency, cost, and repayment ability.",
    
    "cash flow monitoring frequency": "MSMEs should: 1) Check bank balance daily, 2) Review weekly cash flow statement, 3) Update forecasts weekly, 4) Compare actual vs projected monthly, 5) Adjust strategy quarterly. Use accounting software to automate tracking."
}

# Rule-based fallback responses
FALLBACK_RESPONSES = {
    "cash flow": "Cash flow refers to the movement of money in and out of your business. Positive cash flow means more money coming in than going out, which is essential for business sustainability.",
    "forecast": "Financial forecasting involves predicting future cash flows based on historical data, trends, and business plans. This helps businesses prepare for upcoming expenses and revenue.",
    "working capital": "Working capital is the difference between current assets and current liabilities. It represents the funds available for day-to-day operations.",
    "budget": "Budgeting for cash flow involves planning your expected income and expenses over a period to ensure you have enough cash to meet obligations.",
    "liquidity": "Liquidity refers to how easily assets can be converted to cash. High liquidity means you can quickly access cash for immediate needs.",
    "msme": "MSMEs (Micro, Small, and Medium Enterprises) often face cash flow challenges. Proper forecasting can help identify tight periods and plan accordingly.",
}

def get_fallback_response(question: str) -> str:
    """Generate a rule-based response based on keywords"""
    question_lower = question.lower()
    
    # Check for financial/cashflow related keywords
    cashflow_keywords = ["cash", "flow", "forecast", "financial", "budget", "capital", "liquidity", "msme", "money", "revenue", "expense", "income"]
    
    is_relevant = any(keyword in question_lower for keyword in cashflow_keywords)
    
    if not is_relevant:
        return "I'm specialized in financial forecasting and cash flow management. Please ask questions related to cash flow, forecasting, budgeting, working capital, or liquidity planning."
    
    # Find best matching response
    for keyword, response in FALLBACK_RESPONSES.items():
        if keyword in question_lower:
            return response
    
    # Generic relevant response
    return "For cash flow and financial forecasting questions, I recommend: 1) Track all income and expenses regularly, 2) Create monthly cash flow projections, 3) Identify seasonal patterns, 4) Maintain a cash reserve for emergencies. What specific aspect would you like to know more about?"

def call_jules_api(message: str) -> str:
    """Try Jules API first"""
    try:
        headers = {"Authorization": f"Bearer {JULES_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "jules-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7
        }
        response = requests.post(JULES_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("choices", [])[0].get("message", {}).get("content", "")
    except:
        pass
    return None

def call_gemini_api(message: str) -> str:
    """Try Gemini API"""
    try:
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser: {message}"}]
            }]
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "")
    except:
        pass
    return None

def call_grok_api(message: str) -> str:
    """Try Grok API"""
    try:
        headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
        }
        response = requests.post(GROK_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("choices", [])[0].get("message", {}).get("content", "")
    except:
        pass
    return None

def call_huggingface_api(message: str) -> str:
    """Try HuggingFace API"""
    try:
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {"inputs": f"{SYSTEM_PROMPT}\n\nUser: {message}\nAssistant:"}
        response = requests.post(HUGGINGFACE_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").split("Assistant:")[-1].strip()
    except:
        pass
    return None

def call_openrouter_api(message: str) -> str:
    """Try OpenRouter API"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
        }
        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("choices", [])[0].get("message", {}).get("content", "")
    except:
        pass
    return None

def call_aistudio_api(message: str) -> str:
    """Try AI Studio API (Google)"""
    try:
        url = f"{AISTUDIO_API_URL}?key={AISTUDIO_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser: {message}"}]
            }]
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "")
    except:
        pass
    return None


def check_sample_qa(message: str) -> str:
    """Check if message matches any sample Q&A"""
    message_lower = message.lower().strip()
    
    # Direct match
    if message_lower in SAMPLE_QA:
        return SAMPLE_QA[message_lower]
    
    # Partial match - find best matching question
    for question, answer in SAMPLE_QA.items():
        if question in message_lower or message_lower in question:
            return answer
    
    return None


def check_greeting(message: str) -> str:
    """Check if message is a greeting and return appropriate response"""
    message_lower = message.lower().strip()
    
    # Greetings
    greetings = ["hi", "hello", "hey", "hii", "helo", "hola"]
    if any(message_lower == greeting for greeting in greetings):
        return "Hello! I'm CashFlowAI, your financial forecasting assistant. I specialize in cash flow management, budgeting, liquidity analysis, and working capital planning for small businesses. How can I help you today?"    
    # Goodbye
    goodbyes = ["bye", "goodbye", "see you", "byee", "bbye"]
    if any(goodbye in message_lower for goodbye in goodbyes):
        return "Goodbye! Feel free to return anytime you need help with cash flow forecasting or financial planning. Have a great day!"    
    return None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with cascading fallback through all 10 APIs,
    then fallback to rule-based system if all APIs fail.
    """
    user_message = request.message
    
    # Check for greetings first
    greeting_response = check_greeting(user_message)
    if greeting_response:
        return ChatResponse(reply=greeting_response)

        # Check for sample Q&A match
    sample_response = check_sample_qa(user_message)
    if sample_response:
        return ChatResponse(reply=sample_response)

    
    # Try all APIs in sequence
    apis = [
        ("Jules", call_jules_api),
        ("Gemini", call_gemini_api),
        ("Grok", call_grok_api),
        ("HuggingFace", call_huggingface_api),
        ("OpenRouter", call_openrouter_api),
        ("AI Studio", call_aistudio_api),
    ]
    
    for api_name, api_function in apis:
        try:
            response = api_function(user_message)
            if response:
                return ChatResponse(reply=response)
        except Exception as e:
            print(f"{api_name} API failed: {str(e)}")
            continue
    
    # If all APIs fail, use rule-based fallback
    fallback_reply = get_fallback_response(user_message)
    return ChatResponse(reply=fallback_reply)

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Chatbot API with 10 APIs + rule-based fallback"}
