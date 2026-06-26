"""
Exploratory Data Analysis (EDA) Module
Responsibility: Functions for loading, inspecting, and visualizing the dataset
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load the reservoir dataset (handles both .xls (CSV) and actual Excel)
    """
    try:
        # Try as CSV first (since our file is CSV with .xls extension)
        df = pd.read_csv(file_path, delimiter=',', engine='python')
        print(f"Successfully loaded as CSV. Shape: {df.shape}")
        return df
    except Exception:
        try:
            # Try with xlrd
            df = pd.read_excel(file_path, engine='xlrd')
            print(f"Successfully loaded as Excel (xlrd). Shape: {df.shape}")
            return df
        except Exception as e:
            print(f"Failed to load data: {e}")
            raise


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the dataset: convert date column, handle types
    """
    df = df.copy()
    
    # Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Calculate storage percentage
    df['Storage_Percentage'] = (df['Storage'] / df['Live_Capacity_FRL']) * 100
    
    return df


def display_dataset_info(df: pd.DataFrame) -> None:
    """
    Display comprehensive dataset information
    """
    print("="*60)
    print("DATASET OVERVIEW")
    print("="*60)
    print(f"Shape (rows, columns): {df.shape}")
    print("\n" + "="*60)
    print("DATA TYPES")
    print("="*60)
    print(df.dtypes)
    print("\n" + "="*60)
    print("FIRST 10 ROWS")
    print("="*60)
    print(df.head(10).to_string())
    print("\n" + "="*60)
    print("LAST 10 ROWS")
    print("="*60)
    print(df.tail(10).to_string())


def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check for missing values in the dataset
    """
    missing = df.isnull().sum().sort_values(ascending=False)
    missing_percent = (missing / len(df)) * 100
    missing_df = pd.DataFrame({
        'Missing Count': missing,
        'Missing Percentage': missing_percent.round(2)
    })
    return missing_df


def check_duplicates(df: pd.DataFrame) -> int:
    """
    Check for duplicate rows
    """
    return df.duplicated().sum()


def summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary statistics for numerical columns
    """
    return df.describe(include='all').transpose()


def get_unique_reservoirs(df: pd.DataFrame) -> int:
    """
    Get number of unique reservoirs
    """
    return df['Reservoir_Name'].nunique()


def get_reservoir_list(df: pd.DataFrame) -> list:
    """
    Get list of unique reservoirs
    """
    return sorted(df['Reservoir_Name'].unique())


def get_unique_basins(df: pd.DataFrame) -> int:
    """
    Get number of unique basins
    """
    return df['Basin'].nunique()


def get_basin_list(df: pd.DataFrame) -> list:
    """
    Get list of unique basins
    """
    return sorted(df['Basin'].unique())


def get_date_range(df: pd.DataFrame) -> tuple:
    """
    Get min and max dates
    """
    return df['Date'].min(), df['Date'].max()


def get_average_storage(df: pd.DataFrame) -> float:
    """
    Get overall average storage
    """
    return df['Storage'].mean()


def get_average_level(df: pd.DataFrame) -> float:
    """
    Get overall average level
    """
    return df['Level'].mean()


def get_top_reservoirs_by_avg_storage(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Get top N reservoirs by average storage
    """
    top = df.groupby('Reservoir_Name')['Storage'].mean().sort_values(ascending=False).head(n)
    return pd.DataFrame({
        'Reservoir_Name': top.index,
        'Average_Storage': top.values
    })


def get_top_reservoirs_by_avg_level(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Get top N reservoirs by average level
    """
    top = df.groupby('Reservoir_Name')['Level'].mean().sort_values(ascending=False).head(n)
    return pd.DataFrame({
        'Reservoir_Name': top.index,
        'Average_Level': top.values
    })


def get_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get monthly average storage and level
    """
    monthly = df.groupby(['Year', 'Month']).agg({
        'Storage': 'mean',
        'Level': 'mean',
        'Storage_Percentage': 'mean'
    }).reset_index()
    # Create a date column for plotting
    monthly['Date'] = pd.to_datetime(monthly[['Year', 'Month']].assign(Day=1))
    return monthly


def get_yearly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get yearly average storage and level
    """
    yearly = df.groupby('Year').agg({
        'Storage': 'mean',
        'Level': 'mean',
        'Storage_Percentage': 'mean'
    }).reset_index()
    return yearly


def get_basin_wise_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get summary statistics per basin
    """
    basin_summary = df.groupby('Basin').agg({
        'Reservoir_Name': 'nunique',
        'Storage': ['mean', 'median', 'min', 'max', 'std'],
        'Level': ['mean', 'median', 'min', 'max', 'std'],
        'Storage_Percentage': ['mean', 'median', 'min', 'max', 'std']
    }).round(2)
    basin_summary.columns = ['_'.join(col).strip() for col in basin_summary.columns.values]
    basin_summary = basin_summary.rename(columns={'Reservoir_Name_nunique': 'Number_of_Reservoirs'})
    return basin_summary


# === PLOTTING FUNCTIONS ===

def plot_missing_values(missing_df: pd.DataFrame) -> go.Figure:
    """
    Plot missing values
    """
    fig = px.bar(
        missing_df,
        x=missing_df.index,
        y='Missing Percentage',
        title='Missing Values by Column',
        labels={'index': 'Column', 'Missing Percentage': 'Percentage Missing (%)'},
        color='Missing Percentage',
        color_continuous_scale='Reds'
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_distribution_numerical(df: pd.DataFrame) -> go.Figure:
    """
    Plot distribution of numerical columns
    """
    num_cols = ['Storage', 'Level', 'Full_Reservoir_Level', 'Live_Capacity_FRL', 'Storage_Percentage']
    num_cols = [col for col in num_cols if col in df.columns]
    
    fig = make_subplots(rows=len(num_cols), cols=1, 
                        subplot_titles=[f'Distribution of {col}' for col in num_cols],
                        vertical_spacing=0.08)
    
    for i, col in enumerate(num_cols, 1):
        fig.add_trace(
            go.Histogram(x=df[col], name=col, nbinsx=30),
            row=i, col=1
        )
    
    fig.update_layout(height=300*len(num_cols), title_text='Distributions of Numerical Variables', showlegend=False)
    return fig


def plot_monthly_trends(monthly: pd.DataFrame) -> go.Figure:
    """
    Plot monthly trends of storage and level
    """
    fig = make_subplots(rows=2, cols=1, 
                        subplot_titles=['Monthly Average Storage', 'Monthly Average Level'],
                        shared_xaxes=True,
                        vertical_spacing=0.1)
    
    fig.add_trace(
        go.Scatter(x=monthly['Date'], y=monthly['Storage'], name='Storage', line=dict(color='blue')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=monthly['Date'], y=monthly['Level'], name='Level', line=dict(color='green')),
        row=2, col=1
    )
    
    fig.update_layout(height=600, title_text='Monthly Trends')
    return fig


def plot_top_reservoirs_by_storage(top_df: pd.DataFrame) -> go.Figure:
    """
    Plot top reservoirs by average storage
    """
    fig = px.bar(
        top_df,
        x='Average_Storage',
        y='Reservoir_Name',
        orientation='h',
        title='Top 10 Reservoirs by Average Storage',
        color='Average_Storage',
        color_continuous_scale='Blues',
        labels={'Average_Storage': 'Average Storage', 'Reservoir_Name': 'Reservoir Name'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def plot_top_reservoirs_by_level(top_df: pd.DataFrame) -> go.Figure:
    """
    Plot top reservoirs by average level
    """
    fig = px.bar(
        top_df,
        x='Average_Level',
        y='Reservoir_Name',
        orientation='h',
        title='Top 10 Reservoirs by Average Level',
        color='Average_Level',
        color_continuous_scale='Greens',
        labels={'Average_Level': 'Average Level', 'Reservoir_Name': 'Reservoir Name'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig


def plot_basin_wise_reservoirs(basin_summary: pd.DataFrame) -> go.Figure:
    """
    Plot number of reservoirs per basin
    """
    fig = px.bar(
        basin_summary,
        x=basin_summary.index,
        y='Number_of_Reservoirs',
        title='Number of Reservoirs per Basin',
        color='Number_of_Reservoirs',
        color_continuous_scale='Viridis',
        labels={'index': 'Basin', 'Number_of_Reservoirs': 'Number of Reservoirs'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_storage_vs_level(df: pd.DataFrame) -> go.Figure:
    """
    Plot scatter plot of Storage vs Level
    """
    fig = px.scatter(
        df,
        x='Level',
        y='Storage',
        title='Storage vs Level',
        color='Basin',
        hover_data=['Reservoir_Name', 'Date'],
        opacity=0.6
    )
    return fig


def plot_yearly_trends(yearly: pd.DataFrame) -> go.Figure:
    """
    Plot yearly trends
    """
    fig = make_subplots(rows=2, cols=1, 
                        subplot_titles=['Yearly Average Storage', 'Yearly Average Storage Percentage'],
                        shared_xaxes=True,
                        vertical_spacing=0.1)
    
    fig.add_trace(
        go.Bar(x=yearly['Year'], y=yearly['Storage'], name='Storage', marker_color='darkblue'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=yearly['Year'], y=yearly['Storage_Percentage'], name='Storage %', marker_color='darkorange'),
        row=2, col=1
    )
    
    fig.update_layout(height=600, title_text='Yearly Trends')
    return fig


def plot_reservoir_locations(df: pd.DataFrame) -> go.Figure:
    """
    Plot reservoir locations on a map
    """
    # Get latest data per reservoir
    latest = df.sort_values('Date').groupby('Reservoir_Name').last().reset_index()
    
    fig = px.scatter_mapbox(
        latest,
        lat='Lat',
        lon='Long',
        hover_name='Reservoir_Name',
        hover_data=['Basin', 'Storage', 'Level', 'Storage_Percentage'],
        color='Storage_Percentage',
        size='Live_Capacity_FRL',
        color_continuous_scale='RdYlGn',
        zoom=4,
        height=600,
        title='Reservoir Locations (Latest Data)'
    )
    fig.update_layout(mapbox_style='carto-positron')
    return fig
