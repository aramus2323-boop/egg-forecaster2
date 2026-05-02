"""
FastAPI Backend for Egg Price Forecaster
Provides REST API endpoints for the enhanced forecasting model
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys

from egg_forecaster import EggForecaster

# Initialize FastAPI app
app = FastAPI(
    title="Egg Price Forecaster API",
    description="Professional egg price prediction with advanced ML features",
    version="2.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class ForecastRequest(BaseModel):
    months_ahead: int = 6
    include_disease_risk: bool = True
    confidence_level: Optional[str] = "medium"

class DiseaseScenarioRequest(BaseModel):
    outbreak_severity: str = "moderate"  # mild, moderate, severe
    recovery_months: int = 6

class HistoricalDataRequest(BaseModel):
    months_back: int = 24

class ForecastPoint(BaseModel):
    date: str
    price: float
    lower_bound: float
    upper_bound: float
    confidence_multiplier: float
    disease_risk_score: float

class ForecastResponse(BaseModel):
    success: bool
    forecast: List[Dict[str, Any]]
    model_metrics: Dict[str, Any]
    regime_analysis: Dict[str, Any]
    generated_at: str

class HistoricalResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    statistics: Dict[str, Any]

# Global forecaster instance (initialized on startup)
forecaster = None

@app.on_event("startup")
async def startup_event():
    """Initialize forecaster model on startup"""
    global forecaster
    try:
        # Determine data paths
        base_path = os.path.dirname(os.path.abspath(__file__))
        price_path = os.path.join(base_path, "egg_prices.csv")
        cpi_path = os.path.join(base_path, "cpi_data.csv")
        prod_path = os.path.join(base_path, "production_data.csv")
        
        # Initialize with available data
        forecaster = EggForecaster(
            data_path=price_path,
            cpi_path=cpi_path if os.path.exists(cpi_path) else None,
            production_path=prod_path if os.path.exists(prod_path) else None
        )
        
        print(f"DEBUG: Forecaster created: {forecaster is not None}")
        print(f"DEBUG: Before train - is_trained: {forecaster.is_trained}")
        
        # Train model
        forecaster.train()
        
        print(f"DEBUG: After train - is_trained: {forecaster.is_trained}")
        print("[OK] Model loaded and trained successfully")
    except Exception as e:
        print(f"[ERROR] Startup error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    forecast_test = None
    if forecaster:
        try:
            forecast_test = forecaster.forecast(n_months=1, include_disease_risk=False)
        except Exception as e:
            forecast_test = f"Error: {str(e)}"
    
    return {
        "status": "healthy",
        "model_loaded": forecaster is not None,
        "model_trained": forecaster.is_trained if forecaster else False,
        "forecast_test": "works" if forecast_test is not None and isinstance(forecast_test, pd.DataFrame) else str(forecast_test)[:100],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check forecaster state"""
    return {
        "forecaster_is_none": forecaster is None,
        "forecaster_is_trained": forecaster.is_trained if forecaster else None,
        "forecaster_has_data": forecaster.data is not None if forecaster else None,
        "forecaster_combined_data_rows": len(forecaster.combined_data) if forecaster and forecaster.combined_data is not None else None,
        "forecaster_metrics": forecaster.metrics if forecaster else None,
    }

import sys

@app.post("/api/forecast-debug")
async def forecast_debug(request: ForecastRequest):
    """Debug endpoint to log all steps"""
    with open(r"c:\Users\narcisar\Desktop\Project Chicken\api_debug.log", "a") as f:
        f.write(f"\n=== NEW REQUEST ===\n")
        f.write(f"forecast_debug called\n")
        f.write(f"forecaster: {forecaster}\n")
        f.write(f"forecaster.is_trained: {forecaster.is_trained}\n")
    return {"debug": "ok"}

@app.post("/api/forecast")
async def get_forecast(request: ForecastRequest):
    """Simple forecast endpoint - return raw data"""
    print(f"[API] Forecast endpoint called")
    
    if forecaster is None:
        print(f"[API] Forecaster is None!")
        return {"error": "Model not initialized"}, 500
    
    print(f"[API] Forecaster exists. is_trained={forecaster.is_trained}")
    print(f"[API] About to call forecaster.forecast(n_months={request.months_ahead})")
    
    # Call forecast directly
    forecast_df = forecaster.forecast(
        n_months=request.months_ahead,
        include_disease_risk=request.include_disease_risk
    )
    
    print(f"[API] forecast_df type: {type(forecast_df)}, is None: {forecast_df is None}")
    
    if forecast_df is None:
        print(f"[API] Forecast returned None")
        return {"error": "Forecast returned None"}, 500
    
    # Convert to simple list of dicts
    forecast_list = []
    for idx, row in forecast_df.iterrows():
        forecast_list.append({
            "date": str(row['date']),
            "price": float(row['price_forecast']),
            "lower_bound": float(row.get('lower_bound', 0)),
            "upper_bound": float(row.get('upper_bound', 0)),
            "confidence_multiplier": float(row.get('confidence_multiplier', 1.0)),
            "disease_risk_score": float(row.get('disease_risk_score', 0))
        })
    
    return {
        "success": True,
        "forecast": forecast_list,
        "model_metrics": {"r2": 0.96},
        "regime_analysis": {},
        "generated_at": datetime.now().isoformat()
    }

@app.post("/api/disease-scenario")
async def disease_scenario(request: DiseaseScenarioRequest):
    """Apply disease outbreak scenario to forecast"""
    try:
        if forecaster is None:
            return {"error": "Model not initialized"}, 500
        
        severity_map = {"mild": 1.1, "moderate": 1.3, "severe": 1.5}
        multiplier = severity_map.get(request.outbreak_severity, 1.3)
        
        # Generate base forecast
        forecast_df = forecaster.forecast(n_months=6, include_disease_risk=True)
        
        if forecast_df is None:
            return {"error": "Forecast generation failed"}, 500
        
        # Apply disease multiplier to prices
        scenario_df = forecast_df.copy()
        scenario_df['disease_adjusted_price'] = scenario_df['price_forecast'] * multiplier
        
        # Convert to JSON
        scenario_data = []
        for idx, row in scenario_df.iterrows():
            date_str = str(row['date']) if not hasattr(row['date'], 'strftime') else row['date'].strftime("%Y-%m-%d")
            scenario_data.append({
                "date": date_str,
                "original_price": float(row['price_forecast']),
                "disease_adjusted_price": float(row['disease_adjusted_price']),
                "price_impact": float(row['disease_adjusted_price'] - row['price_forecast'])
            })
        
        return {
            "success": True,
            "scenario": request.outbreak_severity,
            "severity_multiplier": multiplier,
            "recovery_months": request.recovery_months,
            "forecast": scenario_data
        }
    
    except Exception as e:
        print(f"[API] Disease scenario error: {str(e)}")
        return {"error": f"Disease scenario error: {str(e)}"}, 500

@app.post("/api/historical")
async def get_historical(request: HistoricalDataRequest):
    """Get historical price data for charting"""
    try:
        if forecaster is None:
            return {"error": "Model not initialized"}, 500
        
        if forecaster.data is None:
            return {"error": "No data loaded"}, 500
        
        # Get data from forecaster
        data = forecaster.data.tail(request.months_back).copy()
        
        # Convert to JSON
        historical_data = []
        for idx, row in data.iterrows():
            date = row.get('date', idx)
            if hasattr(date, 'strftime'):
                date_str = date.strftime("%Y-%m-%d")
            else:
                date_str = str(date)
            
            historical_data.append({
                "date": date_str,
                "price": float(row.get('price', 0)),
                "cpi": float(row.get('cpi', 0)) if 'cpi' in row else None,
                "production": float(row.get('production', 0)) if 'production' in row else None
            })
        
        # Calculate statistics
        prices = [x['price'] for x in historical_data if x['price'] > 0]
        if prices:
            stats = {
                "min_price": float(np.min(prices)),
                "max_price": float(np.max(prices)),
                "avg_price": float(np.mean(prices)),
                "std_dev": float(np.std(prices)),
                "latest_price": float(prices[-1]),
                "volatility": float(np.std(prices) / np.mean(prices)) if np.mean(prices) > 0 else 0
            }
        else:
            stats = {"min_price": 0, "max_price": 0, "avg_price": 0, "std_dev": 0, "latest_price": 0, "volatility": 0}
        
        return {
            "success": True,
            "data": historical_data,
            "statistics": stats
        }
    
    except Exception as e:
        print(f"[API] Historical error: {str(e)}")
        return {"error": f"Historical data error: {str(e)}"}, 500

@app.get("/test-forecast")
async def test_forecast():
    """Test forecast directly"""
    try:
        result = forecaster.forecast(n_months=3, include_disease_risk=False)
        return {
            "type": str(type(result)),
            "is_none": result is None,
            "shape": str(result.shape) if result is not None else None,
            "columns": list(result.columns) if result is not None else None
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/api/model-info")
async def model_info():
    """Get information about the model"""
    return {
        "name": "Enhanced Egg Price Forecaster",
        "version": "2.0.0",
        "improvements": [
            "CPI/Inflation integration",
            "Regime-adaptive forecasting",
            "Production data features",
            "Elasticity-based mean reversion",
            "Rolling volatility regimes",
            "Disease outbreak risk factors",
            "CPI-based ensemble component",
            "Regime-dependent confidence intervals",
            "Production-weighted seasonal factors",
            "Out-of-sample regime-specific validation"
        ],
        "model_type": "Three-model ensemble (RF + GB + CPI-Baseline)",
        "ensemble_r2": 0.9601,
        "features": 21,
        "training_years": 18,
        "forecast_horizon": "1-24 months",
        "last_updated": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """API documentation and landing page"""
    return {
        "message": "🐔 Egg Price Forecaster API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "forecast": "POST /api/forecast",
            "disease_scenario": "POST /api/disease-scenario",
            "historical": "POST /api/historical",
            "model_info": "GET /api/model-info",
            "api_docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
