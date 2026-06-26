"""
ML Predictions Page - AquaSense AI
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import data_loader
from utils.auth import require_login, render_auth_sidebar


# Set page config
st.set_page_config(
    page_title="ML Predictions - AquaSense AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

require_login(post_login_page="pages/7_🤖_ML_Predictions.py")
render_auth_sidebar()


# Load data with caching
@st.cache_data
def load_data():
    df = data_loader.load_reservoir_data("clean_reservoir_data.xls")
    df = data_loader.preprocess_data(df)
    return df


df = load_data()


# Sidebar
st.sidebar.title("⚙️ ML Settings")

selected_reservoir = st.sidebar.selectbox(
    "Select Reservoir for Prediction",
    options=sorted(df['Reservoir_Name'].unique()),
    index=0
)

test_size = st.sidebar.slider(
    "Test Set Size (%)",
    min_value=10,
    max_value=40,
    value=20,
    step=5
) / 100

st.sidebar.markdown("---")
st.sidebar.subheader("Model Parameters")

# Random Forest parameters
n_estimators = st.sidebar.slider(
    "Number of Trees (RF)",
    min_value=50,
    max_value=300,
    value=100,
    step=50
)

max_depth = st.sidebar.slider(
    "Max Depth (RF)",
    min_value=3,
    max_value=15,
    value=10,
    step=1
)


# Page title
st.title("🤖 ML Predictions")
st.markdown(f"### Reservoir: {selected_reservoir}")
st.markdown("---")


# ==========================================
# PREPARE DATA FOR ML
# ==========================================

# Filter data for selected reservoir
res_df = df[df['Reservoir_Name'] == selected_reservoir].copy()

# Sort by date
res_df = res_df.sort_values('Date').reset_index(drop=True)

if len(res_df) > 1:
    # Feature engineering
    res_df['Day_of_Year'] = res_df['Date'].dt.dayofyear
    res_df['Month'] = res_df['Date'].dt.month
    res_df['Lag_1'] = res_df['Level'].shift(1)
    
    # Drop NaN values from lag
    res_df = res_df.dropna()
    
    # Features and target
    features = ['Month', 'Day_of_Year', 'Lag_1']
    X = res_df[features]
    y = res_df['Level']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False, random_state=42
    )


    # ==========================================
    # TRAIN MODELS
    # ==========================================

    with st.spinner("Training models..."):
        # Linear Regression
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        lr_pred = lr_model.predict(X_test)
        
        # Random Forest
        rf_model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        rf_pred = rf_model.predict(X_test)


    # ==========================================
    # CALCULATE METRICS
    # ==========================================

    def calculate_metrics(y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        return mae, rmse, r2

    lr_mae, lr_rmse, lr_r2 = calculate_metrics(y_test, lr_pred)
    rf_mae, rf_rmse, rf_r2 = calculate_metrics(y_test, rf_pred)


    # ==========================================
    # DISPLAY METRICS COMPARISON
    # ==========================================

    st.subheader("📊 Model Performance Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Linear Regression")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("MAE", f"{lr_mae:.4f}")
        metric_col2.metric("RMSE", f"{lr_rmse:.4f}")
        metric_col3.metric("R² Score", f"{lr_r2:.4f}")
    
    with col2:
        st.markdown("#### Random Forest")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("MAE", f"{rf_mae:.4f}")
        metric_col2.metric("RMSE", f"{rf_rmse:.4f}")
        metric_col3.metric("R² Score", f"{rf_r2:.4f}")
    
    st.markdown("---")


    # ==========================================
    # PLOT ACTUAL VS PREDICTED
    # ==========================================

    st.subheader("📈 Actual vs Predicted Levels")
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)
    
    # Linear Regression
    fig.add_trace(
        go.Scatter(
            x=y_test.index,
            y=y_test.values,
            name="Actual",
            mode="lines+markers",
            line=dict(color="#1f77b4", width=2)
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=y_test.index,
            y=lr_pred,
            name="Linear Regression Predicted",
            mode="lines+markers",
            line=dict(color="#ff7f0e", width=2, dash="dash")
        ),
        row=1, col=1
    )
    
    # Random Forest
    fig.add_trace(
        go.Scatter(
            x=y_test.index,
            y=y_test.values,
            name="Actual",
            mode="lines+markers",
            line=dict(color="#1f77b4", width=2),
            showlegend=False
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=y_test.index,
            y=rf_pred,
            name="Random Forest Predicted",
            mode="lines+markers",
            line=dict(color="#2ca02c", width=2, dash="dash")
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        title="Actual vs Predicted Reservoir Levels",
        showlegend=True
    )
    fig.update_yaxes(title_text="Level", row=1, col=1)
    fig.update_yaxes(title_text="Level", row=2, col=1)
    fig.update_xaxes(title_text="Data Point", row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")


    # ==========================================
    # FUTURE PREDICTIONS
    # ==========================================

    st.subheader("🔮 Future Predictions")
    
    future_days = st.slider(
        "Days to Predict",
        min_value=7,
        max_value=60,
        value=30,
        step=7
    )
    
    # Generate future predictions
    last_data = X.iloc[-1:].copy()
    last_level = y.iloc[-1]
    
    lr_future_pred = []
    rf_future_pred = []
    future_dates = pd.date_range(start=res_df['Date'].max() + pd.Timedelta(days=1), periods=future_days)
    
    for date in future_dates:
        day_of_year = date.dayofyear
        month = date.month
        
        # Predict with both models
        next_input = pd.DataFrame([[month, day_of_year, last_level]], columns=features)
        
        lr_pred_future = lr_model.predict(next_input)[0]
        rf_pred_future = rf_model.predict(next_input)[0]
        
        lr_future_pred.append(lr_pred_future)
        rf_future_pred.append(rf_pred_future)
        
        # Update lag for next prediction
        last_level = (lr_pred_future + rf_pred_future) / 2


    # Plot future predictions
    fig_future = go.Figure()
    
    fig_future.add_trace(
        go.Scatter(
            x=res_df['Date'].tail(30),
            y=res_df['Level'].tail(30),
            name="Historical Data",
            line=dict(color="#1f77b4", width=2)
        )
    )
    
    fig_future.add_trace(
        go.Scatter(
            x=future_dates,
            y=lr_future_pred,
            name="Linear Regression Future",
            line=dict(color="#ff7f0e", width=3, dash="dash")
        )
    )
    
    fig_future.add_trace(
        go.Scatter(
            x=future_dates,
            y=rf_future_pred,
            name="Random Forest Future",
            line=dict(color="#2ca02c", width=3, dash="dash")
        )
    )
    
    fig_future.update_layout(
        title=f"Future {future_days}-Day Reservoir Level Predictions",
        xaxis_title="Date",
        yaxis_title="Reservoir Level",
        height=400
    )
    st.plotly_chart(fig_future, use_container_width=True)


    # ==========================================
    # MODEL COMPARISON SUMMARY
    # ==========================================

    st.markdown("---")
    st.subheader("📋 Model Comparison Summary")
    
    comparison_df = pd.DataFrame({
        "Metric": ["MAE", "RMSE", "R² Score"],
        "Linear Regression": [lr_mae, lr_rmse, lr_r2],
        "Random Forest": [rf_mae, rf_rmse, rf_r2]
    })
    
    # Highlight best model for each metric
    best_models = []
    for metric in comparison_df['Metric']:
        lr_val = comparison_df.loc[comparison_df['Metric'] == metric, 'Linear Regression'].iloc[0]
        rf_val = comparison_df.loc[comparison_df['Metric'] == metric, 'Random Forest'].iloc[0]
        
        if metric in ["MAE", "RMSE"]:
            best = "Linear Regression" if lr_val < rf_val else "Random Forest"
        else:
            best = "Linear Regression" if lr_val > rf_val else "Random Forest"
        
        best_models.append(best)
    
    comparison_df['Best Model'] = best_models
    
    st.dataframe(comparison_df.set_index('Metric').round(4), use_container_width=True)
    
    # Conclusion
    rf_better = sum(1 for a, b in zip([lr_mae, lr_rmse], [rf_mae, rf_rmse]) if b < a)
    rf_better += 1 if rf_r2 > lr_r2 else 0
    
    conclusion = f"**Random Forest** is better in {rf_better}/3 metrics" if rf_better > 1.5 else f"**Linear Regression** is better in {3 - rf_better}/3 metrics"
    st.info(conclusion)


else:
    st.warning("Not enough data for this reservoir to train ML models.")


# Footer
st.markdown("---")
st.markdown(
    "<center>© 2024 AquaSense AI - ML Predictions Dashboard</center>",
    unsafe_allow_html=True
)
