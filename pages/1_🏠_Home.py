"""
Home Dashboard - AquaSense AI
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
    page_title="AquaSense AI - Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load data with caching
@st.cache_data
def load_data():
    """Load and preprocess data"""
    df = data_loader.load_reservoir_data("clean_reservoir_data.xls")
    df = data_loader.preprocess_data(df)
    return df


# Load data
df = load_data()


# Sidebar filters
st.sidebar.title("🔍 Filters")

# Reservoir filter
all_reservoirs = sorted(df['Reservoir_Name'].unique())
selected_reservoirs = st.sidebar.multiselect(
    "Select Reservoir(s)",
    options=all_reservoirs,
    default=[]
)

# Basin filter
all_basins = sorted(df['Basin'].unique())
selected_basins = st.sidebar.multiselect(
    "Select Basin(s)",
    options=all_basins,
    default=[]
)

# Year filter
all_years = sorted(df['Year'].unique())
selected_years = st.sidebar.multiselect(
    "Select Year(s)",
    options=all_years,
    default=all_years
)

# Month filter
all_months = sorted(df['Month'].unique())
month_names = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
selected_months = st.sidebar.multiselect(
    "Select Month(s)",
    options=all_months,
    default=all_months,
    format_func=lambda x: month_names[x]
)


# Filter the data
filtered_df = data_loader.filter_data(
    df,
    reservoirs=selected_reservoirs if selected_reservoirs else None,
    basins=selected_basins if selected_basins else None,
    years=selected_years if selected_years else None,
    months=selected_months if selected_months else None
)


# Main dashboard title
st.title("💧 AquaSense AI - Smart Reservoir Monitoring")
st.markdown("---")


# KPI Cards
st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

total_reservoirs = filtered_df['Reservoir_Name'].nunique()
avg_storage = filtered_df['Storage'].mean()
avg_level = filtered_df['Level'].mean()
max_storage = filtered_df['Storage'].max()
min_storage = filtered_df['Storage'].min()

with col1:
    st.metric(
        label="Total Reservoirs",
        value=f"{total_reservoirs}",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="Average Storage",
        value=f"{avg_storage:.4f}"
    )

with col3:
    st.metric(
        label="Average Level",
        value=f"{avg_level:.2f}"
    )

with col4:
    st.metric(
        label="Highest Storage",
        value=f"{max_storage:.4f}",
        delta=f"{max_storage - avg_storage:.4f}"
    )

with col5:
    st.metric(
        label="Lowest Storage",
        value=f"{min_storage:.4f}",
        delta=f"{min_storage - avg_storage:.4f}",
        delta_color="inverse"
    )

st.markdown("---")


# Charts section
st.subheader("📈 Data Visualizations")

# Row 1: Map + Pie Chart
map_col, pie_col = st.columns([2, 1])

with map_col:
    st.markdown("#### 🗺️ Reservoir Locations")
    # Get latest data per reservoir for map
    latest_per_reservoir = filtered_df.sort_values('Date').groupby('Reservoir_Name').last().reset_index()
    
    if len(latest_per_reservoir) > 0:
        fig_map = px.scatter_mapbox(
            latest_per_reservoir,
            lat='Lat',
            lon='Long',
            hover_name='Reservoir_Name',
            hover_data={
                'Basin': True,
                'Storage': ':.4f',
                'Level': ':.2f',
                'Storage_Percentage': ':.2f',
                'Lat': False,
                'Long': False
            },
            color='Storage_Percentage',
            size='Live_Capacity_FRL',
            color_continuous_scale='RdYlGn',
            zoom=4,
            height=500,
            title='Reservoir Status by Location'
        )
        fig_map.update_layout(mapbox_style='carto-positron')
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No data to display on map")

with pie_col:
    st.markdown("#### 🥧 Storage by Basin")
    basin_storage = filtered_df.groupby('Basin')['Storage'].sum().reset_index()
    if len(basin_storage) > 0:
        fig_pie = px.pie(
            basin_storage,
            values='Storage',
            names='Basin',
            title='Total Storage by Basin',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data to display")


# Row 2: Line Chart + Bar Chart
line_col, bar_col = st.columns([1, 1])

with line_col:
    st.markdown("#### 📉 Monthly Trend")
    # Get monthly averages
    monthly_avg = filtered_df.groupby(['Year', 'Month']).agg(
        {'Storage': 'mean', 'Level': 'mean'}
    ).reset_index()
    monthly_avg['Date'] = pd.to_datetime(
        monthly_avg[['Year', 'Month']].assign(Day=1)
    )
    
    if len(monthly_avg) > 0:
        fig_line = go.Figure()
        fig_line.add_trace(
            go.Scatter(
                x=monthly_avg['Date'],
                y=monthly_avg['Storage'],
                name='Storage',
                line=dict(color='#1f77b4', width=3),
                mode='lines+markers'
            )
        )
        fig_line.add_trace(
            go.Scatter(
                x=monthly_avg['Date'],
                y=monthly_avg['Level'],
                name='Level',
                line=dict(color='#ff7f0e', width=3),
                mode='lines+markers',
                yaxis='y2'
            )
        )
        fig_line.update_layout(
            title='Monthly Average Storage & Level',
            xaxis_title='Date',
            yaxis_title='Storage',
            yaxis2=dict(
                title='Level',
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0, y=1.1, orientation='h'),
            height=400
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No data to display")

with bar_col:
    st.markdown("#### 📊 Basin Analysis")
    basin_analysis = filtered_df.groupby('Basin').agg(
        {'Storage': 'mean', 'Level': 'mean'}
    ).reset_index()
    basin_analysis = basin_analysis.sort_values('Storage', ascending=False)
    
    if len(basin_analysis) > 0:
        fig_bar = px.bar(
            basin_analysis,
            x='Basin',
            y='Storage',
            color='Basin',
            title='Average Storage by Basin',
            color_discrete_sequence=px.colors.qualitative.D3,
            hover_data={'Level': ':.2f'}
        )
        fig_bar.update_layout(
            xaxis_tickangle=-45,
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No data to display")


# Row 3: Histogram + Scatter Plot
hist_col, scatter_col = st.columns([1, 1])

with hist_col:
    st.markdown("#### 📶 Storage Distribution")
    if len(filtered_df) > 0:
        fig_hist = px.histogram(
            filtered_df,
            x='Storage_Percentage',
            nbins=30,
            title='Distribution of Storage Percentage',
            color_discrete_sequence=['#17becf']
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No data to display")

with scatter_col:
    st.markdown("#### ⚡ Storage vs Level")
    if len(filtered_df) > 0:
        fig_scatter = px.scatter(
            filtered_df,
            x='Level',
            y='Storage',
            color='Basin',
            size='Live_Capacity_FRL',
            title='Storage vs Level Correlation',
            hover_data={'Reservoir_Name': True},
            color_discrete_sequence=px.colors.qualitative.Pastel,
            opacity=0.7
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No data to display")


# Footer
st.markdown("---")
st.markdown(
    "<center>© 2024 AquaSense AI - Smart Reservoir Monitoring System</center>",
    unsafe_allow_html=True
)
