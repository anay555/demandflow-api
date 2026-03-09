from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model + data once on startup
churn_model = joblib.load("models/churn_xgb.joblib")
features_df = pd.read_parquet("data/features_df.parquet")
forecast_df = pd.read_parquet("data/forecast_df.parquet")
inventory_df = pd.read_parquet("data/inventory_df.parquet")


@app.get("/")
def home():
    return {"message": "DemandFlow Intelligence API Running"}


@app.get("/activation")
def get_activation():
    # Churn scoring
    X = features_df.drop(
        ["customer_id", "churn_label", "churn_probability"],
        axis=1,
        errors="ignore",
    ).copy()

    scored = features_df.copy()
    scored["churn_probability"] = churn_model.predict_proba(X)[:, 1]

    risk_threshold = scored["churn_probability"].quantile(0.85)
    churn_alerts = scored[scored["churn_probability"] > risk_threshold][
        ["customer_id", "churn_probability"]
    ].to_dict(orient="records")

    # Reorder alerts
    inventory_forecast = forecast_df.merge(inventory_df, on="sku_id", how="left")
    inventory_forecast["pressure_score"] = (
        inventory_forecast["forecast_month_1"] / (inventory_forecast["current_stock"] + 1)
    )

    threshold = inventory_forecast["pressure_score"].quantile(0.8)
    reorder_alerts = inventory_forecast[inventory_forecast["pressure_score"] > threshold][
        ["sku_id", "forecast_month_1", "current_stock", "pressure_score"]
    ].to_dict(orient="records")

    # Placeholder for now
    cross_sell_alerts = []

    return {
        "churn_alerts": churn_alerts,
        "reorder_alerts": reorder_alerts,
        "cross_sell_alerts": cross_sell_alerts,
    }


@app.get("/churn")
def get_churn():
    return get_activation()["churn_alerts"]


@app.get("/reorder")
def get_reorder():
    return get_activation()["reorder_alerts"]


@app.get("/cross-sell")
def get_cross_sell():
    return get_activation()["cross_sell_alerts"]
