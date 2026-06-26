"""
AquaSense AI - Main Application Entry Point

Smart Reservoir Monitoring & Prediction System
Built for hackathons and production use.
"""

import streamlit as st
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    # Page configuration
    st.set_page_config(
        page_title="AquaSense AI",
        page_icon="💧",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/',
            'Report a bug': "https://github.com/",
            'About': "# AquaSense AI\nSmart Reservoir Monitoring & Prediction System"
        }
    )

    from utils.auth import redirect_after_login, render_auth_sidebar, require_login

    require_login()
    redirect_after_login(default_page="pages/1_🏠_Home.py")
    render_auth_sidebar()

    # Title section
    st.title("💧 AquaSense AI")
    st.subheader("Smart Reservoir Monitoring & Prediction System")
    st.markdown("---")

    # Welcome content
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            Welcome to **AquaSense AI** - your intelligent companion for reservoir management!
            
            ### 🌟 Key Features
            - 🏠 **Home Dashboard** - Real-time status and monitoring
            - 📊 **Analytics** - Historical trends and patterns
            - 🤖 **Predictions** - AI-powered forecasts
            - ⚠️ **Risk Assessment** - Flood/drought risk analysis
            - 📄 **Reports** - Generate and download reports
            - 🧠 **Intelligent Analytics** - Health scores and AI insights
            - 🤖 **ML Predictions** - Machine learning models
            
            ### 🚀 Get Started
            Use the sidebar to explore different sections of the application!
            """)
        
        with col2:
            st.info("""
            💡 **Quick Tip**: 
            - Go to **Home** for an overview
            - Try **ML Predictions** for AI forecasts
            - Check **Intelligent Analytics** for smart insights
            """)
    
    st.markdown("---")

    # Quick metrics at a glance
    try:
        from utils import data_loader
        
        @st.cache_data(ttl=3600)  # Cache for 1 hour
        def get_quick_stats():
            df = data_loader.load_reservoir_data("clean_reservoir_data.xls")
            df = data_loader.preprocess_data(df)
            return {
                "total_reservoirs": df['Reservoir_Name'].nunique(),
                "total_basins": df['Basin'].nunique(),
                "total_records": len(df)
            }
        
        with st.spinner("Loading quick stats..."):
            stats = get_quick_stats()
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        metric_col1.metric(
            label="Reservoirs Monitored",
            value=f"{stats['total_reservoirs']}",
            delta="Active"
        )
        
        metric_col2.metric(
            label="River Basins",
            value=f"{stats['total_basins']}",
            delta="Regions"
        )
        
        metric_col3.metric(
            label="Data Points",
            value=f"{stats['total_records']:,}",
            delta="Records"
        )
    
    except Exception as e:
        st.error(f"⚠️ Could not load statistics: {str(e)}")

    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: #64748b;'>
        <p>Built with ❤️ using Streamlit, Pandas, and Plotly</p>
        <p>© 2024 AquaSense AI - All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        st.info("Please try reloading the page or contact support.")
