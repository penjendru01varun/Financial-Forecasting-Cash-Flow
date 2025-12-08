import os
from typing import List

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    LLM_AVAILABLE = True
except Exception as e:
    LLM_AVAILABLE = False
    print(f"Warning: OpenAI client not available: {e}")

SYSTEM_PROMPT = """
You are a financial explanation agent for Indian MSMEs specializing in cashflow forecasting.
Explain cash flow forecasts, risks, and actions in very simple, practical language.
Avoid jargon. Talk like you are advising a busy small business owner.
Use Indian Rupee (₹) symbol in responses.
Be concise and actionable.

IMPORTANT: You can ONLY answer questions related to cashflow, cash management, forecasting, 
inflows, outflows, balances, risks, and financial recommendations. 

If a user asks about anything unrelated to cashflow (like sports, weather, general knowledge, 
other topics), politely respond:
"I'm sorry, but I can only answer questions related to your cashflow forecast. 
Please ask me about your weekly projections, risk levels, recommended actions, or any 
cashflow-related concerns."
"""

def is_cashflow_related(question: str) -> bool:
    """
    Check if a question is related to cashflow topics.
    Returns True if related, False otherwise.
    """
    question_lower = question.lower()
    
    # Cashflow-related keywords
    cashflow_keywords = [
        "cashflow", "cash flow", "cash", "flow",
        "inflow", "outflow", "balance", "payment", "invoice",
        "forecast", "projection", "predict", "estimate",
        "week", "weekly", "month", "monthly",
        "risk", "risky", "safe", "tight", "buffer",
        "receivable", "payable", "revenue", "expense",
        "financial", "finance", "money", "rupee", "₹",
        "recommendation", "advice", "suggest", "action",
        "crunch", "shortage", "surplus", "deficit",
        "alert", "warning", "problem", "issue"
    ]
    
    # Check if any keyword is in the question
    return any(keyword in question_lower for keyword in cashflow_keywords)

def build_context_from_forecast(
    initial_balance: float,
    buffer_amount: float,
    points: List[dict],
    alerts: List[str],
    recommendations: List[str],
) -> str:
    """Build context string from forecast data for LLM"""
    summary_lines = [
        f"Initial balance: ₹{initial_balance:.2f}",
        f"Recommended buffer: ₹{buffer_amount:.2f}",
        "\nWeekly Forecast:",
    ]

    for idx, p in enumerate(points, 1):
        summary_lines.append(
            f" Week {idx} ({p['week_start']} to {p['week_end']}): "
            f"balance ₹{p['projected_balance']:.2f}, "
            f"inflow ₹{p['projected_inflow']:.2f}, "
            f"outflow ₹{p['projected_outflow']:.2f}, "
            f"risk: {p['risk_level']}"
        )

    if alerts:
        summary_lines.append("\nAlerts:")
        summary_lines.extend([f" - {a}" for a in alerts])

    if recommendations:
        summary_lines.append("\nRecommendations:")
        summary_lines.extend([f" - {r}" for r in recommendations])

    return "\n".join(summary_lines)

def explanation_agent(
    user_question: str,
    initial_balance: float,
    buffer_amount: float,
    points: List[dict],
    alerts: List[str],
    recommendations: List[str],
) -> str:
    """
    Explanation/chat agent using LLM to answer questions about the forecast.
    Validates that questions are cashflow-related.
    Falls back to a simple message if LLM is not available.
    """
    # First, check if the question is cashflow-related
    if not is_cashflow_related(user_question):
        return (
            "I'm sorry, but I can only answer questions related to your cashflow forecast. \n"
            "Please ask me about your weekly projections, risk levels, recommended actions, "
            "or any cashflow-related concerns."
        )
    
    if not LLM_AVAILABLE:
        return (
            "The explanation agent is currently unavailable. "
            "Please set your OPENAI_API_KEY environment variable to enable AI-powered explanations. "
            "You can still review the forecast, alerts, and recommendations above."
        )

    if not os.getenv("OPENAI_API_KEY"):
        return (
            "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable "
            "to use the explanation agent."
        )

    context = build_context_from_forecast(
        initial_balance, buffer_amount, points, alerts, recommendations
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Here is the current cashflow forecast and advice:\n\n"
                + context
                + "\n\nUser question:\n"
                + user_question
            ),
        },
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating explanation: {str(e)}. Please check your API key and try again."
