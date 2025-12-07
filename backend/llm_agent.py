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
You are a financial explanation agent for Indian MSMEs.
Explain cash flow forecasts, risks, and actions in very simple, practical language.
Avoid jargon. Talk like you are advising a busy small business owner.
Use Indian Rupee (₹) symbol in responses.
Be concise and actionable.
"""

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
    for p in points:
        summary_lines.append(
            f"  Week {p['week_start']} -> balance ₹{p['projected_balance']:.2f}, "
            f"inflow ₹{p['projected_inflow']:.2f}, outflow ₹{p['projected_outflow']:.2f}, "
            f"risk: {p['risk_level']}"
        )
    if alerts:
        summary_lines.append("\nAlerts:")
        summary_lines.extend([f"  - {a}" for a in alerts])
    if recommendations:
        summary_lines.append("\nRecommendations:")
        summary_lines.extend([f"  - {r}" for r in recommendations])
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
    Falls back to a simple message if LLM is not available.
    """
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
