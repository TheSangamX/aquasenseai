"""
Reports Page - AquaSense AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
from io import BytesIO
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import data_loader


# Set page config
st.set_page_config(
    page_title="Reports - AquaSense AI",
    page_icon="📄",
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
st.title("📄 Reports & Exports")
st.markdown("---")


# Sidebar for report configuration
st.sidebar.title("⚙️ Report Settings")

# Report type
report_type = st.sidebar.selectbox(
    "Select Report Type",
    options=[
        "Full Reservoir Report",
        "Basin-wise Report",
        "Risk Assessment Report",
        "Summary Statistics Report"
    ]
)

# Filter options
selected_basins = st.sidebar.multiselect(
    "Filter by Basin (Optional)",
    options=sorted(df['Basin'].unique()),
    default=[]
)

selected_reservoirs = st.sidebar.multiselect(
    "Filter by Reservoir (Optional)",
    options=sorted(df['Reservoir_Name'].unique()),
    default=[]
)

# Export format
export_format = st.sidebar.radio(
    "Export Format",
    options=["CSV", "Excel", "JSON"],
    index=0
)


# Filter data
filtered_df = data_loader.filter_data(
    df,
    reservoirs=selected_reservoirs if selected_reservoirs else None,
    basins=selected_basins if selected_basins else None
)


# Generate reports based on type
st.subheader(f"📊 {report_type}")

if report_type == "Full Reservoir Report":
    # Show full report
    st.dataframe(filtered_df, use_container_width=True)

elif report_type == "Basin-wise Report":
    basin_report = filtered_df.groupby('Basin').agg({
        'Reservoir_Name': 'nunique',
        'Storage': ['mean', 'min', 'max'],
        'Level': ['mean', 'min', 'max'],
        'Storage_Percentage': ['mean', 'min', 'max']
    }).round(2)
    
    basin_report.columns = ['_'.join(col).strip() for col in basin_report.columns.values]
    basin_report = basin_report.reset_index()
    
    st.dataframe(basin_report, use_container_width=True)

elif report_type == "Risk Assessment Report":
    # Calculate risks
    latest_data = filtered_df.sort_values('Date').groupby('Reservoir_Name').last().reset_index()
    
    def calculate_flood_risk(row):
        try:
            level_ratio = row['Level'] / row['Full_Reservoir_Level']
            if level_ratio >= 0.95:
                return "Critical"
            elif level_ratio >= 0.85:
                return "High"
            elif level_ratio >= 0.7:
                return "Medium"
            else:
                return "Low"
        except:
            return "Unknown"
    
    def calculate_drought_risk(row):
        storage_pct = row['Storage_Percentage']
        if storage_pct < 20:
            return "Critical"
        elif storage_pct < 35:
            return "High"
        elif storage_pct < 50:
            return "Medium"
        else:
            return "Low"
    
    latest_data['Flood_Risk'] = latest_data.apply(calculate_flood_risk, axis=1)
    latest_data['Drought_Risk'] = latest_data.apply(calculate_drought_risk, axis=1)
    
    risk_report = latest_data[[
        'Reservoir_Name', 'Basin', 'Date', 'Storage', 'Level',
        'Storage_Percentage', 'Flood_Risk', 'Drought_Risk'
    ]]
    
    st.dataframe(risk_report, use_container_width=True)

elif report_type == "Summary Statistics Report":
    summary_report = filtered_df.describe(include='all').round(4)
    st.dataframe(summary_report, use_container_width=True)


# Export functionality
st.markdown("---")
st.subheader("📥 Export Data")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    # Prepare data for export
    if report_type == "Full Reservoir Report":
        export_df = filtered_df
    elif report_type == "Basin-wise Report":
        export_df = filtered_df.groupby('Basin').agg({
            'Reservoir_Name': 'nunique',
            'Storage': ['mean', 'min', 'max'],
            'Level': ['mean', 'min', 'max'],
            'Storage_Percentage': ['mean', 'min', 'max']
        }).round(2)
        export_df.columns = ['_'.join(col).strip() for col in export_df.columns.values]
        export_df = export_df.reset_index()
    elif report_type == "Risk Assessment Report":
        latest_data = filtered_df.sort_values('Date').groupby('Reservoir_Name').last().reset_index()
        
        def calculate_flood_risk(row):
            try:
                level_ratio = row['Level'] / row['Full_Reservoir_Level']
                if level_ratio >= 0.95:
                    return "Critical"
                elif level_ratio >= 0.85:
                    return "High"
                elif level_ratio >= 0.7:
                    return "Medium"
                else:
                    return "Low"
            except:
                return "Unknown"
        
        def calculate_drought_risk(row):
            storage_pct = row['Storage_Percentage']
            if storage_pct < 20:
                return "Critical"
            elif storage_pct < 35:
                return "High"
            elif storage_pct < 50:
                return "Medium"
            else:
                return "Low"
        
        latest_data['Flood_Risk'] = latest_data.apply(calculate_flood_risk, axis=1)
        latest_data['Drought_Risk'] = latest_data.apply(calculate_drought_risk, axis=1)
        
        export_df = latest_data[[
            'Reservoir_Name', 'Basin', 'Date', 'Storage', 'Level',
            'Storage_Percentage', 'Flood_Risk', 'Drought_Risk'
        ]]
    elif report_type == "Summary Statistics Report":
        export_df = filtered_df.describe(include='all').round(4)
        export_df = export_df.reset_index()

    if export_format == "CSV":
        csv_data = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"aqua_sense_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv'
        )
    
    elif export_format == "Excel":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            export_df.to_excel(writer, index=False, sheet_name='Report')
        excel_data = output.getvalue()
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=f"aqua_sense_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    elif export_format == "JSON":
        json_data = export_df.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"aqua_sense_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime='application/json'
        )


# Report Summary
st.markdown("---")
st.subheader("📈 Report Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Records",
        value=f"{len(filtered_df)}"
    )

with col2:
    st.metric(
        label="Unique Reservoirs",
        value=f"{filtered_df['Reservoir_Name'].nunique()}"
    )

with col3:
    st.metric(
        label="Unique Basins",
        value=f"{filtered_df['Basin'].nunique()}"
    )

with col4:
    st.metric(
        label="Date Range",
        value=f"{filtered_df['Date'].min().date()} - {filtered_df['Date'].max().date()}"
    )


# Quick Reports section
st.markdown("---")
st.subheader("⚡ Quick Reports")

quick_col1, quick_col2 = st.columns(2)

with quick_col1:
    if st.button("Download All Reservoir Data"):
        all_data_csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Confirm Download All Data (CSV)",
            data=all_data_csv,
            file_name=f"aqua_sense_all_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv'
        )

with quick_col2:
    if st.button("Download Latest Status"):
        latest_status = df.sort_values('Date').groupby('Reservoir_Name').last().reset_index()
        latest_csv = latest_status.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Confirm Download Latest Status (CSV)",
            data=latest_csv,
            file_name=f"aqua_sense_latest_status_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv'
        )


# Footer
st.markdown("---")
st.markdown(
    "<center>© 2024 AquaSense AI - Reports Dashboard</center>",
    unsafe_allow_html=True
)
