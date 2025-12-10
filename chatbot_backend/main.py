# chatbot_backend/main.py

import os
from typing import List
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# ---------- Load env & configure Jules API ----------
load_dotenv()
API_KEY = os.getenv("JULES_API_KEY")

if not API_KEY:
    raise RuntimeError("JULES_API_KEY not configured in .env")

JULES_API_URL = "https://api.jules.ai/v1/chat/completions"

SYSTEM_PROMPT = """
You are a specialized AI Assistant designed ONLY for answering questions related to:
Cash flow
Cash-flow management
Cash-flow forecasting
Financial forecasting
Budgeting related to cash flow
Working capital
Liquidity planning

Your strict rules:
Only respond to cash-flow or financial-forecasting related questions.
If the user asks anything outside these topics, respond with:
"I'm not allowed to answer this type of question. Please ask about cash flow or financial forecasting."
Do NOT behave like ChatGPT.
Do NOT answer questions about programming, general knowledge, personal advice, math, or any other subject.
Keep answers clear, accurate, and professional.
If the question is unclear but related to finance/cashflow, politely ask for clarification.

Your purpose:
To help users understand, analyze, and forecast cash flow and short-term financial performance only.
"""

# ---------- FastAPI app ----------
app = FastAPI(title="Cashflow & Forecasting Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: List[dict] | None = None


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        # Prepare messages for Jules API
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history if provided
        if req.history:
            for msg in req.history:
                messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": req.message})
        
        # Call Jules API
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "jules-v1",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(JULES_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not reply.strip():
                reply = "I'm not allowed to answer this type of question. Please ask about cash flow or financial forecasting."
        else:
            reply = f"API Error: {response.status_code} - {response.text}"

        return ChatResponse(reply=reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend error: {str(e)}")
