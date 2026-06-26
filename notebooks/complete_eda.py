"""
Complete Exploratory Data Analysis (EDA) for AquaSense AI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import eda
import plotly.io as pio
pio.renderers.default = "json"  # Render to JSON for safety

# Create output directory for plots
os.makedirs("eda_plots", exist_ok=True)


def main():
    print("="*80)
    print("AQUASENSE AI - COMPLETE EXPLORATORY DATA ANALYSIS")
    print("="*80)
    
    # 1. Load and preprocess data
    print("\n" + "="*80)
    print("STEP 1: LOADING AND PREPROCESSING DATA")
    print("="*80)
    file_path = "../clean_reservoir_data.xls"
    df = eda.load_data(file_path)
    df = eda.preprocess_data(df)
    print("Data preprocessed successfully!")
    
    # 2. Display dataset information
    print("\n" + "="*80)
    print("STEP 2: DATASET INFORMATION")
    print("="*80)
    eda.display_dataset_info(df)
    
    # 3. Check missing values
    print("\n" + "="*80)
    print("STEP 3: MISSING VALUES")
    print("="*80)
    missing_df = eda.check_missing_values(df)
    print("\nMissing values summary:")
    print(missing_df.to_string())
    fig_missing = eda.plot_missing_values(missing_df)
    fig_missing.write_html("eda_plots/01_missing_values.html")
    print("Plot saved: eda_plots/01_missing_values.html")
    
    # 4. Check duplicates
    print("\n" + "="*80)
    print("STEP 4: DUPLICATE ROWS")
    print("="*80)
    num_duplicates = eda.check_duplicates(df)
    print(f"Number of duplicate rows: {num_duplicates}")
    
    # 5. Summary statistics
    print("\n" + "="*80)
    print("STEP 5: SUMMARY STATISTICS")
    print("="*80)
    summary_stats = eda.summary_statistics(df)
    print(summary_stats.to_string())
    
    # 6. Unique reservoirs and basins
    print("\n" + "="*80)
    print("STEP 6: UNIQUE VALUES")
    print("="*80)
    num_reservoirs = eda.get_unique_reservoirs(df)
    reservoir_list = eda.get_reservoir_list(df)
    num_basins = eda.get_unique_basins(df)
    basin_list = eda.get_basin_list(df)
    
    print(f"Number of unique reservoirs: {num_reservoirs}")
    print(f"List of reservoirs: {', '.join(reservoir_list[:5])}...")
    print(f"\nNumber of unique basins: {num_basins}")
    print(f"List of basins: {', '.join(basin_list)}")
    
    # 7. Date range
    print("\n" + "="*80)
    print("STEP 7: DATE RANGE")
    print("="*80)
    min_date, max_date = eda.get_date_range(df)
    print(f"Data spans from: {min_date.date()} to {max_date.date()}")
    print(f"Duration: {(max_date - min_date).days} days ({((max_date - min_date).days/365.25):.1f} years)")
    
    # 8. Averages
    print("\n" + "="*80)
    print("STEP 8: OVERALL AVERAGES")
    print("="*80)
    avg_storage = eda.get_average_storage(df)
    avg_level = eda.get_average_level(df)
    print(f"Average Storage: {avg_storage:.2f}")
    print(f"Average Level: {avg_level:.2f}")
    
    # 9. Top reservoirs
    print("\n" + "="*80)
    print("STEP 9: TOP RESERVOIRS")
    print("="*80)
    top_storage = eda.get_top_reservoirs_by_avg_storage(df, 10)
    top_level = eda.get_top_reservoirs_by_avg_level(df, 10)
    
    print("\nTop 10 Reservoirs by Average Storage:")
    print(top_storage.to_string(index=False))
    fig_top_storage = eda.plot_top_reservoirs_by_storage(top_storage)
    fig_top_storage.write_html("eda_plots/02_top_reservoirs_storage.html")
    print("Plot saved: eda_plots/02_top_reservoirs_storage.html")
    
    print("\nTop 10 Reservoirs by Average Level:")
    print(top_level.to_string(index=False))
    fig_top_level = eda.plot_top_reservoirs_by_level(top_level)
    fig_top_level.write_html("eda_plots/03_top_reservoirs_level.html")
    print("Plot saved: eda_plots/03_top_reservoirs_level.html")
    
    # 10. Basin-wise summary
    print("\n" + "="*80)
    print("STEP 10: BASIN-WISE SUMMARY")
    print("="*80)
    basin_summary = eda.get_basin_wise_summary(df)
    print(basin_summary.to_string())
    fig_basin = eda.plot_basin_wise_reservoirs(basin_summary)
    fig_basin.write_html("eda_plots/04_basin_wise_reservoirs.html")
    print("Plot saved: eda_plots/04_basin_wise_reservoirs.html")
    
    # 11. Monthly and yearly trends
    print("\n" + "="*80)
    print("STEP 11: TRENDS ANALYSIS")
    print("="*80)
    monthly = eda.get_monthly_trends(df)
    yearly = eda.get_yearly_trends(df)
    
    print("\nMonthly trends (first 10 rows):")
    print(monthly.head(10).to_string(index=False))
    fig_monthly = eda.plot_monthly_trends(monthly)
    fig_monthly.write_html("eda_plots/05_monthly_trends.html")
    print("Plot saved: eda_plots/05_monthly_trends.html")
    
    print("\nYearly trends:")
    print(yearly.to_string(index=False))
    fig_yearly = eda.plot_yearly_trends(yearly)
    fig_yearly.write_html("eda_plots/06_yearly_trends.html")
    print("Plot saved: eda_plots/06_yearly_trends.html")
    
    # 12. Distributions
    print("\n" + "="*80)
    print("STEP 12: DISTRIBUTIONS")
    print("="*80)
    fig_dist = eda.plot_distribution_numerical(df)
    fig_dist.write_html("eda_plots/07_numerical_distributions.html")
    print("Plot saved: eda_plots/07_numerical_distributions.html")
    
    # 13. Correlations
    print("\n" + "="*80)
    print("STEP 13: CORRELATIONS")
    print("="*80)
    fig_corr = eda.plot_storage_vs_level(df)
    fig_corr.write_html("eda_plots/08_storage_vs_level.html")
    print("Plot saved: eda_plots/08_storage_vs_level.html")
    
    # 14. Reservoir locations
    print("\n" + "="*80)
    print("STEP 14: RESERVOIR LOCATIONS")
    print("="*80)
    fig_map = eda.plot_reservoir_locations(df)
    fig_map.write_html("eda_plots/09_reservoir_locations.html")
    print("Plot saved: eda_plots/09_reservoir_locations.html")
    
    print("\n" + "="*80)
    print("EDA COMPLETED SUCCESSFULLY!")
    print("="*80)


if __name__ == "__main__":
    main()
