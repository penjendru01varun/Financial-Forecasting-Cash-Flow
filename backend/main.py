from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import shutil
import os

from models import ForecastPoint, ForecastResponse, ChatRequest
from agents import (
    ingestion_agent_from_csv,
    forecasting_agent,
    risk_alert_agent,
    advisor_agent,
    compute_initial_balance,
)
from llm_agent import explanation_agent

app = FastAPI(
    title="MSME Cashflow Agent System",
    description="Multi-agent system for MSME cash flow forecasting and risk management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "MSME Cashflow Agent System API",
        "version": "1.0.0",
        "endpoints": {
            "forecast": "/api/forecast",
            "chat": "/api/chat"
        }
    }

@app.post("/api/forecast", response_model=ForecastResponse)
async def generate_forecast(
    file: UploadFile = File(...),
    initial_balance: Optional[float] = Form(default=None),
    horizon_weeks: int = Form(default=8),
):
    """
    Orchestrator endpoint:
    1. Data ingestion agent parses CSV.
    2. Forecasting agent projects cash flow.
    3. Risk agent creates alerts.
    4. Advisor agent suggests actions.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        df = ingestion_agent_from_csv(save_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")

    if initial_balance is None:
        initial_balance = compute_initial_balance(df)

    forecast_df, buffer_amount = forecasting_agent(
        df, horizon_weeks=horizon_weeks, initial_balance=initial_balance
    )

    alerts = risk_alert_agent(forecast_df, buffer_amount)
    recommendations = advisor_agent(df, forecast_df, buffer_amount)

    points: List[ForecastPoint] = []
    for _, row in forecast_df.iterrows():
        points.append(
            ForecastPoint(
                week_start=row["week_start"],
                week_end=row["week_end"],
                projected_inflow=row["projected_inflow"],
                projected_outflow=row["projected_outflow"],
                projected_balance=row["projected_balance"],
                risk_level=row["risk_level"],
            )
        )

    response = ForecastResponse(
        initial_balance=initial_balance,
        buffer_amount=buffer_amount,
        points=points,
        alerts=alerts,
        recommendations=recommendations,
    )
    return response

@app.post("/api/chat")
async def chat_with_explanation_agent(payload: ChatRequest):
    points_dicts = [p.model_dump() for p in payload.points]
    answer = explanation_agent(
        user_question=payload.question,
        initial_balance=payload.initial_balance,
        buffer_amount=payload.buffer_amount,
        points=points_dicts,
        alerts=payload.alerts,
        recommendations=payload.recommendations,
    )
    return {"answer": answer}
