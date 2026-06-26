"""
Risk Assessment Page - AquaSense AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import data_loader


# Set page config
st.set_page_config(
    page_title="Risk Assessment - AquaSense AI",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load data with caching
@st.cache_data
def load_data():
    df = data_loader.load_reservoir_data("clean_reservoir_data.xls")
    df = data_loader.preprocess_data(df)
    return df


df = load_data()


# Page title
st.title("⚠️ Risk Assessment")
st.markdown("---")


# Risk calculation functions
def calculate_flood_risk(row):
    """Calculate flood risk based on level vs full reservoir level"""
    try:
        level_ratio = row['Level'] / row['Full_Reservoir_Level']
        if level_ratio >= 0.95:
            return "Critical", "🔴"
        elif level_ratio >= 0.85:
            return "High", "🟠"
        elif level_ratio >= 0.7:
            return "Medium", "🟡"
        else:
            return "Low", "🟢"
    except:
        return "Unknown", "⚪"


def calculate_drought_risk(row):
    """Calculate drought risk based on storage percentage"""
    storage_pct = row['Storage_Percentage']
    if storage_pct < 20:
        return "Critical", "🔴"
    elif storage_pct < 35:
        return "High", "🟠"
    elif storage_pct < 50:
        return "Medium", "🟡"
    else:
        return "Low", "🟢"


# Get latest data per reservoir
latest_data = df.sort_values('Date').groupby('Reservoir_Name').last().reset_index()

# Calculate risks
latest_data[['Flood_Risk', 'Flood_Risk_Icon']] = latest_data.apply(
    lambda x: pd.Series(calculate_flood_risk(x)), axis=1
)
latest_data[['Drought_Risk', 'Drought_Risk_Icon']] = latest_data.apply(
    lambda x: pd.Series(calculate_drought_risk(x)), axis=1
)


# KPI Section
st.subheader("📊 Risk Overview")
col1, col2, col3, col4, col5 = st.columns(5)

# Flood risk counts
flood_counts = latest_data['Flood_Risk'].value_counts()
with col1:
    st.metric(
        label="Critical Flood Risk",
        value=flood_counts.get('Critical', 0),
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="High Flood Risk",
        value=flood_counts.get('High', 0),
        delta_color="inverse"
    )

# Drought risk counts
drought_counts = latest_data['Drought_Risk'].value_counts()
with col3:
    st.metric(
        label="Critical Drought Risk",
        value=drought_counts.get('Critical', 0),
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="High Drought Risk",
        value=drought_counts.get('High', 0),
        delta_color="inverse"
    )

with col5:
    st.metric(
        label="Total Reservoirs",
        value=len(latest_data)
    )

st.markdown("---")


# Risk Visualizations
st.subheader("📈 Risk Visualizations")

# Row 1: Risk Map + Flood Risk Distribution
map_col, flood_col = st.columns([2, 1])

with map_col:
    st.markdown("#### 🗺️ Risk Map")
    # Create risk color map
    def get_risk_color(row):
        if row['Flood_Risk'] == 'Critical' or row['Drought_Risk'] == 'Critical':
            return 'red'
        elif row['Flood_Risk'] == 'High' or row['Drought_Risk'] == 'High':
            return 'orange'
        elif row['Flood_Risk'] == 'Medium' or row['Drought_Risk'] == 'Medium':
            return 'yellow'
        else:
            return 'green'
    
    latest_data['Risk_Color'] = latest_data.apply(get_risk_color, axis=1)
    
    fig_risk_map = px.scatter_mapbox(
        latest_data,
        lat='Lat',
        lon='Long',
        hover_name='Reservoir_Name',
        hover_data={
            'Basin': True,
            'Flood_Risk': True,
            'Drought_Risk': True,
            'Storage_Percentage': ':.2f',
            'Lat': False,
            'Long': False
        },
        color='Risk_Color',
        size='Live_Capacity_FRL',
        color_discrete_map={
            'red': '#dc3545',
            'orange': '#fd7e14',
            'yellow': '#ffc107',
            'green': '#28a745'
        },
        zoom=4,
        height=500,
        title='Reservoir Risk Map'
    )
    fig_risk_map.update_layout(mapbox_style='carto-positron')
    st.plotly_chart(fig_risk_map, use_container_width=True)


with flood_col:
    st.markdown("#### 🌊 Flood Risk Distribution")
    fig_flood = px.pie(
        latest_data,
        names='Flood_Risk',
        title='Flood Risk Levels',
        color='Flood_Risk',
        color_discrete_map={
            'Critical': '#dc3545',
            'High': '#fd7e14',
            'Medium': '#ffc107',
            'Low': '#28a745',
            'Unknown': '#6c757d'
        }
    )
    st.plotly_chart(fig_flood, use_container_width=True)


# Row 2: Drought Risk Distribution + Risk Comparison
drought_col, comp_col = st.columns([1, 2])

with drought_col:
    st.markdown("#### 🏜️ Drought Risk Distribution")
    fig_drought = px.pie(
        latest_data,
        names='Drought_Risk',
        title='Drought Risk Levels',
        color='Drought_Risk',
        color_discrete_map={
            'Critical': '#dc3545',
            'High': '#fd7e14',
            'Medium': '#ffc107',
            'Low': '#28a745',
            'Unknown': '#6c757d'
        }
    )
    st.plotly_chart(fig_drought, use_container_width=True)


with comp_col:
    st.markdown("#### 📊 Risk by Basin")
    # Basin-wise risk counts
    basin_risk = latest_data.groupby('Basin').agg({
        'Reservoir_Name': 'count',
        'Storage_Percentage': 'mean'
    }).reset_index()
    basin_risk.columns = ['Basin', 'Reservoir_Count', 'Avg_Storage_Percentage']
    
    fig_basin_risk = px.bar(
        basin_risk.sort_values('Avg_Storage_Percentage', ascending=False),
        x='Basin',
        y='Avg_Storage_Percentage',
        title='Average Storage Percentage by Basin',
        color='Avg_Storage_Percentage',
        color_continuous_scale='RdYlGn',
        height=400
    )
    fig_basin_risk.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_basin_risk, use_container_width=True)


# Alert Table
st.markdown("---")
st.subheader("🔔 Risk Alerts")

# Show critical and high risk reservoirs
alert_reservoirs = latest_data[
    (latest_data['Flood_Risk'].isin(['Critical', 'High'])) | 
    (latest_data['Drought_Risk'].isin(['Critical', 'High']))
][[
    'Reservoir_Name', 'Basin', 'Storage_Percentage', 'Level', 
    'Full_Reservoir_Level', 'Flood_Risk', 'Flood_Risk_Icon',
    'Drought_Risk', 'Drought_Risk_Icon', 'Date'
]].sort_values('Storage_Percentage')

if len(alert_reservoirs) > 0:
    st.dataframe(
        alert_reservoirs.style.format({
            'Storage_Percentage': '{:.2f}%',
            'Level': '{:.2f}',
            'Full_Reservoir_Level': '{:.2f}'
        }),
        use_container_width=True
    )
else:
    st.success("No high or critical risk alerts at the moment!")


# Recommendations
st.markdown("---")
st.subheader("💡 Recommendations")

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌊 Flood Risk Recommendations")
        st.info("""
        - Monitor reservoirs with **Critical/High** flood risk closely
        - Release water gradually if levels exceed 90% of FRL
        - Alert local authorities and communities
        - Activate emergency flood preparedness plans
        """)
    
    with col2:
        st.markdown("#### 🏜️ Drought Risk Recommendations")
        st.warning("""
        - Implement water conservation measures for critical risk areas
        - Prioritize water allocation for essential needs
        - Promote efficient irrigation techniques
        - Consider cloud seeding or groundwater recharge programs
        """)


# Footer
st.markdown("---")
st.markdown(
    "<center>© 2024 AquaSense AI - Risk Assessment Dashboard</center>",
    unsafe_allow_html=True
)
