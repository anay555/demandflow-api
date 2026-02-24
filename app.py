from fastapi import FastAPI
import pandas as pd
import json

app = FastAPI()

# Load precomputed activation data
with open("activation_data.json") as f:
    activation_data = json.load(f)

@app.get("/")
def home():
    return {"message": "DemandFlow Intelligence API Running"}

@app.get("/activation")
def get_activation_data():
    return activation_data

@app.get("/churn")
def get_churn():
    return activation_data["churn_alerts"]

@app.get("/reorder")
def get_reorder():
    return activation_data["reorder_alerts"]

@app.get("/cross-sell")
def get_cross_sell():
    return activation_data["cross_sell_alerts"]