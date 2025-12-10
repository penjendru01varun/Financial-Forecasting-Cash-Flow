# chatbot_backend/main.py

import os
from typing import List
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import google.generativeai as genai

# ---------- Load env & configure Gemini ----------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not configured in .env")

genai.configure(api_key=API_KEY)

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

# Create model with system instruction
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT,
)

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
    history: List[dict] | None = None  # optional: [{"role": "user"/"model", "parts": ["..."]}, ...]


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        history = req.history or []
        chat_session = model.start_chat(history=history)

        result = chat_session.send_message(req.message)
        reply = result.text or ""

        if not reply.strip():
            reply = "I'm not allowed to answer this type of question. Please ask about cash flow or financial forecasting."

        return ChatResponse(reply=reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend error: {str(e)}")
