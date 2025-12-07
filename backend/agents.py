import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

RISK_MULTIPLIER = 1.0

def ingestion_agent_from_csv(file_path: str) -> pd.DataFrame:
    """
    Data ingestion agent:
    - Reads CSV with columns: date, description, category, type, amount
    - Normalizes date and amount types
    """
    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["amount"] = df["amount"].astype(float)
    df["type"] = df["type"].str.lower()
    return df

def compute_initial_balance(df: pd.DataFrame) -> float:
    """
    Approximates current cash balance from data.
    For hackathon, treat cumulative inflow - outflow as balance.
    """
    inflow = df.loc[df["type"] == "inflow", "amount"].sum()
    outflow = df.loc[df["type"] == "outflow", "amount"].sum()
    return float(inflow - outflow)

def forecasting_agent(
    df: pd.DataFrame,
    horizon_weeks: int = 8,
    initial_balance: Optional[float] = None,
) -> Tuple[pd.DataFrame, float]:
    """
    Forecasting agent:
    - Groups historical data by week to estimate typical inflows/outflows.
    - Projects next N weeks using simple averages.
    """
    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    df_copy["week"] = df_copy["date"].dt.to_period("W").apply(lambda r: r.start_time.date())

    inflow_by_week = (
        df_copy[df_copy["type"] == "inflow"]
        .groupby("week")["amount"]
        .sum()
        .rename("inflow")
    )
    outflow_by_week = (
        df_copy[df_copy["type"] == "outflow"]
        .groupby("week")["amount"]
        .sum()
        .rename("outflow")
    )

    weekly = pd.concat([inflow_by_week, outflow_by_week], axis=1).fillna(0.0)

    avg_inflow = weekly["inflow"].mean() if not weekly.empty else 0.0
    avg_outflow = weekly["outflow"].mean() if not weekly.empty else 0.0

    buffer_amount = max(avg_outflow, 0.0) * RISK_MULTIPLIER

    today = datetime.today().date()
    next_monday = today + timedelta(days=(7 - today.weekday()) % 7)

    weeks = []
    balance = initial_balance if initial_balance is not None else compute_initial_balance(df_copy)

    for i in range(horizon_weeks):
        week_start = next_monday + timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)

        projected_inflow = float(avg_inflow)
        projected_outflow = float(avg_outflow)
        balance = balance + projected_inflow - projected_outflow

        if balance >= buffer_amount * 2:
            risk_level = "safe"
        elif balance >= buffer_amount:
            risk_level = "tight"
        else:
            risk_level = "risky"

        weeks.append(
            {
                "week_start": week_start,
                "week_end": week_end,
                "projected_inflow": projected_inflow,
                "projected_outflow": projected_outflow,
                "projected_balance": float(balance),
                "risk_level": risk_level,
            }
        )

    forecast_df = pd.DataFrame(weeks)
    return forecast_df, buffer_amount

def risk_alert_agent(forecast_df: pd.DataFrame, buffer_amount: float) -> List[str]:
    """
    Risk & alert agent:
    - Scans forecast to identify risky or tight weeks.
    """
    alerts: List[str] = []
    for _, row in forecast_df.iterrows():
        if row["risk_level"] == "risky":
            alerts.append(
                f"⚠️ High risk in week starting {row['week_start']}: "
                f"projected balance ₹{row['projected_balance']:.2f} below safe buffer ₹{buffer_amount:.2f}."
            )
        elif row["risk_level"] == "tight":
            alerts.append(
                f"⚡ Tight cash in week starting {row['week_start']}: "
                f"projected balance ₹{row['projected_balance']:.2f} close to buffer ₹{buffer_amount:.2f}."
            )
    return alerts

def advisor_agent(
    df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    buffer_amount: float,
) -> List[str]:
    """
    Advisor agent:
    - Generates practical recommendations based on inflow/outflow patterns and risk weeks.
    """
    recommendations: List[str] = []

    inflow_total = df.loc[df["type"] == "inflow", "amount"].sum()
    outflow_total = df.loc[df["type"] == "outflow", "amount"].sum()

    if outflow_total > inflow_total:
        recommendations.append(
            "💡 Total outflows exceed inflows; consider reducing discretionary expenses or renegotiating payment terms with vendors."
        )
    else:
        recommendations.append(
            "✅ Inflows currently exceed outflows; maintain this by invoicing promptly and following up on overdue payments."
        )

    risky_weeks = forecast_df[forecast_df["risk_level"] == "risky"]
    if not risky_weeks.empty:
        first_risky = risky_weeks.iloc[0]
        recommendations.append(
            f"🎯 Prepare for the week starting {first_risky['week_start']} by accelerating receivables or delaying non-critical purchases."
        )

    recommendations.append(
        "📋 Implement strict invoicing discipline: send invoices within 24 hours and follow up before due dates to stabilize cash flow."
    )

    recommendations.append(
        f"💰 Try to maintain at least one week of outflows (~₹{buffer_amount:.2f}) as a minimum cash buffer in your main account."
    )

    return recommendations
