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

# Load all available API keys
JULES_API_KEY = os.getenv("JULES_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROK_API_KEY = os.getenv("GROK_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# API endpoints
JULES_API_URL = "https://jules.googleapis.com/v1alpha/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"

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
2. If the user asks anything outside these topics, respond with:
   "I'm not allowed to answer this type of question. Please ask about cash flow or financial forecasting."
3. Do NOT behave like ChatGPT.
4. Do NOT answer questions about programming, general knowledge, personal advice, math, or any other subject.
5. Keep answers clear, accurate, and professional.
6. If the question is unclear but related to finance/cashflow, politely ask for clarification.

Your purpose:
To help users understand, analyze, and forecast cash flow and short-term financial performance only.
"""

# ---------- Helper function to handle greetings ----------
def handle_greeting(message: str) -> str:
    """Handle simple greetings"""
    msg_lower = message.lower().strip()
    
    if msg_lower in ["hi", "hello", "hey", "hii", "helo"]:
        return "Hi there, how are you! 😊 I'm here to help you with cash flow and financial forecasting questions."
    elif msg_lower in ["bye", "goodbye", "see you", "byebye"]:
        return "Bye! See you next time. Feel free to come back for any cashflow or forecasting questions! 👋"
    elif msg_lower in ["how are you", "how are you?", "how r u"]:
        return "I'm doing great, thank you for asking! How can I help you with cash flow or financial forecasting today?"
    
    return None

# ---------- API calling functions with fallback ----------
def try_jules_api(messages: List[dict]) -> str:
    """Try Jules API"""
    if not JULES_API_KEY:
        return None
    
    try:
        headers = {
            "X-Goog-Api-Key": JULES_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gemini-pro",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        response = requests.post(JULES_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            if reply.strip():
                return reply
        return None
    except:
        return None

def try_gemini_api(messages: List[dict]) -> str:
    """Try Google Gemini API"""
    if not GEMINI_API_KEY:
        return None
    
    try:
        # Combine messages into a single prompt
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if reply.strip():
                return reply
        return None
    except:
        return None

def try_grok_api(messages: List[dict]) -> str:
    """Try Grok (X.AI) API"""
    if not GROK_API_KEY:
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "grok-beta",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        response = requests.post(GROK_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            if reply.strip():
                return reply
        return None
    except:
        return None

def try_huggingface_api(messages: List[dict]) -> str:
    """Try HuggingFace API"""
    if not HUGGINGFACE_API_KEY:
        return None
    
    try:
        # Combine messages into a single prompt
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7
            }
        }
        
        response = requests.post(HUGGINGFACE_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                reply = result[0].get("generated_text", "")
                if reply.strip():
                    return reply
        return None
    except:
        return None

# ---------- FastAPI app ----------
app = FastAPI(title="Cashflow & Forecasting Chatbot with Multi-API Fallback")

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
    api_used: str = "fallback"

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        # Check for greetings first
        greeting_response = handle_greeting(req.message)
        if greeting_response:
            return ChatResponse(reply=greeting_response, api_used="greeting")
        
        # Prepare messages for API
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history if provided
        if req.history:
            for msg in req.history:
                messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": req.message})
        
        # Try APIs in order: Jules -> Gemini -> Grok -> HuggingFace
        reply = None
        api_used = "none"
        
        # Try Jules first
        reply = try_jules_api(messages)
        if reply:
            api_used = "Jules AI"
        
        # Try Gemini if Jules failed
        if not reply:
            reply = try_gemini_api(messages)
            if reply:
                api_used = "Google Gemini"
        
        # Try Grok if Gemini failed
        if not reply:
            reply = try_grok_api(messages)
            if reply:
                api_used = "Grok (X.AI)"
        
        # Try HuggingFace if Grok failed
        if not reply:
            reply = try_huggingface_api(messages)
            if reply:
                api_used = "HuggingFace"
        
        # If all APIs failed
        if not reply:
            reply = "I'm currently experiencing technical difficulties with all AI services. Please try again later."
            api_used = "error"
        
        return ChatResponse(reply=reply, api_used=api_used)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend error: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint with API key status"""
    return {
        "status": "healthy",
        "available_apis": {
            "jules": bool(JULES_API_KEY),
            "gemini": bool(GEMINI_API_KEY),
            "grok": bool(GROK_API_KEY),
            "huggingface": bool(HUGGINGFACE_API_KEY)
        }
    }
