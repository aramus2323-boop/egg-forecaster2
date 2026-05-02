"""
INTERACTIVE EGG PRICE FORECASTING DASHBOARD
Streamlit web application for visualizing forecasts and scenarios
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from egg_forecaster import EggForecaster, CpiAnalyzer, MeanReversionAnalyzer

# Page configuration
st.set_page_config(
    page_title="Egg Price Forecasting",
    page_icon="🥚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .forecast-title {
        font-size: 28px;
        font-weight: bold;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================
st.sidebar.title("⚙️ Configuration")
st.sidebar.markdown("---")

# Data source selection
data_source = st.sidebar.radio(
    "Select Data Source:",
    ["Sample Data (Built-in)", "Upload CSV File"]
)

# Load or create data
@st.cache_resource
def load_default_data():
    """Create sample egg price data"""
    dates = pd.date_range(start='2008-01-01', end='2026-04-28', freq='MS')
    np.random.seed(42)
    
    # Create realistic egg price data with trends and seasonality
    base_price = 1.0
    prices = []
    
    for i, date in enumerate(dates):
        # Trend component (0.5 to 1.0)
        trend = 0.5 + (i / len(dates)) * 0.5
        
        # Seasonality (±0.2)
        season = 0.2 * np.sin(2 * np.pi * date.month / 12)
        
        # Random noise
        noise = np.random.normal(0, 0.05)
        
        # Base price calculation
        base = trend + season + noise
        
        # Crisis periods (AI outbreaks)
        crisis_multiplier = 1.0
        if date.year == 2022 and date.month >= 2:
            crisis_multiplier = 1.5
        elif date.year == 2023 and date.month <= 6:
            crisis_multiplier = 1.3
        
        price = base * crisis_multiplier
        prices.append(max(price, 0.5))
    
    df = pd.DataFrame({
        'date': dates,
        'price': prices
    })
    
    return df

if data_source == "Sample Data (Built-in)":
    data = load_default_data()
    st.sidebar.success("✓ Sample data loaded")
else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV (columns: date, price)",
        type=['csv']
    )
    
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date')
        st.sidebar.success(f"✓ Loaded {len(data)} records")
    else:
        data = load_default_data()
        st.sidebar.info("Using sample data")

# Forecast parameters
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Forecast Parameters")

forecast_months = st.sidebar.slider(
    "Forecast horizon (months):",
    min_value=1,
    max_value=24,
    value=6,
    step=1
)

confidence_level = st.sidebar.slider(
    "Confidence interval:",
    min_value=0.7,
    max_value=0.99,
    value=0.95,
    step=0.05
)

# Disease scenario
st.sidebar.markdown("---")
st.sidebar.subheader("🦠 Disease Scenarios")

disease_select = st.sidebar.selectbox(
    "Select disease scenario:",
    ["None", "Avian Influenza (H5N1)", "Newcastle Disease", "Infectious Bronchitis"]
)

disease_map = {
    "None": None,
    "Avian Influenza (H5N1)": "AI",
    "Newcastle Disease": "ND",
    "Infectious Bronchitis": "IB"
}

selected_disease = disease_map[disease_select]

if selected_disease:
    outbreak_date = st.sidebar.date_input(
        "Outbreak date:",
        value=datetime.now()
    )
else:
    outbreak_date = None

# ============================================================================
# MAIN CONTENT
# ============================================================================
st.title("🥚 Egg Price Forecasting System")
st.markdown("---")

# Initialize forecaster
@st.cache_resource
def init_forecaster(df):
    forecaster = EggForecaster()
    forecaster.data = df
    forecaster.train()
    return forecaster

forecaster = init_forecaster(data)

# Tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Forecast", "📊 Historical Analysis", "🎯 Scenarios", 
     "📉 Mean Reversion", "ℹ️ About"]
)

# ============================================================================
# TAB 1: FORECAST
# ============================================================================
with tab1:
    st.subheader("Price Forecast")
    
    # Generate forecast
    forecast_df = forecaster.forecast(n_months=forecast_months)
    
    # Apply disease scenario if selected
    if selected_disease and outbreak_date:
        forecast_df = forecaster.apply_disease_scenario(
            forecast_df,
            disease=selected_disease,
            outbreak_date=pd.Timestamp(outbreak_date)
        )
    
    # Create interactive plot
    fig = go.Figure()
    
    # Historical prices
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['price'],
        mode='lines',
        name='Historical Prices',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Price: $%{y:.2f}<extra></extra>'
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df['date'],
        y=forecast_df['price_forecast'],
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#2ca02c', width=2, dash='dash'),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Forecast: $%{y:.2f}<extra></extra>'
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_df['date'].tolist() + forecast_df['date'].tolist()[::-1],
        y=forecast_df['upper_bound'].tolist() + forecast_df['lower_bound'].tolist()[::-1],
        fill='toself',
        name='Confidence Interval',
        fillcolor='rgba(46, 202, 44, 0.2)',
        line=dict(color='rgba(255, 255, 255, 0)'),
        hoverinfo='skip'
    ))
    
    # Disease scenario if applicable
    if selected_disease and outbreak_date and 'price_with_disease' in forecast_df.columns:
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['price_with_disease'],
            mode='lines+markers',
            name=f'{disease_select} Impact',
            line=dict(color='#d62728', width=2, dash='dot'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>With Disease: $%{y:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"Egg Price Forecast ({forecast_months} months)",
        xaxis_title="Date",
        yaxis_title="Price ($/lb)",
        hovermode='x unified',
        template='plotly_white',
        height=600,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Forecast table
    st.subheader("Forecast Data")
    display_cols = ['date', 'price_forecast', 'lower_bound', 'upper_bound']
    if 'price_with_disease' in forecast_df.columns:
        display_cols.append('price_with_disease')
    
    forecast_display = forecast_df[display_cols].copy()
    forecast_display['date'] = forecast_display['date'].dt.strftime('%Y-%m-%d')
    forecast_display.columns = ['Date', 'Forecast', 'Lower Bound', 'Upper Bound'] + (
        ['With Disease'] if 'price_with_disease' in forecast_df.columns else []
    )
    
    st.dataframe(forecast_display, use_container_width=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Price", f"${data['price'].iloc[-1]:.2f}")
    
    with col2:
        avg_forecast = forecast_df['price_forecast'].mean()
        change = ((avg_forecast - data['price'].iloc[-1]) / data['price'].iloc[-1]) * 100
        st.metric("Avg Forecast", f"${avg_forecast:.2f}", f"{change:+.1f}%")
    
    with col3:
        st.metric("Model R²", f"{forecaster.metrics['ensemble_r2']:.4f}")
    
    with col4:
        st.metric("RMSE", f"${forecaster.metrics['ensemble_rmse']:.4f}")

# ============================================================================
# TAB 2: HISTORICAL ANALYSIS
# ============================================================================
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Price Trends")
        
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(
            x=data['date'],
            y=data['price'],
            mode='lines',
            fill='tozeroy',
            name='Price',
            line=dict(color='#1f77b4')
        ))
        
        # Add rolling average
        rolling_mean = data['price'].rolling(12).mean()
        fig_hist.add_trace(go.Scatter(
            x=data['date'],
            y=rolling_mean,
            mode='lines',
            name='12-Month MA',
            line=dict(color='#ff7f0e', dash='dash')
        ))
        
        fig_hist.update_layout(
            title="Historical Prices with 12-Month Moving Average",
            xaxis_title="Date",
            yaxis_title="Price ($/lb)",
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("Price Distribution")
        
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=data['price'],
            nbinsx=30,
            name='Price Distribution',
            marker_color='#2ca02c'
        ))
        
        fig_dist.update_layout(
            title="Historical Price Distribution",
            xaxis_title="Price ($/lb)",
            yaxis_title="Frequency",
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
    
    # Summary statistics
    st.subheader("Summary Statistics")
    
    stats = {
        'Mean': data['price'].mean(),
        'Median': data['price'].median(),
        'Std Dev': data['price'].std(),
        'Min': data['price'].min(),
        'Max': data['price'].max(),
        'Range': data['price'].max() - data['price'].min(),
        '25th Percentile': data['price'].quantile(0.25),
        '75th Percentile': data['price'].quantile(0.75)
    }
    
    stats_df = pd.DataFrame(stats.items(), columns=['Metric', 'Value'])
    st.dataframe(stats_df, use_container_width=True)

# ============================================================================
# TAB 3: SCENARIOS
# ============================================================================
with tab3:
    st.subheader("Disease Impact Scenarios")
    
    diseases = {
        'AI': 'Avian Influenza (H5N1)',
        'ND': 'Newcastle Disease',
        'IB': 'Infectious Bronchitis'
    }
    
    cols = st.columns(3)
    
    for i, (disease_code, disease_name) in enumerate(diseases.items()):
        with cols[i]:
            scenario = forecaster.get_disease_impact_scenario(disease_code)
            
            st.markdown(f"**{disease_name}**")
            st.write(f"Severity: {scenario['severity']}")
            st.write(f"Price Impact: {scenario['price_impact']*100:.0f}%")
            st.write(f"Lead Time: {scenario['lead_time_days']} days")
            st.write(f"Recovery: {scenario['recovery_weeks']} weeks")
            st.write(f"Probability: {scenario['probability']*100:.0f}%")
    
    st.markdown("---")
    
    # Compare scenarios
    st.subheader("Scenario Comparison")
    
    scenario_cols = st.columns(3)
    scenario_diseases = ['AI', 'ND', 'IB']
    scenario_forecasts = {}
    
    for disease_code, col in zip(scenario_diseases, scenario_cols):
        with col:
            forecast_scenario = forecaster.forecast(n_months=forecast_months)
            forecast_scenario = forecaster.apply_disease_scenario(
                forecast_scenario,
                disease=disease_code,
                outbreak_date=pd.Timestamp(datetime.now())
            )
            scenario_forecasts[disease_code] = forecast_scenario
    
    # Plot comparison
    fig_scenarios = go.Figure()
    
    # Base forecast
    forecast_base = forecaster.forecast(n_months=forecast_months)
    fig_scenarios.add_trace(go.Scatter(
        x=forecast_base['date'],
        y=forecast_base['price_forecast'],
        mode='lines',
        name='No Disease',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Disease scenarios
    colors = {'AI': '#d62728', 'ND': '#ff7f0e', 'IB': '#2ca02c'}
    for disease_code, disease_name in diseases.items():
        fig_scenarios.add_trace(go.Scatter(
            x=scenario_forecasts[disease_code]['date'],
            y=scenario_forecasts[disease_code]['price_with_disease'],
            mode='lines',
            name=disease_name,
            line=dict(color=colors[disease_code], width=2, dash='dash')
        ))
    
    fig_scenarios.update_layout(
        title="Price Forecasts Under Disease Scenarios",
        xaxis_title="Date",
        yaxis_title="Price ($/lb)",
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_scenarios, use_container_width=True)

# ============================================================================
# TAB 4: MEAN REVERSION
# ============================================================================
with tab4:
    st.subheader("Mean Reversion Analysis")
    
    # Identify extremes
    prices_array = data['price'].values
    extremes = MeanReversionAnalyzer.identify_extremes(prices_array, window=24, threshold=2.0)
    
    fig_mr = go.Figure()
    
    # Price line
    fig_mr.add_trace(go.Scatter(
        x=data['date'],
        y=data['price'],
        mode='lines',
        name='Price',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Rolling mean
    rolling_mean = data['price'].rolling(24).mean()
    fig_mr.add_trace(go.Scatter(
        x=data['date'],
        y=rolling_mean,
        mode='lines',
        name='24-Month MA',
        line=dict(color='#ff7f0e', dash='dash')
    ))
    
    # Bands
    rolling_std = data['price'].rolling(24).std()
    upper_band = rolling_mean + (2 * rolling_std)
    lower_band = rolling_mean - (2 * rolling_std)
    
    fig_mr.add_trace(go.Scatter(
        x=data['date'].tolist() + data['date'].tolist()[::-1],
        y=upper_band.tolist() + lower_band.tolist()[::-1],
        fill='toself',
        name='±2 Std Dev',
        fillcolor='rgba(255, 0, 0, 0.1)',
        line=dict(color='rgba(255, 0, 0, 0)')
    ))
    
    # Extremes
    extreme_dates = data[extremes]['date']
    extreme_prices = data[extremes]['price']
    
    fig_mr.add_trace(go.Scatter(
        x=extreme_dates,
        y=extreme_prices,
        mode='markers',
        name='Extreme Points',
        marker=dict(color='red', size=10, symbol='star')
    ))
    
    fig_mr.update_layout(
        title="Mean Reversion Analysis (Bollinger Bands)",
        xaxis_title="Date",
        yaxis_title="Price ($/lb)",
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_mr, use_container_width=True)
    
    # Statistics
    reversion_time = MeanReversionAnalyzer.estimate_reversion_time(prices_array, extremes)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Extreme Points", extremes.sum())
    
    with col2:
        st.metric("Avg Reversion Time", f"{reversion_time:.0f} months")
    
    with col3:
        st.metric("Current Deviation", f"{((data['price'].iloc[-1] - rolling_mean.iloc[-1]) / rolling_std.iloc[-1]):.2f} σ")

# ============================================================================
# TAB 5: ABOUT
# ============================================================================
with tab5:
    st.subheader("About This Application")
    
    st.markdown("""
    ### Egg Price Forecasting System
    
    This application provides comprehensive forecasting and analysis of egg prices using:
    
    **📊 Models:**
    - Random Forest Regression
    - Gradient Boosting Regression
    - Weighted Ensemble approach
    - Mean Reversion analysis
    
    **🦠 Disease Integration:**
    - Avian Influenza (H5N1) impact scenarios
    - Newcastle Disease scenarios
    - Infectious Bronchitis scenarios
    
    **📈 Features:**
    - Historical price analysis
    - Seasonal pattern detection
    - Mean reversion identification
    - Confidence intervals
    - Disease outbreak impact modeling
    
    ### Data Requirements
    
    CSV file with columns:
    - `date`: YYYY-MM-DD format
    - `price`: Price per pound in dollars
    
    ### Model Performance
    """)
    
    metrics_display = {
        'R² Score': f"{forecaster.metrics['ensemble_r2']:.4f}",
        'RMSE': f"${forecaster.metrics['ensemble_rmse']:.4f}",
        'MAE': f"${forecaster.metrics['ensemble_mae']:.4f}",
        'RF Weight': f"{forecaster.metrics['rf_weight']:.1%}",
        'GB Weight': f"{forecaster.metrics['gb_weight']:.1%}"
    }
    
    metrics_df = pd.DataFrame(metrics_display.items(), columns=['Metric', 'Value'])
    st.dataframe(metrics_df, use_container_width=True)
    
    st.markdown("""
    ### Limitations
    
    - ⚠️ Supply shocks (avian flu) are unpredictable
    - ⚠️ Not suitable for long-term (5+ year) forecasts
    - ⚠️ Policy changes and tariffs not captured
    - ⚠️ Best for 3-12 month forecasts during normal conditions
    
    ### Data Sources
    
    - USDA APHIS (Animal and Plant Health Inspection Service)
    - USDA NASS (National Agricultural Statistics Service)
    - BLS (Bureau of Labor Statistics) pricing data
    
    ### Contact & Support
    
    For issues or suggestions, please refer to the documentation.
    """)


if __name__ == '__main__':
    pass
