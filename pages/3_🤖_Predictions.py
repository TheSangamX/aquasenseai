"""
Predictions Page - AquaSense AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import data_loader
from utils.auth import require_login, render_auth_sidebar


# Set page config
st.set_page_config(
    page_title="Predictions - AquaSense AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

require_login(post_login_page="pages/3_🤖_Predictions.py")
render_auth_sidebar()


# Load data with caching
@st.cache_data
def load_data():
    df = data_loader.load_reservoir_data("clean_reservoir_data.xls")
    df = data_loader.preprocess_data(df)
    return df


df = load_data()


# Sidebar for prediction settings
st.sidebar.title("🤖 Prediction Settings")

# Select reservoir
selected_reservoir_pred = st.sidebar.selectbox(
    "Select Reservoir for Prediction",
    options=sorted(df['Reservoir_Name'].unique()),
    index=0
)

# Prediction horizon
prediction_horizon = st.sidebar.slider(
    "Prediction Horizon (Days)",
    min_value=7,
    max_value=60,
    value=30,
    step=7
)


# Filter data for selected reservoir
reservoir_data = df[df['Reservoir_Name'] == selected_reservoir_pred].copy()


# Page title
st.title("🤖 AI Predictions")
st.markdown(f"### Reservoir: {selected_reservoir_pred}")
st.markdown("---")


# Mock ML Predictions
def generate_mock_predictions(data, horizon):
    """Generate realistic mock predictions"""
    last_date = data['Date'].max()
    last_storage = data['Storage'].iloc[-1]
    last_level = data['Level'].iloc[-1]
    
    # Create future dates
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq='D')
    
    # Generate synthetic trends with seasonality
    np.random.seed(42)
    time_steps = np.arange(horizon)
    
    # Storage prediction with small trend and noise
    storage_trend = 0.0001 * time_steps
    storage_seasonality = 0.01 * np.sin(2 * np.pi * time_steps / 30)
    storage_noise = np.random.normal(0, 0.005, horizon)
    predicted_storage = last_storage + storage_trend + storage_seasonality + storage_noise
    predicted_storage = np.clip(predicted_storage, 0, None)
    
    # Level prediction
    level_trend = 0.1 * time_steps
    level_seasonality = 2 * np.sin(2 * np.pi * time_steps / 30)
    level_noise = np.random.normal(0, 1, horizon)
    predicted_level = last_level + level_trend + level_seasonality + level_noise
    
    # Confidence intervals
    storage_ci_low = predicted_storage - 0.01
    storage_ci_high = predicted_storage + 0.01
    level_ci_low = predicted_level - 3
    level_ci_high = predicted_level + 3
    
    return pd.DataFrame({
        'Date': future_dates,
        'Predicted_Storage': predicted_storage,
        'Storage_CI_Low': storage_ci_low,
        'Storage_CI_High': storage_ci_high,
        'Predicted_Level': predicted_level,
        'Level_CI_Low': level_ci_low,
        'Level_CI_High': level_ci_high
    })


# Generate predictions
if len(reservoir_data) > 0:
    predictions = generate_mock_predictions(reservoir_data, prediction_horizon)
    
    # Prediction KPIs
    st.subheader("📈 Prediction Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Last Actual Storage",
            value=f"{reservoir_data['Storage'].iloc[-1]:.4f}"
        )
    
    with col2:
        st.metric(
            label="Predicted Avg Storage",
            value=f"{predictions['Predicted_Storage'].mean():.4f}"
        )
    
    with col3:
        st.metric(
            label="Last Actual Level",
            value=f"{reservoir_data['Level'].iloc[-1]:.2f}"
        )
    
    with col4:
        st.metric(
            label="Predicted Avg Level",
            value=f"{predictions['Predicted_Level'].mean():.2f}"
        )
    
    st.markdown("---")
    
    # Charts section
    st.subheader("📊 Prediction Charts")
    
    # Storage prediction chart
    st.markdown("#### 🔮 Storage Forecast")
    fig_storage_pred = go.Figure()
    
    # Actual data
    fig_storage_pred.add_trace(
        go.Scatter(
            x=reservoir_data['Date'],
            y=reservoir_data['Storage'],
            name='Actual Storage',
            line=dict(color='#1f77b4', width=2)
        )
    )
    
    # Predictions
    fig_storage_pred.add_trace(
        go.Scatter(
            x=predictions['Date'],
            y=predictions['Predicted_Storage'],
            name='Predicted Storage',
            line=dict(color='#ff7f0e', width=3, dash='dash')
        )
    )
    
    # Confidence interval
    fig_storage_pred.add_trace(
        go.Scatter(
            x=list(predictions['Date']) + list(reversed(predictions['Date'])),
            y=list(predictions['Storage_CI_High']) + list(reversed(predictions['Storage_CI_Low'])),
            fill='toself',
            fillcolor='rgba(255, 127, 14, 0.2)',
            line=dict(color='rgba(255, 127, 14, 0)'),
            name='95% Confidence Interval'
        )
    )
    
    fig_storage_pred.update_layout(
        title=f'Storage Forecast - {selected_reservoir_pred}',
        xaxis_title='Date',
        yaxis_title='Storage',
        height=400
    )
    st.plotly_chart(fig_storage_pred, use_container_width=True)
    
    # Level prediction chart
    st.markdown("#### 📏 Level Forecast")
    fig_level_pred = go.Figure()
    
    # Actual data
    fig_level_pred.add_trace(
        go.Scatter(
            x=reservoir_data['Date'],
            y=reservoir_data['Level'],
            name='Actual Level',
            line=dict(color='#2ca02c', width=2)
        )
    )
    
    # Predictions
    fig_level_pred.add_trace(
        go.Scatter(
            x=predictions['Date'],
            y=predictions['Predicted_Level'],
            name='Predicted Level',
            line=dict(color='#d62728', width=3, dash='dash')
        )
    )
    
    # Confidence interval
    fig_level_pred.add_trace(
        go.Scatter(
            x=list(predictions['Date']) + list(reversed(predictions['Date'])),
            y=list(predictions['Level_CI_High']) + list(reversed(predictions['Level_CI_Low'])),
            fill='toself',
            fillcolor='rgba(214, 39, 40, 0.2)',
            line=dict(color='rgba(214, 39, 40, 0)'),
            name='95% Confidence Interval'
        )
    )
    
    fig_level_pred.update_layout(
        title=f'Level Forecast - {selected_reservoir_pred}',
        xaxis_title='Date',
        yaxis_title='Level',
        height=400
    )
    st.plotly_chart(fig_level_pred, use_container_width=True)
    
    # Prediction table
    st.markdown("---")
    st.subheader("📋 Prediction Details")
    st.dataframe(predictions.round(4), use_container_width=True)

else:
    st.info("No data available for the selected reservoir")


# Footer
st.markdown("---")
st.markdown(
    "<center>© 2024 AquaSense AI - Predictive Analytics Dashboard</center>",
    unsafe_allow_html=True
)
