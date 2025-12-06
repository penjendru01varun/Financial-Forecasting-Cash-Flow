from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import date

class Transaction(BaseModel):
    date: date
    description: str
    category: str
    type: Literal["inflow", "outflow"]
    amount: float

class ForecastPoint(BaseModel):
    week_start: date
    week_end: date
    projected_inflow: float
    projected_outflow: float
    projected_balance: float
    risk_level: Literal["safe", "tight", "risky"]

class ForecastResponse(BaseModel):
    initial_balance: float
    buffer_amount: float
    points: List[ForecastPoint]
    alerts: List[str]
    recommendations: List[str]

class ChatRequest(BaseModel):
    question: str
    initial_balance: float
    buffer_amount: float
    points: List[ForecastPoint]
    alerts: List[str]
    recommendations: List[str]
