"""
Analytics Page - AquaSense AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import data_loader
from utils.auth import require_login, render_auth_sidebar


# Set page config
st.set_page_config(
    page_title="Analytics - AquaSense AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

require_login(post_login_page="pages/2_📊_Analytics.py")
render_auth_sidebar()


# Load data with caching
@st.cache_data
def load_data():
    df = data_loader.load_reservoir_data("clean_reservoir_data.xls")
    df = data_loader.preprocess_data(df)
    return df


df = load_data()


# Sidebar filters for analytics
st.sidebar.title("🔍 Analysis Filters")

# Reservoir filter
selected_reservoirs_analytics = st.sidebar.multiselect(
    "Select Reservoir(s)",
    options=sorted(df['Reservoir_Name'].unique()),
    default=[]
)

# Basin filter
selected_basins_analytics = st.sidebar.multiselect(
    "Select Basin(s)",
    options=sorted(df['Basin'].unique()),
    default=[]
)


# Filter data
filtered_df_analytics = data_loader.filter_data(
    df,
    reservoirs=selected_reservoirs_analytics if selected_reservoirs_analytics else None,
    basins=selected_basins_analytics if selected_basins_analytics else None
)


# Page title
st.title("📊 Data Analytics")
st.markdown("---")


# Summary Statistics
st.subheader("📋 Summary Statistics")
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Display descriptive statistics
        st.dataframe(
            filtered_df_analytics.describe(include='all').round(2),
            use_container_width=True
        )


# Visualization section
st.markdown("---")
st.subheader("📈 Advanced Visualizations")

# Row 1: Reservoir Comparison + Time Series
comp_col, ts_col = st.columns([1, 1])

with comp_col:
    st.markdown("#### 📊 Reservoir Comparison")
    
    # Top 10 reservoirs by average storage
    top_reservoirs = filtered_df_analytics.groupby('Reservoir_Name')['Storage'].mean().sort_values(ascending=False).head(10).reset_index()
    
    if len(top_reservoirs) > 0:
        fig_compare = px.bar(
            top_reservoirs,
            x='Storage',
            y='Reservoir_Name',
            orientation='h',
            title='Top 10 Reservoirs by Average Storage',
            color='Storage',
            color_continuous_scale='Blues',
            height=400
        )
        fig_compare.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_compare, use_container_width=True)
    else:
        st.info("No data to display")


with ts_col:
    st.markdown("#### 📉 Storage Over Time")
    
    if len(filtered_df_analytics) > 0:
        # Time series
        fig_ts = px.line(
            filtered_df_analytics.sort_values('Date'),
            x='Date',
            y='Storage',
            color='Reservoir_Name',
            title='Reservoir Storage Over Time',
            hover_data={'Level': ':.2f', 'Basin': True},
            height=400
        )
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.info("No data to display")


# Row 2: Correlation Matrix + Seasonal Patterns
corr_col, season_col = st.columns([1, 1])

with corr_col:
    st.markdown("#### 🔗 Correlation Heatmap")
    
    if len(filtered_df_analytics) > 0:
        # Compute correlation matrix
        corr_matrix = filtered_df_analytics[['Storage', 'Level', 'Full_Reservoir_Level', 'Live_Capacity_FRL', 'Storage_Percentage']].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu',
            title='Correlation Matrix',
            height=400
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("No data to display")


with season_col:
    st.markdown("#### 🌦️ Monthly Patterns")
    
    if len(filtered_df_analytics) > 0:
        # Monthly averages
        monthly_patterns = filtered_df_analytics.groupby('Month').agg(
            {'Storage': 'mean', 'Level': 'mean'}
        ).reset_index()
        
        month_names = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
            5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
            9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
        monthly_patterns['Month_Name'] = monthly_patterns['Month'].map(month_names)
        
        fig_season = px.bar(
            monthly_patterns,
            x='Month_Name',
            y=['Storage', 'Level'],
            barmode='group',
            title='Average Storage & Level by Month',
            height=400,
            color_discrete_map={'Storage': '#1f77b4', 'Level': '#ff7f0e'}
        )
        st.plotly_chart(fig_season, use_container_width=True)
    else:
        st.info("No data to display")


# Footer
st.markdown("---")
st.markdown(
    "<center>© 2024 AquaSense AI - Data Analytics Dashboard</center>",
    unsafe_allow_html=True
)
